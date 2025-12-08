
from typing import List, Dict, Any
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS

def _driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def list_all_docs() -> List[str]:
    driver = _driver()
    with driver.session() as session:
        result = session.run("MATCH (d:Document) RETURN d.doc_id AS doc_id ORDER BY d.doc_id")
        docs = [r["doc_id"] for r in result]
    driver.close()
    return docs

def get_graph_for_doc(doc_id: str) -> Dict[str, Any]:
    """
    Return a lightweight graph suitable for force-directed visualisation:
      { "nodes": [{id, label, group}], "links": [{source, target, type}] }
    """
    driver = _driver()
    nodes = {}
    links = []
    with driver.session() as session:
        q = """
        MATCH (d:Document {doc_id:$doc_id})-[:HAS_PAGE]->(p:Page)
        OPTIONAL MATCH (p)-[rp]->(c)
        RETURN d, p, rp, c
        """
        for r in session.run(q, doc_id=doc_id):
            d = r["d"]
            p = r["p"]
            rel = r["rp"]
            c = r["c"]

            doc_key = d.id
            if doc_key not in nodes:
                nodes[doc_key] = {"id": doc_key, "label": d["doc_id"], "group": "Document"}

            page_key = p.id
            if page_key not in nodes:
                nodes[page_key] = {"id": page_key, "label": f"Page {p['page_number']}", "group": "Page"}

            links.append({"source": doc_key, "target": page_key, "type": "HAS_PAGE"})

            if c is not None and rel is not None:
                child_key = c.id
                label = c.get("figure_id") or c.get("id") or "node"
                group = list(c.labels)[0] if c.labels else "Node"
                if child_key not in nodes:
                    nodes[child_key] = {"id": child_key, "label": label, "group": group}
                links.append({"source": page_key, "target": child_key, "type": rel.type})

    driver.close()
    return {"nodes": list(nodes.values()), "links": links}

def get_chunks_for_doc(doc_id: str) -> List[Dict[str, Any]]:
    """
    Return chunks for pgvector indexing.
    Each chunk: {doc_id, source, page_number, node_id, text, pin}
    """
    driver = _driver()
    chunks: List[Dict[str, Any]] = []
    with driver.session() as session:
        # TextBlocks
        q_tb = """
        MATCH (d:Document {doc_id:$doc_id})-[:HAS_PAGE]->(p:Page)-[:HAS_TEXT_BLOCK]->(t:TextBlock)
        RETURN p.page_number AS page, t.id AS node_id, t.summary AS text
        """
        for r in session.run(q_tb, doc_id=doc_id):
            chunks.append(
                {
                    "doc_id": doc_id,
                    "pin": None,
                    "source": "TextBlock",
                    "page_number": r["page"],
                    "node_id": r["node_id"],
                    "text": r["text"],
                }
            )

        # Figures
        q_fig = """
        MATCH (d:Document {doc_id:$doc_id})-[:HAS_PAGE]->(p:Page)-[:HAS_FIGURE]->(f:Figure)
        RETURN p.page_number AS page, f.figure_id AS node_id, f.title AS text, f.path AS path
        """
        for r in session.run(q_fig, doc_id=doc_id):
            chunks.append(
                {
                    "doc_id": doc_id,
                    "pin": None,
                    "source": "Figure",
                    "page_number": r["page"],
                    "node_id": r["node_id"],
                    "text": r["text"],
                    "image_path": r["path"],
                }
            )
    driver.close()
    return chunks

def search_context_for_question(question: str) -> List[Dict[str, Any]]:
    """
    Very simple heuristic: fetch all TextBlocks, Figures, and Tables from all docs as base context.
    In a production system you'd use more selective logic and ontology.
    """
    driver = _driver()
    chunks: List[Dict[str, Any]] = []
    with driver.session() as session:
        q = """
        MATCH (d:Document)-[:HAS_PAGE]->(p:Page)
        OPTIONAL MATCH (p)-[:HAS_TEXT_BLOCK]->(t:TextBlock)
        OPTIONAL MATCH (p)-[:HAS_FIGURE]->(f:Figure)
        OPTIONAL MATCH (p)-[:HAS_TABLE]->(tbl:Table)
        RETURN d.doc_id AS doc_id, p.page_number AS page,
               t.id AS tb_id, t.summary AS tb_text,
               f.figure_id AS fig_id, f.title AS fig_title, f.path AS fig_path,
               tbl.table_id AS tbl_id, tbl.data AS tbl_data, tbl.title AS tbl_title
        """
        for r in session.run(q):
            doc_id = r["doc_id"]
            page = r["page"]
            if r["tb_id"] and r["tb_text"]:
                chunks.append(
                    {
                        "doc_id": doc_id,
                        "source": "TextBlock",
                        "page": page,
                        "pin": None,
                        "node_id": r["tb_id"],
                        "text": r["tb_text"],
                        "image_path": None,
                    }
                )
            if r["fig_id"] and (r["fig_title"] or r["fig_path"]):
                chunks.append(
                    {
                        "doc_id": doc_id,
                        "source": "Figure",
                        "page": page,
                        "pin": None,
                        "node_id": r["fig_id"],
                        "text": r["fig_title"] or "",
                        "image_path": r["fig_path"],
                    }
                )
            if r["tbl_id"] and r["tbl_data"]:
                # Parse table data if it's stored as JSON string
                import json
                table_data = r["tbl_data"]
                if isinstance(table_data, str):
                    try:
                        table_data = json.loads(table_data)
                    except:
                        table_data = []
                
                chunks.append(
                    {
                        "doc_id": doc_id,
                        "source": "Table",
                        "page": page,
                        "pin": None,
                        "node_id": r["tbl_id"],
                        "text": r["tbl_title"] or "",
                        "table_data": table_data,
                    }
                )
    driver.close()
    return chunks
