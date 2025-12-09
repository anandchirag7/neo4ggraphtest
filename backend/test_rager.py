
from typing import Dict, Any, List
import json
import psycopg2
from psycopg2.extras import DictCursor
from pathlib import Path
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS, STATIC_DIR, UPLOAD_DIR
from models.neo4j_client import search_context_for_question
from llm.prompt_generator import build_prompt
from llm.answer_llm import answer_llm


def _pg_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASS,
    )

def _search_pgvector(question: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Hybrid search: Cosine (<=>) and Euclidean (<->).
    1. Get Top 10 Cosine.
    2. Get Top 10 Euclidean.
    3. Take Top 2 from each.
    4. Combine/Dedupe -> Take Top 2.
    5. Write to rag_chunks.json.
    """
    conn = _pg_conn()
    cur = conn.cursor(cursor_factory=DictCursor)
    try:
        from llm.embeddings import embed_text
        q_emb = embed_text(question)
        emb_literal = "[" + ",".join(str(x) for x in q_emb) + "]"

        def run_query(operator, limit):
            cur.execute(
                f"""
                SELECT
                    doc_id, pin, source, page_number, node_id, text, embedding {operator} %s::vector AS distance
                FROM rag_chunks
                ORDER BY distance ASC
                LIMIT %s;
                """,
                (emb_literal, limit),
            )
            return [dict(r) for r in cur.fetchall()]

        # 1. Top 10 Cosine
        cosine_10 = run_query("<=>", 10)
        
        # 2. Top 10 Euclidean
        euclidean_10 = run_query("<->", 10)

        # "Store all the 20 chunks"
        # We will NOT deduplicate, because we want to see the distance variance for the same chunk across metrics.
        all_results = cosine_10 + euclidean_10

        # Write to JSON
        with open("rag_chunks.json", "w") as f:
            for r in all_results:
                record = {
                    "distance": float(r["distance"]), # First column
                    "doc_id": r["doc_id"],
                    "pin": r["pin"],
                    "source": r["source"],
                    "page_number": r["page_number"],
                    "node_id": r["node_id"],
                    "text": r["text"]
                }
                f.write(json.dumps(record) + "\n")
        
        conn.close()
        return all_results

    except Exception as e:
        print(f"Error in vector search: {e}")
        conn.close()
        return []

def rag_answer(question: str) -> Dict[str, Any]:
    """
    End-to-end:
      1) Get base context from Neo4j
      2) Optionally refine/rerank with pgvector (if available)
      3) Build prompt with meta-prompt
      4) Call answer LLM
      5) Return text + figures + tables
    """
    # Smart Context Filtering
    # Simple Entity Extraction for Proof-of-Concept
    doc_filter = None
    q_lower = question.lower()
    
    # Map keywords to doc_ids (in production this would be a lookup or LLM call)
    if "7m" in q_lower:
        doc_filter = ["7m"]
    elif "isl81401" in q_lower:
        doc_filter = ["7m"] # Assuming ISL81401 is covered by 7m doc
        
    print(f"DEBUG: Smart Context Filter: {doc_filter}")

    base_context = search_context_for_question(question, doc_ids=doc_filter)
    
    # Note: _search_pgvector doesn't support metadata filtering yet in this impl, 
    # but base_context (Graph) is usually the source of structured tables/figures.
    vector_context = _search_pgvector(question, top_k=15)
    
    # merge (simple: union, prioritising vector hits if present)
    context_map = {}
    for c in base_context + vector_context:
        key = (c["doc_id"], c["source"], c["node_id"])
        if key not in context_map:
            context_map[key] = c
    context_chunks = list(context_map.values())

    # no explicit constraints yet; you can later populate from ontology layer
    constraints: List[Dict[str, Any]] = []
    ontology_hints: Dict[str, Any] = {"intent": "generic_rag"}

    top_k = 15 # Updated
    
    # 3. Build Prompt
    print(f"DEBUG: Using Deterministic CoT Prompting. Context chunks: {len(context_chunks)}")
    qs = build_prompt(
        user_question=question,
        context_chunks=context_chunks,
        constraints=constraints,
        ontology_hints=ontology_hints
    )
    answer_text = answer_llm(qs) # Changed from answer_prompt to qs

    figures = []
    for c in context_chunks:
        if c.get("image_path") and c.get("source") == "Figure":
            # Resolve the actual image path
            resolved_path = _resolve_image_path(c["doc_id"], c["image_path"])
            if resolved_path:
                figures.append({
                    "doc_id": c["doc_id"],
                    "node_id": c["node_id"],
                    "page": c.get("page"),
                    "image_url": f"/static/{resolved_path}",
                    "caption": (c.get("text") or "")[:120],
                })

    tables = [
        {
            "doc_id": c["doc_id"],
            "node_id": c["node_id"],
            "page": c.get("page"),
            "table_data": c.get("table_data", []),
            "caption": (c.get("text") or "")[:120],
        }
        for c in context_chunks
        if c.get("table_data") and c.get("source") == "Table"
    ]

    docs = sorted({c["doc_id"] for c in context_chunks})

    return {
        "answer_text": answer_text,
        "figures": figures,
        "tables": tables,
        "documents": docs,
        "contexts": [c.get("text", "") for c in context_chunks] # Added for Ragas evaluation
    }


_search_pgvector(question = "give me ordering info for 7m?")