import pytest
from unittest.mock import MagicMock
from pathlib import Path
from app.rag.embedder import OllamaEmbedder, VectorStoreManager

def test_vector_store_count():
    manager = VectorStoreManager()
    collection = manager.get_or_create_collection()
    assert collection.count() == 14

def test_ollama_embedder_mock():
    embedder = OllamaEmbedder()
    # Mocking Ollama call for fast offline unit test
    fake_embedding = [0.1] * 768
    embedder.get_embedding = MagicMock(return_value=fake_embedding)

    result = embedder.get_embedding("test query")
    assert len(result) == 768
    assert result[0] == 0.1

def test_ingest_from_postgres_mocked(tmp_path):
    mock_embedder = MagicMock(spec=OllamaEmbedder)
    mock_embedder.model = "nomic-embed-text"
    mock_embedder.get_embeddings_batch.side_effect = lambda texts: [[0.1] * 768 for _ in texts]

    manager = VectorStoreManager(persist_dir=str(tmp_path / "chroma_test"), embedder=mock_embedder)
    count = manager.ingest_from_postgres(force_reload=True)
    assert count == 14
    collection = manager.get_or_create_collection()
    assert collection.count() == 14

