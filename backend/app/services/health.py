import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.repositories.health import check_database
from app.schemas.health import (
    ComponentStatus,
    HealthCheckResponse,
    HealthChecks,
    HealthStatus,
)

logger = logging.getLogger(__name__)


async def get_health_status(
    engine: AsyncEngine,
    db_timeout: float,
) -> HealthCheckResponse:
    try:
        await asyncio.wait_for(check_database(engine), timeout=db_timeout)
        db_status = ComponentStatus.OK
    except (TimeoutError, OSError, SQLAlchemyError) as exc:
        logger.warning("Health check: database unreachable: %r", exc)
        db_status = ComponentStatus.UNREACHABLE

    if db_status == ComponentStatus.OK:
        return HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            checks=HealthChecks(database=ComponentStatus.OK),
            message="API and database are healthy",
            timestamp=datetime.now(UTC),
        )

    return HealthCheckResponse(
        status=HealthStatus.DEGRADED,
        checks=HealthChecks(database=ComponentStatus.UNREACHABLE),
        message="Database is unreachable",
        timestamp=datetime.now(UTC),
    )
