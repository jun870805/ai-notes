from __future__ import annotations

from datetime import datetime, timezone
from math import sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.note import Note
from app.models.note_chunk import NoteChunk
from app.services.chunking_service import ChunkDraft


class NoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_notes(self) -> list[Note]:
        stmt = select(Note).order_by(Note.updated_at.desc())
        return list(self.db.scalars(stmt))

    def get_note(self, note_id: str) -> Note | None:
        return self.db.get(Note, note_id)

    def create_note(self, *, title: str, content: str, tags: list[str] | None) -> Note:
        note = Note(title=title, content=content, tags=tags)
        self.db.add(note)
        self.db.flush()
        return note

    def update_note(self, note: Note, *, title: str, content: str, tags: list[str] | None) -> Note:
        note.title = title
        note.content = content
        note.tags = tags
        self.db.add(note)
        self.db.flush()
        return note

    def replace_note_chunks(
        self, note: Note, *, chunks: list[ChunkDraft], embeddings: list[list[float]]
    ) -> None:
        note.chunks.clear()
        self.db.flush()
        note.embedding_updated_at = datetime.now(timezone.utc)
        self.db.add_all(
            [
                NoteChunk(
                    note_id=note.id,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.chunk_text,
                    token_count=chunk.token_count,
                    embedding=embedding,
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]
        )
        self.db.flush()

    def build_similarity_search_stmt(self, query_embedding: list[float], *, top_k: int = 5):
        return (
            select(NoteChunk)
            .options(joinedload(NoteChunk.note))
            .order_by(NoteChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )

    def search_similar_chunks(self, query_embedding: list[float], *, top_k: int = 5) -> list[NoteChunk]:
        if self.db.bind is not None and self.db.bind.dialect.name == "sqlite":
            return self._search_similar_chunks_sqlite(query_embedding, top_k=top_k)
        return list(self.db.scalars(self.build_similarity_search_stmt(query_embedding, top_k=top_k)))

    def _search_similar_chunks_sqlite(self, query_embedding: list[float], *, top_k: int = 5) -> list[NoteChunk]:
        stmt = select(NoteChunk).options(joinedload(NoteChunk.note))
        chunks = list(self.db.scalars(stmt))
        chunks.sort(key=lambda chunk: self._cosine_distance(query_embedding, chunk.embedding))
        return chunks[:top_k]

    @staticmethod
    def _cosine_distance(left: list[float], right: list[float]) -> float:
        if len(left) != len(right) or not left:
            return 1.0
        dot = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = sqrt(sum(value * value for value in left))
        right_norm = sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 1.0
        cosine_similarity = dot / (left_norm * right_norm)
        cosine_similarity = max(-1.0, min(1.0, cosine_similarity))
        return 1 - cosine_similarity

    def delete_note(self, note: Note) -> None:
        self.db.delete(note)
        self.db.commit()
