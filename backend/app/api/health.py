from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings, get_settings
from app.core.db import get_engine
from app.schemas.health import HealthCheckResponse, HealthStatus
from app.services.health import get_health_status

router = APIRouter()


async def get_health_check_result(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckResponse:
    return await get_health_status(engine, settings.health_check_db_timeout_seconds)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    result: Annotated[HealthCheckResponse, Depends(get_health_check_result)],
    response: Response,
) -> HealthCheckResponse:
    if result.status == HealthStatus.DEGRADED:
        response.status_code = 503
    return result
