# rag_retrieval.py

from typing import List, Dict, Any
from neo4j import GraphDatabase

# Plug in your own embedding client here
def embed_text_batch(texts: List[str]) -> List[List[float]]:
    """
    Return vector embeddings for a list of texts.
    Replace this stub with your embedding API (OpenAI, Azure, etc.).
    """
    raise NotImplementedError("Implement embed_text_batch() with your embedding client.")


class Neo4jRAGRetriever:
    def __init__(self, uri: str, user: str, password: str, doc_id: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.doc_id = doc_id

    def close(self):
        self.driver.close()

    def get_context_for_pin(self, pin_name: str) -> Dict[str, List[str]]:
        """
        Symbolic retrieval:
        Return summaries/contexts for a specific pin:
          - TextBlocks
          - Figures
          - Tables
          - Constraints descriptions
        """
        with self.driver.session() as session:
            # TextBlocks, Figures, Tables
            records = session.run(
                """
                MATCH (ic:IC {doc_id: $doc_id})-[:HAS_PIN]->(p:Pin {name: $pin_name})
                OPTIONAL MATCH (p)-[:MENTIONED_IN]->(tb:TextBlock)
                OPTIONAL MATCH (p)-[:MENTIONED_IN]->(f:Figure)
                OPTIONAL MATCH (p)-[:MENTIONED_IN]->(t:Table)
                OPTIONAL MATCH (p)-[:HAS_CONSTRAINT]->(c:Constraint)
                RETURN
                    collect(DISTINCT tb.summary) AS text_blocks,
                    collect(DISTINCT f.natural_language_context) AS figures,
                    collect(DISTINCT t.natural_language_context) AS tables,
                    collect(DISTINCT c.description) AS constraints
                """,
                doc_id=self.doc_id,
                pin_name=pin_name,
            )
            rec = records.single() or {}
            return {
                "text_blocks": [x for x in (rec.get("text_blocks") or []) if x],
                "figure_contexts": [x for x in (rec.get("figures") or []) if x],
                "table_contexts": [x for x in (rec.get("tables") or []) if x],
                "constraints": [x for x in (rec.get("constraints") or []) if x],
            }

    def build_candidate_chunks(self, pin_name: str) -> List[Dict[str, Any]]:
        """
        Flatten the contexts into chunks, each with a 'text' field.
        """
        ctx = self.get_context_for_pin(pin_name)
        chunks: List[Dict[str, Any]] = []

        for t in ctx["text_blocks"]:
            chunks.append({"source": "TextBlock", "pin": pin_name, "text": t})
        for f in ctx["figure_contexts"]:
            chunks.append({"source": "Figure", "pin": pin_name, "text": f})
        for t in ctx["table_contexts"]:
            chunks.append({"source": "Table", "pin": pin_name, "text": t})
        for c in ctx["constraints"]:
            chunks.append({"source": "Constraint", "pin": pin_name, "text": c})

        return chunks

    def rank_chunks_for_query(self, query: str, pin_name: str, top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Combine symbolic retrieval with embedding-based rerank.
        """
        chunks = self.build_candidate_chunks(pin_name)
        if not chunks:
            return []

        texts = [c["text"] for c in chunks]
        query_vec = embed_text_batch([query])[0]
        chunk_vecs = embed_text_batch(texts)

        # Simple cosine similarity
        import numpy as np

        def cos_sim(a, b):
            a = np.array(a)
            b = np.array(b)
            return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

        scores = [cos_sim(query_vec, v) for v in chunk_vecs]
        scored = [
            {**c, "score": s}
            for c, s in zip(chunks, scores)
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
