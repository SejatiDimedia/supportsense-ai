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
