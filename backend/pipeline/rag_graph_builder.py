
from typing import Dict, Any
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS

def ingest_raw_into_graph(raw_json: Dict[str, Any]) -> None:
    """
    Simplified ingestion:
      - Document
      - Pages
      - TextBlocks (one per page)
      - Figures (images)
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    doc_id = raw_json["doc_id"]

    with driver.session() as session:
        session.run(
            "MERGE (d:Document {doc_id:$doc_id}) "
            "SET d.source_file=$source_file, d.num_pages=$num_pages",
            doc_id=doc_id,
            source_file=raw_json.get("source_file"),
            num_pages=raw_json.get("num_pages"),
        )

        for page in raw_json["pages"]:
            page_number = page["page_number"]
            raw_text = page.get("raw_text", "")

            session.run(
                """
                MATCH (d:Document {doc_id:$doc_id})
                MERGE (p:Page {doc_id:$doc_id, page_number:$page_number})
                SET p.raw_text=$raw_text
                MERGE (d)-[:HAS_PAGE]->(p)
                """,
                doc_id=doc_id,
                page_number=page_number,
                raw_text=raw_text,
            )

            # text block (one per page)
            tb_id = f"{doc_id}_p{page_number}_tb1"
            session.run(
                """
                MATCH (p:Page {doc_id:$doc_id, page_number:$page_number})
                MERGE (t:TextBlock {id:$tb_id})
                SET t.summary=$summary
                MERGE (p)-[:HAS_TEXT_BLOCK]->(t)
                """,
                doc_id=doc_id,
                page_number=page_number,
                tb_id=tb_id,
                summary=raw_text[:500],
            )

            # figures
            for img in page.get("images", []):
                fig_id = img["image_id"]
                title = img.get("title") or "Figure"
                path = img.get("path")
                session.run(
                    """
                    MATCH (p:Page {doc_id:$doc_id, page_number:$page_number})
                    MERGE (f:Figure {figure_id:$figure_id})
                    SET f.title=$title,
                        f.path=$path,
                        f.page_number=$page_number,
                        f.doc_id=$doc_id
                    MERGE (p)-[:HAS_FIGURE]->(f)
                    """,
                    doc_id=doc_id,
                    page_number=page_number,
                    figure_id=fig_id,
                    title=title,
                    path=path,
                )
    driver.close()
