# index_chunks_pgvector.py

import argparse
from typing import List, Dict, Any

from neo4j import GraphDatabase

from pgvector_store import PgVectorStore


def fetch_chunks_from_neo4j(
    uri: str,
    user: str,
    password: str,
    doc_id: str,
) -> List[Dict[str, Any]]:
    """
    Fetch candidate chunks from Neo4j for this document.
    One chunk per TextBlock/Figure/Table/Constraint + Pin links.
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))
    chunks: List[Dict[str, Any]] = []

    with driver.session() as session:
        # TextBlocks
        records = session.run(
            """
            MATCH (d:Document {doc_id: $doc_id})-[:HAS_PAGE]->(p:Page)-[:HAS_TEXT_BLOCK]->(tb:TextBlock)
            OPTIONAL MATCH (ic:IC {doc_id: $doc_id})-[:HAS_PIN]->(pin)-[:MENTIONED_IN]->(tb)
            RETURN p.page_number AS page,
                   tb.id AS node_id,
                   tb.summary AS text,
                   collect(DISTINCT pin.name) AS pins
            """,
            doc_id=doc_id,
        )
        for r in records:
            text = r["text"]
            if not text:
                continue
            pins = r["pins"] or []
            if pins:
                for pin in pins:
                    chunks.append(
                        {
                            "pin": pin,
                            "source": "TextBlock",
                            "page_number": r["page"],
                            "node_id": r["node_id"],
                            "text": text,
                        }
                    )
            else:
                chunks.append(
                    {
                        "pin": None,
                        "source": "TextBlock",
                        "page_number": r["page"],
                        "node_id": r["node_id"],
                        "text": text,
                    }
                )

        # Figures
        records = session.run(
            """
            MATCH (d:Document {doc_id: $doc_id})-[:HAS_PAGE]->(p:Page)-[:HAS_FIGURE]->(f:Figure)
            OPTIONAL MATCH (ic:IC {doc_id: $doc_id})-[:HAS_PIN]->(pin)-[:MENTIONED_IN]->(f)
            RETURN p.page_number AS page,
                   f.figure_id AS node_id,
                   f.natural_language_context AS text,
                   collect(DISTINCT pin.name) AS pins
            """,
            doc_id=doc_id,
        )
        for r in records:
            text = r["text"]
            if not text:
                continue
            pins = r["pins"] or []
            if pins:
                for pin in pins:
                    chunks.append(
                        {
                            "pin": pin,
                            "source": "Figure",
                            "page_number": r["page"],
                            "node_id": r["node_id"],
                            "text": text,
                        }
                    )
            else:
                chunks.append(
                    {
                        "pin": None,
                        "source": "Figure",
                        "page_number": r["page"],
                        "node_id": r["node_id"],
                        "text": text,
                    }
                )

        # Tables
        records = session.run(
            """
            MATCH (d:Document {doc_id: $doc_id})-[:HAS_PAGE]->(p:Page)-[:HAS_TABLE]->(t:Table)
            OPTIONAL MATCH (ic:IC {doc_id: $doc_id})-[:HAS_PIN]->(pin)-[:MENTIONED_IN]->(t)
            RETURN p.page_number AS page,
                   t.table_id AS node_id,
                   t.natural_language_context AS text,
                   collect(DISTINCT pin.name) AS pins
            """,
            doc_id=doc_id,
        )
        for r in records:
            text = r["text"]
            if not text:
                continue
            pins = r["pins"] or []
            if pins:
                for pin in pins:
                    chunks.append(
                        {
                            "pin": pin,
                            "source": "Table",
                            "page_number": r["page"],
                            "node_id": r["node_id"],
                            "text": text,
                        }
                    )
            else:
                chunks.append(
                    {
                        "pin": None,
                        "source": "Table",
                        "page_number": r["page"],
                        "node_id": r["node_id"],
                        "text": text,
                    }
                )

        # Constraints
        records = session.run(
            """
            MATCH (ic:IC {doc_id: $doc_id})-[:HAS_PIN]->(pin)-[:HAS_CONSTRAINT]->(c:Constraint)
            RETURN pin.name AS pin,
                   c.id AS node_id,
                   c.description AS text
            """,
            doc_id=doc_id,
        )
        for r in records:
            text = r["text"]
            if not text:
                continue
            chunks.append(
                {
                    "pin": r["pin"],
                    "source": "Constraint",
                    "page_number": None,
                    "node_id": r["node_id"],
                    "text": text,
                }
            )

    driver.close()
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--neo4j_uri", required=True)
    parser.add_argument("--neo4j_user", required=True)
    parser.add_argument("--neo4j_password", required=True)
    parser.add_argument("--pg_dsn", help="Postgres DSN", required=False)
    parser.add_argument("--pg_host", default="localhost")
    parser.add_argument("--pg_port", type=int, default=5432)
    parser.add_argument("--pg_dbname", default="rag_db")
    parser.add_argument("--pg_user", default="postgres")
    parser.add_argument("--pg_password", default="postgres")
    parser.add_argument("--doc_id", required=True)

    args = parser.parse_args()

    # 1. Fetch chunks from Neo4j
    print(f"[INFO] Fetching chunks from Neo4j for doc_id={args.doc_id}")
    chunks = fetch_chunks_from_neo4j(
        uri=args.neo4j_uri,
        user=args.neo4j_user,
        password=args.neo4j_password,
        doc_id=args.doc_id,
    )
    print(f"[INFO] Retrieved {len(chunks)} chunks")

    # 2. Insert into pgvector
    store = PgVectorStore(
        dsn=args.pg_dsn,
        host=args.pg_host,
        port=args.pg_port,
        dbname=args.pg_dbname,
        user=args.pg_user,
        password=args.pg_password,
    )
    try:
        store.create_schema()
        print("[INFO] Indexing chunks into pgvector ...")
        store.upsert_chunks(args.doc_id, chunks)
        print("[OK] Done")
    finally:
        store.close()


if __name__ == "__main__":
    main()
