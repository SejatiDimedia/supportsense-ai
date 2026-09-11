import time
from fastapi import APIRouter
import httpx
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    start_time = time.time()
    ollama_status = "disconnected"
    n8n_status = "disconnected"

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                ollama_status = "connected"
    except Exception:
        ollama_status = "disconnected"

    # Check n8n webhook host
    try:
        base_n8n = settings.n8n_webhook_url.split("/webhook")[0]
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{base_n8n}/healthz")
            if resp.status_code in (200, 404):
                n8n_status = "connected"
    except Exception:
        n8n_status = "disconnected"

    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "status": "ok" if ollama_status == "connected" else "degraded",
        "app": settings.app_name,
        "ollama": {
            "status": ollama_status,
            "url": settings.ollama_base_url,
            "model": settings.llm_model,
            "embedding": settings.embedding_model
        },
        "n8n": {
            "status": n8n_status,
            "webhook_url": settings.n8n_webhook_url
        },
        "latency_ms": duration_ms
    }
