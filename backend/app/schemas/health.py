from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class ComponentStatus(StrEnum):
    OK = "ok"
    UNREACHABLE = "unreachable"


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class HealthChecks(BaseModel):
    api: Literal[ComponentStatus.OK] = ComponentStatus.OK
    database: ComponentStatus


class HealthCheckResponse(BaseModel):
    status: HealthStatus
    checks: HealthChecks
    message: str
    timestamp: datetime
