"""add note chunk metadata

Revision ID: 20260611_0002
Revises: 20260609_0001
Create Date: 2026-06-11 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260611_0002"
down_revision: Union[str, None] = "20260609_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("embedding_updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("note_chunks", sa.Column("chunk_index", sa.Integer(), nullable=True))
    op.add_column("note_chunks", sa.Column("token_count", sa.Integer(), nullable=True))
    op.execute("UPDATE note_chunks SET chunk_index = 0 WHERE chunk_index IS NULL")
    op.execute("UPDATE note_chunks SET embedding = '[]' WHERE embedding IS NULL")
    with op.batch_alter_table("note_chunks") as batch_op:
        batch_op.alter_column("chunk_index", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("embedding", existing_type=sa.JSON(), nullable=False)
        batch_op.create_index("ix_note_chunks_note_id_chunk_index", ["note_id", "chunk_index"])


def downgrade() -> None:
    with op.batch_alter_table("note_chunks") as batch_op:
        batch_op.drop_index("ix_note_chunks_note_id_chunk_index")
        batch_op.drop_column("token_count")
        batch_op.drop_column("chunk_index")
    op.drop_column("notes", "embedding_updated_at")
