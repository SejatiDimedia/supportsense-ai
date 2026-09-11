import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from app.rag.embedder import VectorStoreManager, OllamaEmbedder

logger = logging.getLogger(__name__)

@dataclass
class RetrievedChunk:
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float
    score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RAGRetriever:
    """
    Handles semantic retrieval from Chroma vector database.
    Adheres to resilience principles: never raises unhandled exceptions on search failure,
    gracefully returns an empty list if Chroma is unreachable or empty.
    """
    def __init__(self, vector_store: Optional[VectorStoreManager] = None, default_top_k: int = 5):
        self.vector_store = vector_store or VectorStoreManager()
        self.default_top_k = default_top_k

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievedChunk]:
        k = top_k or self.default_top_k
        if not query or not query.strip():
            return []

        try:
            collection = self.vector_store.get_or_create_collection()
            if collection.count() == 0:
                logger.warning("Vector store collection is empty. Returning empty retrieval.")
                return []

            query_embedding = self.vector_store.embedder.get_embedding(query.strip())

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, collection.count()),
                include=["documents", "metadatas", "distances"]
            )

            retrieved_chunks: List[RetrievedChunk] = []

            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for doc_id, doc_text, meta, dist in zip(ids, docs, metadatas, distances):
                # Normalized similarity score from distance
                # Chroma uses L2 squared or cosine distance by default; score in [0, 1]
                score = round(1.0 / (1.0 + float(dist)), 4)
                retrieved_chunks.append(
                    RetrievedChunk(
                        id=doc_id,
                        text=doc_text,
                        metadata=meta,
                        distance=round(float(dist), 4),
                        score=score
                    )
                )

            # Sort descending by score
            retrieved_chunks.sort(key=lambda x: x.score, reverse=True)
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error during semantic retrieval: {e}", exc_info=True)
            return []

    async def aretrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievedChunk]:
        # Async-friendly wrapper for FastAPI routes
        return self.retrieve(query, top_k=top_k)
