import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama" in data

@pytest.mark.asyncio
async def test_telemetry():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "chroma_count" in data
    assert "graph_nodes" in data
    assert "graph_edges" in data
    assert "pending_escalations" in data
    assert "database" in data
    assert "postgres_url" not in data["database"]
    assert "postgres_url" not in response.text
    assert "password" not in response.text.lower()
    assert data["database"].get("engine") == "postgresql"
    assert "connected" in data["database"]

