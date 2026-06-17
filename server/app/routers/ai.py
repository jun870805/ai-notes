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


def _dedupe_results_by_note(results):
    deduped = []
    seen_note_ids: set[str] = set()
    for result in results:
        if result.note_id in seen_note_ids:
            continue
        deduped.append(result)
        seen_note_ids.add(result.note_id)
    return deduped


@router.post("/ai/tag", response_model=Envelope)
def generate_tags(payload: TagRequest) -> dict:
    tags = TaggingService().generate_tags(payload.title, payload.content, allow_fallback=False)
    data = TagResponseData(tags=tags).model_dump(mode="json")
    return success_envelope(data)


@router.post("/ai/search", response_model=Envelope)
def search_notes(payload: SearchRequest, db: Session = Depends(get_db)) -> dict:
    note_repository = NoteRepository(db)
    results = SearchService(note_repository).search_notes(payload.query, payload.top_k)
    data = SearchResponseData(results=results).model_dump(mode="json")
    return success_envelope(data)


@router.post("/ai/chat", response_model=Envelope)
def chat_with_notes(payload: ChatRequest, db: Session = Depends(get_db)) -> dict:
    note_repository = NoteRepository(db)
    search_service = SearchService(note_repository)
    context_sources = search_service.search_notes(
        payload.question,
        max(payload.top_k * 4, payload.top_k),
        dedupe_by_note=False,
    )
    response_sources = _dedupe_results_by_note(context_sources)[: payload.top_k]
    answer = ChatService().answer(payload.question, context_sources)
    data = ChatResponseData(answer=answer, sources=response_sources).model_dump(mode="json")
    return success_envelope(data)
