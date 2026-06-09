from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.note_repository import NoteRepository
from app.schemas.common import Envelope, success_envelope
from app.schemas.note import NoteCreateRequest, NoteRead, NoteUpdateRequest
from app.services.note_service import NoteService
from app.services.tagging_service import TaggingService

router = APIRouter(tags=["Notes"])


def _service(db: Session) -> NoteService:
    return NoteService(NoteRepository(db), TaggingService())


@router.get("/notes", response_model=Envelope)
def list_notes(db: Session = Depends(get_db)) -> dict:
    notes = _service(db).list_notes()
    return success_envelope([NoteRead.model_validate(note).model_dump(mode="json") for note in notes])


@router.get("/notes/{note_id}", response_model=Envelope)
def get_note(note_id: str, db: Session = Depends(get_db)) -> dict:
    note = _service(db).get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")
    return success_envelope(NoteRead.model_validate(note).model_dump(mode="json"))


@router.post("/notes", status_code=status.HTTP_201_CREATED, response_model=Envelope)
def create_note(payload: NoteCreateRequest, db: Session = Depends(get_db)) -> dict:
    note = _service(db).create_note(payload.title, payload.content, payload.tags)
    return success_envelope(NoteRead.model_validate(note).model_dump(mode="json"))


@router.put("/notes/{note_id}", response_model=Envelope)
def update_note(note_id: str, payload: NoteUpdateRequest, db: Session = Depends(get_db)) -> dict:
    service = _service(db)
    note = service.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")
    updated = service.update_note(note, payload.title, payload.content, payload.tags)
    return success_envelope(NoteRead.model_validate(updated).model_dump(mode="json"))


@router.delete("/notes/{note_id}", response_model=Envelope)
def delete_note(note_id: str, db: Session = Depends(get_db)) -> dict:
    service = _service(db)
    note = service.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")
    NoteRepository(db).delete_note(note)
    return success_envelope("note deleted")
