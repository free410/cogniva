"""baseline

首次建立迁移基线：以当前 ORM 模型为准创建全部表结构。
已有数据库执行 `alembic stamp head` 即可标记为已应用，无需重复建表。

Revision ID: 9703841e02d9
Revises: 
Create Date: 2026-11-07 21:09:55.801041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9703841e02d9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from core.database import Base
    import models  # noqa: F401

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Downgrade schema."""
    from core.database import Base
    import models  # noqa: F401

    Base.metadata.drop_all(bind=op.get_bind())
