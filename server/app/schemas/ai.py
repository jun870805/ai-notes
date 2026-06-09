from __future__ import annotations

from pydantic import BaseModel, Field


class TagRequest(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1)


class SearchResult(BaseModel):
    note_id: str
    note_title: str
    chunk_text: str
    similarity_score: float


class SearchResponseData(BaseModel):
    results: list[SearchResult]


class ChatResponseData(BaseModel):
    answer: str
    sources: list[SearchResult]


class TagResponseData(BaseModel):
    tags: list[str]

