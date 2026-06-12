"""convert note chunk embeddings to pgvector

Revision ID: 20260612_0003
Revises: 20260611_0002
Create Date: 2026-06-12 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


revision: str = "20260612_0003"
down_revision: Union[str, None] = "20260611_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
EMBEDDING_DIMENSIONS = 3072


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("note_chunks", sa.Column("embedding_vector", VECTOR(EMBEDDING_DIMENSIONS), nullable=True))
    op.execute("UPDATE note_chunks SET embedding_vector = embedding::text::vector WHERE embedding IS NOT NULL")
    op.execute("ALTER TABLE note_chunks DROP COLUMN embedding")
    op.execute("ALTER TABLE note_chunks RENAME COLUMN embedding_vector TO embedding")
    op.execute("ALTER TABLE note_chunks ALTER COLUMN embedding SET NOT NULL")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.add_column("note_chunks", sa.Column("embedding_json", sa.JSON(), nullable=True))
    op.execute("UPDATE note_chunks SET embedding_json = embedding::text::json WHERE embedding IS NOT NULL")
    op.execute("ALTER TABLE note_chunks DROP COLUMN embedding")
    op.execute("ALTER TABLE note_chunks RENAME COLUMN embedding_json TO embedding")
    op.execute("ALTER TABLE note_chunks ALTER COLUMN embedding SET NOT NULL")
