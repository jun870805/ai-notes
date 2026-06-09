from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    tags: list[str] | None = None


class NoteCreateRequest(NoteBase):
    pass


class NoteUpdateRequest(NoteBase):
    pass


class NoteRead(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

