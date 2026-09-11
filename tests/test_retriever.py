import pytest
from unittest.mock import MagicMock
from app.rag.retriever import RAGRetriever, RetrievedChunk

def test_retriever_empty_query():
    retriever = RAGRetriever()
    results = retriever.retrieve("")
    assert results == []

def test_retriever_mocked_results():
    mock_vector_store = MagicMock()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 1

    mock_collection.query.return_value = {
        "ids": [["policy_001"]],
        "documents": [["Refund policy details here."]],
        "metadatas": [[{"source": "policy.md", "section": "Refunds"}]],
        "distances": [[0.15]]
    }
    mock_vector_store.get_or_create_collection.return_value = mock_collection
    mock_vector_store.embedder.get_embedding.return_value = [0.1] * 768

    retriever = RAGRetriever(vector_store=mock_vector_store)
    results = retriever.retrieve("How to refund?", top_k=1)

    assert len(results) == 1
    assert results[0].id == "policy_001"
    assert results[0].metadata["section"] == "Refunds"
    assert results[0].distance == 0.15
    assert results[0].score > 0.8

def test_retriever_graceful_error_handling():
    mock_vector_store = MagicMock()
    # Simulate DB failure
    mock_vector_store.get_or_create_collection.side_effect = Exception("Chroma connection error")

    retriever = RAGRetriever(vector_store=mock_vector_store)
    # Should not throw exception, returns empty list
    results = retriever.retrieve("Any query")
    assert results == []
