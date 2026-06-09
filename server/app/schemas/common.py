from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class Envelope(BaseModel):
    code: str
    success: bool
    message: str | None
    data: Any

    model_config = ConfigDict(from_attributes=True)


def success_envelope(data: Any, code: str = "success") -> dict[str, Any]:
    return {"code": code, "success": True, "message": None, "data": data}


def error_envelope(code: str, message: str) -> dict[str, Any]:
    return {"code": code, "success": False, "message": message, "data": None}

