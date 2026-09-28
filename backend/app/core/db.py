from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import Settings, get_settings


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.database_url)


_engine: AsyncEngine | None = None


async def get_engine(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncIterator[AsyncEngine]:
    global _engine  # noqa: PLW0603
    if _engine is None:
        _engine = create_engine(settings)
    yield _engine
