from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.observability.metrics import metrics

router = APIRouter(tags=["Observability"])

@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """
    Returns application metrics in Prometheus exposition format.
    Scraped by Prometheus server or inspection tools.
    """
    return PlainTextResponse(
        content=metrics.generate_prometheus_metrics(),
        media_type="text/plain; version=0.0.4"
    )
