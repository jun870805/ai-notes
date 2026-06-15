from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError

from app.config import settings
from app.schemas.ai import SearchResult


class ChatServiceError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ChatService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model if model is not None else settings.gemini_chat_model

    def answer(self, question: str, sources: list[SearchResult]) -> str:
        if not sources:
            return "沒有足夠的筆記資料可以回答這個問題。"
        if not self.api_key:
            return self._fallback_answer(question, sources)
        return self._gemini_answer(question, sources)

    def _fallback_answer(self, question: str, sources: list[SearchResult]) -> str:
        combined = " ".join(source.chunk_text for source in sources)
        return f"根據目前檢索到的筆記內容，{combined} 以上回答對應問題「{question}」。"

    def _build_prompt(self, question: str, sources: list[SearchResult]) -> str:
        rendered_sources = "\n\n".join(
            [
                (
                    f"來源 {index}\n"
                    f"筆記標題: {source.note_title}\n"
                    f"筆記 ID: {source.note_id}\n"
                    f"相似度: {source.similarity_score}\n"
                    f"內容: {source.chunk_text}"
                )
                for index, source in enumerate(sources, start=1)
            ]
        )
        return (
            "你是使用者個人技術筆記的問答助理。"
            "你只能根據提供的筆記來源回答問題，不能捏造來源中沒有的內容。"
            "如果來源不足以回答，請明確說明資訊不足。\n\n"
            f"問題:\n{question}\n\n"
            f"筆記來源:\n{rendered_sources}\n\n"
            "請使用繁體中文回答，並保持精簡。"
        )

    def _gemini_answer(self, question: str, sources: list[SearchResult]) -> str:
        payload = json.dumps(
            {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": self._build_prompt(question, sources),
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
                raise ChatServiceError("chat_rate_limited", "Chat service is rate limited.", 429) from exc
            if exc.code == 401:
                raise ChatServiceError("chat_auth_failed", "Chat service authentication failed.", 401) from exc
            raise ChatServiceError("chat_request_failed", "Chat service request failed.") from exc
        except URLError as exc:
            raise ChatServiceError("chat_unavailable", "Chat service is unavailable.") from exc

        answer = self._extract_text(body)
        if not answer:
            raise ChatServiceError("chat_response_invalid", "Chat service returned an invalid response.")
        return answer

    def _extract_text(self, body: dict) -> str:
        candidates = body.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [part.get("text", "").strip() for part in parts if part.get("text")]
        return "\n".join(texts).strip()
