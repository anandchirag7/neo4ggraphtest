import sys
import os
import json
from pathlib import Path

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.pipeline.build_rag_graph import Neo4jRAGIngestor
import backend.config as config

def reingest_7m():
    # Adjusted path relative to this script location (backend/pipeline/reingest_7m.py)
    raw_path = Path(__file__).parent / "enriched_7m.json"
    if not raw_path.exists():
        print(f"File not found: {raw_path}")
        return

    print(f"Loading {raw_path}...")
    with raw_path.open("r", encoding="utf-8") as f:
        enriched = json.load(f)

    # Ingest
    print(f"Connecting to {config.NEO4J_URI}...")
    ingestor = Neo4jRAGIngestor(config.NEO4J_URI, config.NEO4J_USER, config.NEO4J_PASS)
    try:
        # Optional: Delete old 7m nodes directly if needed (Cypher), 
        # but ingest_enriched might just MERGE/update.
        # Let's trust MERGE for now or we can run a specific delete query.
        print("Clearing old 7m nodes...")
        with ingestor.driver.session() as session:
            session.run("MATCH (d:Document {doc_id: '7m'}) DETACH DELETE d")
            # Pages are linked to Document, so if we delete Document we might orphan pages if not detached
            # Better:
            session.run("MATCH (d:Document {doc_id: '7m'})-[*]->(n) DETACH DELETE d, n")
            # Also delete pages directly attached to 7m just in case
            session.run("MATCH (p:Page {doc_id: '7m'}) DETACH DELETE p")
            
        print("Ingesting fresh data...")
        ingestor.ingest_enriched_json(enriched)
        print("Done.")
    finally:
        ingestor.close()

if __name__ == "__main__":
    reingest_7m()
