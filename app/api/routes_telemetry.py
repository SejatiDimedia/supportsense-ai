import logging
from typing import Dict, Any
from fastapi import APIRouter

from app.config import settings
from app.rag.embedder import VectorStoreManager
from app.kag.graph_builder import SupportKnowledgeGraph
from app.persistence.repository import repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Telemetry"])

@router.get("/telemetry")
async def get_telemetry() -> Dict[str, Any]:
    """
    Returns live system telemetry and topology metrics for SupportSense AI:
    ChromaDB vector count, PostgreSQL Knowledge Graph size, pending escalations,
    and configured model versions.
    """
    # 1. ChromaDB vector count
    try:
        vsm = VectorStoreManager()
        collection = vsm.get_or_create_collection()
        chroma_count = collection.count()
    except Exception as e:
        logger.warning(f"Failed to query ChromaDB count: {e}")
        chroma_count = 0

    # 2. Knowledge Graph nodes and edges (loaded from PostgreSQL)
    try:
        kg = SupportKnowledgeGraph()
        graph_nodes = kg.graph.number_of_nodes()
        graph_edges = kg.graph.number_of_edges()
    except Exception as e:
        logger.warning(f"Failed to query Knowledge Graph topology: {e}")
        graph_nodes = 0
        graph_edges = 0

    # 3. Pending Escalations Queue
    try:
        pending_list = repo.get_pending_escalations()
        pending_count = len(pending_list)
    except Exception as e:
        logger.warning(f"Failed to query pending escalations queue: {e}")
        pending_count = 0

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "chroma_count": chroma_count,
        "graph_nodes": graph_nodes,
        "graph_edges": graph_edges,
        "pending_escalations": pending_count,
        "models": {
            "llm": getattr(settings, "llm_model", "hermes3:latest"),
            "embedding": getattr(settings, "embedding_model", "nomic-embed-text"),
        },
        "database": {
            "postgres_url": settings.postgres_url,
            "connected": True if graph_nodes > 0 else False
        }
    }
