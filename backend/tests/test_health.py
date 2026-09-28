from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.health import get_health_check_result
from app.main import app
from app.schemas.health import (
    ComponentStatus,
    HealthCheckResponse,
    HealthChecks,
    HealthStatus,
)


def _healthy_response() -> HealthCheckResponse:
    return HealthCheckResponse(
        status=HealthStatus.HEALTHY,
        checks=HealthChecks(database=ComponentStatus.OK),
        message="API and database are healthy",
        timestamp=datetime.now(UTC),
    )


def _degraded_response() -> HealthCheckResponse:
    return HealthCheckResponse(
        status=HealthStatus.DEGRADED,
        checks=HealthChecks(database=ComponentStatus.UNREACHABLE),
        message="Database is unreachable",
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
async def healthy_client() -> AsyncIterator[AsyncClient]:
    async def _override() -> HealthCheckResponse:
        return _healthy_response()

    app.dependency_overrides[get_health_check_result] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def degraded_client() -> AsyncIterator[AsyncClient]:
    async def _override() -> HealthCheckResponse:
        return _degraded_response()

    app.dependency_overrides[get_health_check_result] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_health_healthy(healthy_client: AsyncClient) -> None:
    resp = await healthy_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["checks"]["api"] == "ok"
    assert body["checks"]["database"] == "ok"
    assert body["message"] == "API and database are healthy"
    assert "timestamp" in body


async def test_health_degraded_no_leak(degraded_client: AsyncClient) -> None:
    resp = await degraded_client.get("/health")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "unreachable"
    assert body["message"] == "Database is unreachable"

    raw = resp.text
    for forbidden in ["Traceback", "psycopg", "localhost:5432", "taskly_dev"]:
        assert forbidden not in raw, f"Leaked internal detail: {forbidden}"
