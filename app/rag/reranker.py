import logging
from typing import List, Optional
from app.rag.retriever import RetrievedChunk

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Reranks retrieved document chunks using a deep cross-encoder model.
    Bi-encoders (embedding search) find candidate chunks quickly;
    Cross-encoders score full (query, document) pairs together for high precision.

    Resilience Guarantee (PRD Section 5):
    If the cross-encoder model fails to load or download, it falls back
    to returning the initial retriever results without breaking the request.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None
        self._load_failed = False

    def _get_model(self):
        if self._model is None and not self._load_failed:
            try:
                from sentence_transformers import CrossEncoder
                logger.info(f"Loading CrossEncoder reranker model: {self.model_name}...")
                self._model = CrossEncoder(self.model_name)
            except Exception as e:
                logger.warning(f"Failed to load CrossEncoder model ({e}). Gracefully falling back to raw retrieval.")
                self._load_failed = True
        return self._model

    def rerank(self, query: str, chunks: List[RetrievedChunk], top_n: int = 3) -> List[RetrievedChunk]:
        if not chunks:
            return []

        if len(chunks) <= 1:
            return chunks[:top_n]

        model = self._get_model()
        if model is None:
            # Graceful degradation fallback
            return chunks[:top_n]

        try:
            # Build query-document pairs
            pairs = [[query, chunk.text] for chunk in chunks]
            scores = model.predict(pairs)

            # Assign new cross-encoder scores
            for chunk, score in zip(chunks, scores):
                chunk.score = round(float(score), 4)

            # Sort descending by cross-encoder score
            reranked = sorted(chunks, key=lambda x: x.score, reverse=True)
            return reranked[:top_n]

        except Exception as e:
            logger.error(f"Error during reranking inference: {e}. Falling back to initial ranking.", exc_info=True)
            return chunks[:top_n]
