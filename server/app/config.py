from __future__ import annotations

import os
from dataclasses import dataclass, field


def _parse_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _normalize_api_key(*env_names: str) -> str:
    for env_name in env_names:
        value = os.getenv(env_name, "").strip()
        if value and value != "your_api_key":
            return value
    return ""


@dataclass(slots=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ai_notes.db")
    gemini_api_key: str = _normalize_api_key("GEMINI_API_KEY", "OPENAI_API_KEY")
    gemini_embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", os.getenv("OPENAI_EMBEDDING_MODEL", "gemini-embedding-2"))
    gemini_chat_model: str = os.getenv("GEMINI_CHAT_MODEL", os.getenv("OPENAI_CHAT_MODEL", "gemini-3.5-flash"))
    cors_allow_origins: list[str] = field(default_factory=_parse_cors_origins)


settings = Settings()
