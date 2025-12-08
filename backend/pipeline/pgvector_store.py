# pgvector_store.py

import os
from typing import List, Dict, Any, Optional, Tuple

import psycopg2
import psycopg2.extras


# ---------- EMBEDDING HOOK (you plug your API here) ----------

import sys
import os

# Add parent directory to sys.path to allow importing 'llm'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.embeddings import embed_text

def get_embedding(text: str) -> List[float]:
    """
    Call your embedding model and return a 1024-dim vector.
    """
    return embed_text(text).tolist()


# ---------- PGVECTOR STORE CLASS ----------

class PgVectorStore:
    def __init__(
        self,
        dsn: Optional[str] = None,
        host: str = "localhost",
        port: int = 5432,
        dbname: str = "rag_db",
        user: str = "postgres",
        password: str = "postgres",
    ) -> None:
        """
        You can either pass a DSN string, or host/port/dbname/user/password.
        """
        if dsn is None:
            dsn = f"host={host} port={port} dbname={dbname} user={user} password={password}"
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True

    def close(self) -> None:
        self.conn.close()

    def create_schema(self) -> None:
        """
        Create the rag_chunks table and index if they don't exist.
        """
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id          BIGSERIAL PRIMARY KEY,
                    doc_id      TEXT NOT NULL,
                    pin         TEXT,
                    source      TEXT NOT NULL,
                    page_number INT,
                    node_id     TEXT,
                    text        TEXT NOT NULL,
                    embedding   vector(1024) NOT NULL
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

    def upsert_chunks(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]],
        recompute_embeddings: bool = False,
    ) -> None:
        """
        Insert chunks into rag_chunks.

        Each chunk dict should contain:
          - "pin"        (optional)
          - "source"     ("TextBlock"|"Figure"|"Table"|"Constraint")
          - "page_number" (optional)
          - "node_id"    (optional: Neo4j node ID or composite key)
          - "text"       (the text to embed)
        """
        with self.conn.cursor() as cur:
            for c in chunks:
                text = c["text"]
                if not text:
                    continue

                # You might have a more sophisticated "idempotency" strategy
                # (e.g., a hash of doc_id + node_id + text) to avoid duplicates.
                # For simplicity, we always insert here.

                # Get vector embedding
                emb = c.get("embedding")
                if emb is None or recompute_embeddings:
                    emb = get_embedding(text)

                # Convert Python list[float] to pgvector literal: '[1,2,3,...]'
                emb_literal = "[" + ",".join(str(x) for x in emb) + "]"

                cur.execute(
                    """
                    INSERT INTO rag_chunks (doc_id, pin, source, page_number, node_id, text, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
                    """,
                    (
                        doc_id,
                        c.get("pin"),
                        c.get("source", "Unknown"),
                        c.get("page_number"),
                        c.get("node_id"),
                        text,
                        emb_literal,
                    ),
                )

    def search(
        self,
        query: str,
        doc_id: Optional[str] = None,
        pin: Optional[str] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for top_k most similar chunks to the query using cosine distance.
        Optionally filter by doc_id and/or pin.
        """
        q_emb = get_embedding(query)
        q_emb_literal = "[" + ",".join(str(x) for x in q_emb) + "]"

        where_clauses = []
        params: List[Any] = [q_emb_literal]

        if doc_id is not None:
            where_clauses.append("doc_id = %s")
            params.append(doc_id)
        if pin is not None:
            where_clauses.append("pin = %s")
            params.append(pin)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        sql = f"""
            SELECT
                id,
                doc_id,
                pin,
                source,
                page_number,
                node_id,
                text,
                embedding <=> %s::vector AS distance
            FROM rag_chunks
            {where_sql}
            ORDER BY embedding <=> %s::vector
            LIMIT {top_k};
        """

        # Notice we pass q_emb_literal twice: once for SELECT and once for ORDER BY
        params.append(q_emb_literal)

        rows: List[Dict[str, Any]] = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, params)
            for r in cur.fetchall():
                rows.append(
                    {
                        "id": r["id"],
                        "doc_id": r["doc_id"],
                        "pin": r["pin"],
                        "source": r["source"],
                        "page_number": r["page_number"],
                        "node_id": r["node_id"],
                        "text": r["text"],
                        "distance": float(r["distance"]),
                    }
                )
        return rows
