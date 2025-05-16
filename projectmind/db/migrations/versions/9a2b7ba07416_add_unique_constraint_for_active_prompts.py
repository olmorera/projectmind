"""add unique constraint for active prompts

Revision ID: 9a2b7ba07416
Revises: b119f2bef33d
Create Date: 2025-05-16 02:06:14.978188
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa  # ✅ esta línea es la clave

# revision identifiers
revision: str = '9a2b7ba07416'
down_revision: Union[str, None] = 'b119f2bef33d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "unique_active_prompt",
        "prompts",
        ["agent_name", "task_type"],
        unique=True,
        postgresql_where=sa.text("is_active = TRUE")
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("unique_active_prompt", table_name="prompts")
