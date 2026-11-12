"""align users username not null

已有库的 users.username 允许为空，与 ORM 模型（nullable=False）不一致。
本次迁移补齐 NOT NULL 约束。

Revision ID: b148e0233258
Revises: 9703841e02d9
Create Date: 2026-11-07 21:11:36.661708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b148e0233258'
down_revision: Union[str, Sequence[str], None] = '9703841e02d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE users ALTER COLUMN username SET NOT NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE users ALTER COLUMN username DROP NOT NULL")
