"""add_pgvector_and_embedding

Revision ID: 9c93b7347812
Revises: b9fc4472a124
Create Date: 2026-07-23 17:40:13.017595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c93b7347812'
down_revision: Union[str, Sequence[str], None] = 'b9fc4472a124'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import pgvector.sqlalchemy

def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.add_column('timeline_events', sa.Column('embedding', pgvector.sqlalchemy.Vector(1536), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('timeline_events', 'embedding')
    op.execute("DROP EXTENSION IF EXISTS vector;")
