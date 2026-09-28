"""baseline

Revision ID: 4e851c599c2c
Revises:
Create Date: 2026-09-28 17:16:29.665052

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "4e851c599c2c"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
