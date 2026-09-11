import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
import chromadb
from chromadb.api.models.Collection import Collection

from app.config import settings
from app.rag.chunking import MarkdownSectionChunker, DocumentChunk

logger = logging.getLogger(__name__)

class OllamaEmbedder:
    """Client for generating vector embeddings via Ollama."""
    def __init__(self, base_url: str = settings.ollama_base_url, model: str = settings.embedding_model):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def get_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model, "prompt": text}
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return embeddings

    async def aget_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model, "prompt": text}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]

class VectorStoreManager:
    """Manages Chroma persistent collection for support docs."""
    def __init__(self, persist_dir: str = settings.chroma_persist_dir, embedder: Optional[OllamaEmbedder] = None):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embedder = embedder or OllamaEmbedder()
        self.collection_name = "support_docs"

    def get_or_create_collection(self) -> Collection:
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Customer Support FAQ, Policies, and Manuals"}
        )

    def ingest_documents(self, docs_dir: Path, force_reload: bool = False) -> int:
        collection = self.get_or_create_collection()
        current_count = collection.count()

        if current_count > 0 and not force_reload:
            logger.info(f"Collection '{self.collection_name}' already contains {current_count} documents. Skipping re-ingestion.")
            return current_count

        if force_reload and current_count > 0:
            logger.info(f"Force reload active. Resetting collection '{self.collection_name}'...")
            self.client.delete_collection(self.collection_name)
            collection = self.get_or_create_collection()

        chunker = MarkdownSectionChunker(max_chunk_chars=1200, overlap_chars=150)
        all_chunks: List[DocumentChunk] = []

        for file_path in sorted(docs_dir.glob("*.md")):
            chunks = chunker.chunk_file(file_path)
            all_chunks.extend(chunks)

        if not all_chunks:
            logger.warning(f"No documents found to ingest in {docs_dir}")
            return 0

        ids = [c.id for c in all_chunks]
        documents = [c.text for c in all_chunks]
        metadatas = [c.metadata for c in all_chunks]

        logger.info(f"Generating embeddings for {len(all_chunks)} chunks via Ollama ({self.embedder.model})...")
        embeddings = self.embedder.get_embeddings_batch(documents)

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        final_count = collection.count()
        logger.info(f"Ingestion completed. Total documents in Chroma: {final_count}")
        return final_count
