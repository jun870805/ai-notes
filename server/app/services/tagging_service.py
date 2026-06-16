from __future__ import annotations

import json
import re
from urllib import request
from urllib.error import HTTPError, URLError

from app.config import settings


class TaggingServiceError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class TaggingService:
    _candidates = [
        "fastapi",
        "websocket",
        "streaming",
        "backend",
        "frontend",
        "react",
        "pgvector",
        "retrieval",
        "docker",
        "auth",
        "jwt",
        "markdown",
    ]

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model if model is not None else settings.gemini_tag_model

    def generate_tags(self, title: str, content: str, *, allow_fallback: bool = True) -> list[str]:
        fallback_tags = self._fallback_tags(title, content)
        if not self.api_key:
            return fallback_tags

        try:
            generated_tags = self._gemini_tags(title, content)
        except TaggingServiceError:
            if allow_fallback:
                return fallback_tags
            raise

        sanitized = self._sanitize_tags(generated_tags)
        if len(sanitized) >= 3:
            return sanitized[:6]
        if allow_fallback:
            return self._merge_tags(sanitized, fallback_tags)
        raise TaggingServiceError("tag_response_invalid", "Tag service returned an invalid response.")

    def normalize_tags(self, tags: list[str]) -> list[str]:
        return self._sanitize_tags(tags)

    def _gemini_tags(self, title: str, content: str) -> list[str]:
        payload = json.dumps(
            {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": self._build_prompt(title, content),
                            }
                        ]
                    }
                ]
            }
        ).encode("utf-8")
        req = request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 429:
                raise TaggingServiceError("tag_rate_limited", "Tag service is rate limited.", 429) from exc
            if exc.code == 401:
                raise TaggingServiceError("tag_auth_failed", "Tag service authentication failed.", 401) from exc
            raise TaggingServiceError("tag_request_failed", "Tag service request failed.") from exc
        except URLError as exc:
            raise TaggingServiceError("tag_unavailable", "Tag service is unavailable.") from exc

        text = self._extract_text(body)
        if not text:
            raise TaggingServiceError("tag_response_invalid", "Tag service returned an invalid response.")
        return self._parse_tags(text)

    def _build_prompt(self, title: str, content: str) -> str:
        return (
            "請根據以下技術筆記產生 3 到 6 個標籤。"
            "標籤必須使用小寫英文或 kebab-case，只輸出 JSON 陣列，不要輸出其他說明。\n\n"
            f"title:\n{title.strip()}\n\n"
            f"content:\n{content.strip()}"
        )

    def _extract_text(self, body: dict) -> str:
        candidates = body.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [part.get("text", "").strip() for part in parts if part.get("text")]
        return "\n".join(texts).strip()

    def _parse_tags(self, text: str) -> list[str]:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None

        if isinstance(parsed, dict):
            parsed = parsed.get("tags", [])
        if isinstance(parsed, list):
            return [str(item) for item in parsed]

        return [part.strip() for part in re.split(r"[\n,]", text) if part.strip()]

    def _sanitize_tags(self, tags: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for tag in tags:
            cleaned = re.sub(r"[^a-z0-9]+", "-", tag.strip().lower()).strip("-")
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            normalized.append(cleaned)
            if len(normalized) == 6:
                break
        return normalized

    def _merge_tags(self, generated_tags: list[str], fallback_tags: list[str]) -> list[str]:
        merged = list(generated_tags)
        seen = set(generated_tags)
        for tag in fallback_tags:
            if tag in seen:
                continue
            seen.add(tag)
            merged.append(tag)
            if len(merged) == 6:
                break
        return merged[:6]

    def _fallback_tags(self, title: str, content: str) -> list[str]:
        haystack = f"{title}\n{content}".lower()
        tags = [tag for tag in self._candidates if tag in haystack][:6]
        if len(tags) >= 3:
            return tags

        words = [
            word
            for word in re.split(r"[^a-z0-9]+", haystack)
            if len(word) > 3 and word.isascii() and word not in tags
        ]
        for word in words:
            tags.append(word)
            if len(tags) == 3:
                break
        return tags[:6] or ["engineering-note", "notes", "knowledge"]
