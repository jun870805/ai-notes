from __future__ import annotations

from app.models.note import Note
from app.repositories.note_repository import NoteRepository
from app.services.tagging_service import TaggingService


class NoteService:
    def __init__(self, repository: NoteRepository, tagging_service: TaggingService) -> None:
        self.repository = repository
        self.tagging_service = tagging_service

    def list_notes(self) -> list[Note]:
        return self.repository.list_notes()

    def get_note(self, note_id: str) -> Note | None:
        return self.repository.get_note(note_id)

    def create_note(self, title: str, content: str, tags: list[str] | None) -> Note:
        final_tags = tags if tags is not None else self.tagging_service.generate_tags(title, content)
        return self.repository.create_note(title=title, content=content, tags=final_tags)

    def update_note(self, note: Note, title: str, content: str, tags: list[str] | None) -> Note:
        final_tags = tags if tags is not None else self.tagging_service.generate_tags(title, content)
        return self.repository.update_note(note, title=title, content=content, tags=final_tags)

