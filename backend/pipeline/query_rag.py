
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import DictCursor
from pathlib import Path
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS, STATIC_DIR, UPLOAD_DIR
from models.neo4j_client import search_context_for_question
from llm.prompt_generator import build_prompt
from llm.answer_llm import answer_llm

def _resolve_image_path(doc_id: str, image_path: str) -> str:
    """
    Resolve the actual image path from various possible storage locations.
    Handles both:
    - backend/uploads/{doc_id}/assets/images/{filename}
    - backend/static/{doc_id_with_suffix}/images/{filename}
    
    Returns the path relative to the static directory for URL generation.
    """
    if not image_path:
        return None
    
    # Extract just the filename from the path
    filename = Path(image_path).name
    
    # Try to find the image in static directory
    # Pattern 1: static/{doc_id}/images/{filename}
    static_path_1 = STATIC_DIR / doc_id / "images" / filename
    if static_path_1.exists():
        return f"{doc_id}/images/{filename}"
    
    # Pattern 2: static/{doc_id_with_suffix}/images/{filename_with_suffix}
    # Look for directories that start with the doc_id
    if STATIC_DIR.exists():
        for subdir in STATIC_DIR.iterdir():
            if subdir.is_dir() and subdir.name.startswith(doc_id):
                # Check if image exists in this directory
                img_dir = subdir / "images"
                if img_dir.exists():
                    # Try exact filename first
                    img_path = img_dir / filename
                    if img_path.exists():
                        return f"{subdir.name}/images/{filename}"
                    
                    # Try filename with doc_id prefix
                    prefixed_filename = f"{subdir.name}_{filename.split('_', 1)[-1] if '_' in filename else filename}"
                    img_path_prefixed = img_dir / prefixed_filename
                    if img_path_prefixed.exists():
                        return f"{subdir.name}/images/{prefixed_filename}"
    
    # Pattern 3: uploads/{doc_id}/assets/images/{filename}
    upload_path = UPLOAD_DIR / doc_id / "assets" / "images" / filename
    if upload_path.exists():
        # Copy to static directory for serving
        target_dir = STATIC_DIR / doc_id / "images"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename
        if not target_file.exists():
            import shutil
            shutil.copy2(upload_path, target_file)
        return f"{doc_id}/images/{filename}"
    
    # If all else fails, return the original path structure
    # This will at least show what was expected
    return image_path.replace("backend\\uploads\\", "").replace("backend/uploads/", "").replace("\\", "/")

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
    Fallback: if pgvector not yet populated, returns empty list.
    """
    conn = _pg_conn()
    cur = conn.cursor(cursor_factory=DictCursor)
    try:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'rag_chunks'
            );
            """
        )
        exists = cur.fetchone()[0]
        if not exists:
            conn.close()
            return []

        from llm.embeddings import embed_text
        q_emb = embed_text(question)
        emb_literal = "[" + ",".join(str(x) for x in q_emb) + "]"

        cur.execute(
            """
            SELECT
                doc_id, pin, source, page_number, node_id, text, embedding <=> %s::vector AS distance
            FROM rag_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (emb_literal, emb_literal, top_k),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            dict(
                doc_id=r["doc_id"],
                pin=r["pin"],
                source=r["source"],
                page=r["page_number"],
                node_id=r["node_id"],
                text=r["text"],
                distance=float(r["distance"]),
                image_path=None,
            )
            for r in rows
        ]
    except Exception:
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
    base_context = search_context_for_question(question)
    vector_context = _search_pgvector(question, top_k=10)

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

    answer_prompt = build_prompt(
        user_question=question,
        context_chunks=context_chunks,
        constraints=constraints,
        ontology_hints=ontology_hints,
    )
    answer_text = answer_llm(answer_prompt)

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
    }
