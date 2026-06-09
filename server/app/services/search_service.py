from __future__ import annotations

import re

from app.models.note import Note
from app.schemas.ai import SearchResult


class SearchService:
    def search_notes(self, notes: list[Note], query: str, top_k: int) -> list[SearchResult]:
        terms = [term for term in re.split(r"[^a-z0-9]+", query.lower()) if term]
        if not terms:
            return []

        results: list[SearchResult] = []
        for note in notes:
            source = f"{note.title}\n{note.content}".lower()
            hits = sum(1 for term in terms if term in source)
            if hits == 0:
                continue
            excerpt = self._excerpt(note.content, terms)
            score = round(min(0.55 + (hits / len(terms)) * 0.45, 1.0), 2)
            results.append(
                SearchResult(
                    note_id=note.id,
                    note_title=note.title,
                    chunk_text=excerpt,
                    similarity_score=score,
                )
            )
        results.sort(key=lambda item: item.similarity_score, reverse=True)
        return results[:top_k]

    def _excerpt(self, content: str, terms: list[str]) -> str:
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", content) if part.strip()]
        for sentence in sentences:
            lowered = sentence.lower()
            if any(term in lowered for term in terms):
                return sentence
        return content[:240]

