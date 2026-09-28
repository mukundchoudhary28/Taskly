import asyncio
import time
from unittest.mock import AsyncMock, patch

from app.schemas.health import ComponentStatus, HealthStatus
from app.services.health import get_health_status


async def test_health_timeout_bounded() -> None:
    mock_engine = AsyncMock()

    async def _hang(engine: object) -> None:
        await asyncio.sleep(999)

    with patch("app.services.health.check_database", side_effect=_hang):
        start = time.monotonic()
        result = await get_health_status(mock_engine, db_timeout=0.2)
        elapsed = time.monotonic() - start

    assert result.status == HealthStatus.DEGRADED
    assert result.checks.database == ComponentStatus.UNREACHABLE
    assert elapsed < 1.0


async def test_health_service_healthy() -> None:
    mock_engine = AsyncMock()

    async def _ok(engine: object) -> None:
        pass

    with patch("app.services.health.check_database", side_effect=_ok):
        result = await get_health_status(mock_engine, db_timeout=3.0)

    assert result.status == HealthStatus.HEALTHY
    assert result.checks.database == ComponentStatus.OK


async def test_health_service_db_error() -> None:
    mock_engine = AsyncMock()

    async def _fail(engine: object) -> None:
        raise OSError("Connection refused")

    with patch("app.services.health.check_database", side_effect=_fail):
        result = await get_health_status(mock_engine, db_timeout=3.0)

    assert result.status == HealthStatus.DEGRADED
    assert result.checks.database == ComponentStatus.UNREACHABLE
    assert result.message == "Database is unreachable"
