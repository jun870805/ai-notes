from __future__ import annotations

import hashlib
import json
from urllib.error import HTTPError, URLError
from urllib import request

from app.config import settings


class EmbeddingServiceError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class EmbeddingService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model if model is not None else settings.gemini_embedding_model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self.api_key:
            return [self._fallback_embedding(text) for text in texts]
        return [self._gemini_embedding(text) for text in texts]

    def embed_documents(self, title: str, texts: list[str]) -> list[list[float]]:
        formatted_texts = [self._format_document_for_retrieval(title, text) for text in texts]
        return self.embed_texts(formatted_texts)

    def _fallback_embedding(self, text: str, *, dimensions: int = 12) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [round((digest[index] / 255.0) * 2 - 1, 6) for index in range(dimensions)]

    def _format_document_for_retrieval(self, title: str, text: str) -> str:
        return f"title: {title.strip()} | text: {text.strip()}"

    def _gemini_embedding(self, text: str) -> list[float]:
        payload = json.dumps(
            {
                "model": f"models/{self.model}",
                "content": {
                    "parts": [
                        {
                            "text": text,
                        }
                    ]
                },
            }
        ).encode("utf-8")
        req = request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent",
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
                raise EmbeddingServiceError("embedding_rate_limited", "Embedding service is rate limited.", 429) from exc
            if exc.code == 401:
                raise EmbeddingServiceError("embedding_auth_failed", "Embedding service authentication failed.", 401) from exc
            raise EmbeddingServiceError("embedding_request_failed", "Embedding service request failed.") from exc
        except URLError as exc:
            raise EmbeddingServiceError("embedding_unavailable", "Embedding service is unavailable.") from exc
        if "embedding" in body and "values" in body["embedding"]:
            return body["embedding"]["values"]
        if "embeddings" in body and body["embeddings"]:
            return body["embeddings"][0]["values"]
        raise EmbeddingServiceError("embedding_response_invalid", "Embedding service returned an invalid response.")
