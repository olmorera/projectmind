"""drop old prompts table

Revision ID: 7e04d4c9cda2
Revises: 4d63c705a8a3
Create Date: 2025-05-16 01:01:48.443151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e04d4c9cda2'
down_revision: Union[str, None] = '4d63c705a8a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
