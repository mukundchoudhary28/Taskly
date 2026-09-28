from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.db import get_engine
from app.main import app


@pytest.mark.integration
async def test_health_healthy_real_db() -> None:
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["checks"]["database"] == "ok"


@pytest.mark.integration
async def test_health_degraded_real_db() -> None:
    unreachable_engine = create_async_engine(
        "postgresql+psycopg://taskly:taskly@127.0.0.1:1/taskly_dev"
    )

    async def _unreachable_engine() -> AsyncIterator[AsyncEngine]:
        yield unreachable_engine

    app.dependency_overrides[get_engine] = _unreachable_engine
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 503
        body = resp.json()
        assert body["status"] == "degraded"
        assert body["checks"]["database"] == "unreachable"
    finally:
        app.dependency_overrides.clear()
        await unreachable_engine.dispose()
