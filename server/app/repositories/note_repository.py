from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.note import Note


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
        self.db.commit()
        self.db.refresh(note)
        return note

    def update_note(self, note: Note, *, title: str, content: str, tags: list[str] | None) -> Note:
        note.title = title
        note.content = content
        note.tags = tags
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete_note(self, note: Note) -> None:
        self.db.delete(note)
        self.db.commit()

