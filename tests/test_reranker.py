import pytest
from unittest.mock import MagicMock
from app.rag.retriever import RetrievedChunk
from app.rag.reranker import CrossEncoderReranker

def test_reranker_empty():
    reranker = CrossEncoderReranker()
    assert reranker.rerank("query", []) == []

def test_reranker_fallback_on_model_failure():
    reranker = CrossEncoderReranker()
    reranker._load_failed = True # Simulate model unavailable

    chunk1 = RetrievedChunk(id="c1", text="text1", metadata={}, distance=0.1, score=0.9)
    chunk2 = RetrievedChunk(id="c2", text="text2", metadata={}, distance=0.2, score=0.8)

    results = reranker.rerank("query", [chunk1, chunk2], top_n=1)
    assert len(results) == 1
    assert results[0].id == "c1"

def test_reranker_sorting_logic():
    reranker = CrossEncoderReranker()
    mock_model = MagicMock()
    # Chunk 2 gets higher score from cross-encoder
    mock_model.predict.return_value = [1.2, 5.8]
    reranker._model = mock_model

    chunk1 = RetrievedChunk(id="c1", text="text1", metadata={}, distance=0.1, score=0.9)
    chunk2 = RetrievedChunk(id="c2", text="text2", metadata={}, distance=0.2, score=0.8)

    results = reranker.rerank("query", [chunk1, chunk2], top_n=2)
    assert results[0].id == "c2" # c2 boosted to rank 1
    assert results[0].score == 5.8
    assert results[1].id == "c1"
