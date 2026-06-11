from __future__ import annotations

from app.models.note import Note
from app.repositories.note_repository import NoteRepository
from app.services.chunking_service import chunk_markdown
from app.services.embedding_service import EmbeddingService
from app.services.tagging_service import TaggingService


class NoteService:
    def __init__(
        self, repository: NoteRepository, tagging_service: TaggingService, embedding_service: EmbeddingService
    ) -> None:
        self.repository = repository
        self.tagging_service = tagging_service
        self.embedding_service = embedding_service

    def list_notes(self) -> list[Note]:
        return self.repository.list_notes()

    def get_note(self, note_id: str) -> Note | None:
        return self.repository.get_note(note_id)

    def create_note(self, title: str, content: str, tags: list[str] | None) -> Note:
        final_tags = tags if tags is not None else self.tagging_service.generate_tags(title, content)
        try:
            note = self.repository.create_note(title=title, content=content, tags=final_tags)
            self._rebuild_note_chunks(note)
            self.repository.db.commit()
            self.repository.db.refresh(note)
            return note
        except Exception:
            self.repository.db.rollback()
            raise

    def update_note(self, note: Note, title: str, content: str, tags: list[str] | None) -> Note:
        final_tags = tags if tags is not None else self.tagging_service.generate_tags(title, content)
        try:
            updated_note = self.repository.update_note(note, title=title, content=content, tags=final_tags)
            self._rebuild_note_chunks(updated_note)
            self.repository.db.commit()
            self.repository.db.refresh(updated_note)
            return updated_note
        except Exception:
            self.repository.db.rollback()
            raise

    def _rebuild_note_chunks(self, note: Note) -> None:
        chunks = chunk_markdown(note.content)
        embeddings = self.embedding_service.embed_documents(note.title, [chunk.chunk_text for chunk in chunks])
        self.repository.replace_note_chunks(note, chunks=chunks, embeddings=embeddings)
