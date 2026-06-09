from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.note_repository import NoteRepository
from app.schemas.ai import ChatRequest, ChatResponseData, SearchRequest, SearchResponseData, TagRequest, TagResponseData
from app.schemas.common import Envelope, success_envelope
from app.services.chat_service import ChatService
from app.services.search_service import SearchService
from app.services.tagging_service import TaggingService

router = APIRouter(tags=["AI"])


@router.post("/ai/tag", response_model=Envelope)
def generate_tags(payload: TagRequest) -> dict:
    tags = TaggingService().generate_tags(payload.title, payload.content)
    data = TagResponseData(tags=tags).model_dump(mode="json")
    return success_envelope(data)


@router.post("/ai/search", response_model=Envelope)
def search_notes(payload: SearchRequest, db: Session = Depends(get_db)) -> dict:
    notes = NoteRepository(db).list_notes()
    results = SearchService().search_notes(notes, payload.query, payload.top_k)
    data = SearchResponseData(results=results).model_dump(mode="json")
    return success_envelope(data)


@router.post("/ai/chat", response_model=Envelope)
def chat_with_notes(payload: ChatRequest, db: Session = Depends(get_db)) -> dict:
    notes = NoteRepository(db).list_notes()
    sources = SearchService().search_notes(notes, payload.question, payload.top_k)
    answer = ChatService().answer(payload.question, sources)
    data = ChatResponseData(answer=answer, sources=sources).model_dump(mode="json")
    return success_envelope(data)

