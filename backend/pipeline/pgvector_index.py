
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import execute_batch
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS, VECTOR_DIM
from models.neo4j_client import get_chunks_for_doc
from llm.embeddings import embed_text

def _get_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASS,
    )

def _ensure_schema(conn):
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS rag_chunks (
            id BIGSERIAL PRIMARY KEY,
            doc_id TEXT NOT NULL,
            pin TEXT,
            source TEXT NOT NULL,
            page_number INT,
            node_id TEXT,
            text TEXT NOT NULL,
            embedding vector({VECTOR_DIM}) NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS rag_chunks_embedding_cosine_idx
        ON rag_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
    )
    cur.execute("ANALYZE rag_chunks;")
    conn.commit()
    cur.close()

def index_doc_in_pgvector(doc_id: str) -> None:
    conn = _get_conn()
    _ensure_schema(conn)
    chunks = get_chunks_for_doc(doc_id)
    if not chunks:
        conn.close()
        return

    records = []
    for c in chunks:
        text = c["text"]
        if not text:
            continue
        emb = embed_text(text)
        # Convert numpy array to list for string formatting
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        emb_literal = "[" + ",".join(str(x) for x in emb) + "]"
        records.append(
            (
                c.get("doc_id", doc_id),
                c.get("pin"),
                c.get("source", "Unknown"),
                c.get("page_number"),
                c.get("node_id"),
                text,
                emb_literal,
            )
        )

    cur = conn.cursor()
    execute_batch(
        cur,
        """
        INSERT INTO rag_chunks (doc_id, pin, source, page_number, node_id, text, embedding)
        VALUES (%s,%s,%s,%s,%s,%s,%s::vector)
        """,
        records,
    )
    conn.commit()
    cur.close()
    conn.close()
