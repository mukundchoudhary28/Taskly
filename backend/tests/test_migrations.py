import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


@pytest.mark.integration
def test_alembic_upgrade_creates_no_product_tables() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")

    from app.core.config import get_settings

    sync_url = get_settings().database_url.replace("+psycopg", "+psycopg")
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        tables = inspect(conn).get_table_names()
    engine.dispose()

    product_tables = [t for t in tables if t != "alembic_version"]
    assert product_tables == [], f"Unexpected tables: {product_tables}"


@pytest.mark.integration
def test_alembic_upgrade_idempotent() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    command.upgrade(cfg, "head")
