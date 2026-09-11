import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.observability.metrics import MetricsCollector

def test_metrics_collector_recording():
    collector = MetricsCollector()
    collector.record_request("rag", 150.0)
    collector.record_request("rag", 250.0)
    collector.record_request("hybrid", 500.0)
    collector.record_error("ollama")

    assert collector.requests_total["rag"] == 2
    assert collector.requests_total["hybrid"] == 1
    assert collector.errors_total["ollama"] == 1

    prom_text = collector.generate_prometheus_metrics()
    assert 'supportsense_requests_total{route="rag"} 2' in prom_text
    assert 'supportsense_requests_total{route="hybrid"} 1' in prom_text
    assert 'supportsense_errors_total{dependency="ollama"} 1' in prom_text
    assert "supportsense_process_memory_mb" in prom_text
    assert "supportsense_process_cpu_percent" in prom_text

@pytest.mark.asyncio
async def test_get_metrics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "supportsense_requests_total" in response.text
