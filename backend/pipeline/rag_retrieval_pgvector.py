# rag_retrieval_pgvector.py

from typing import List, Dict, Any

from pgvector_store import PgVectorStore


class RAGRetrieverPgVector:
    """
    High-level helper:
      - search similar chunks for a query
      - optionally constrained by doc_id and/or pin
    """
    def __init__(
        self,
        pg_store: PgVectorStore,
        doc_id: str,
    ) -> None:
        self.store = pg_store
        self.doc_id = doc_id

    def retrieve(
        self,
        query: str,
        pin: str | None = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of chunks:
        {
          "id": ...,
          "doc_id": ...,
          "pin": ...,
          "source": ...,
          "page_number": ...,
          "node_id": ...,
          "text": ...,
          "distance": ...
        }
        """
        return self.store.search(
            query=query,
            doc_id=self.doc_id,
            pin=pin,
            top_k=top_k,
        )
