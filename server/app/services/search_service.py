from __future__ import annotations

from math import sqrt

from app.repositories.note_repository import NoteRepository
from app.schemas.ai import SearchResult
from app.services.embedding_service import EmbeddingService


class SearchService:
    def __init__(
        self,
        note_repository: NoteRepository,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.note_repository = note_repository
        self.embedding_service = embedding_service or EmbeddingService()

    def search_notes(self, query: str, top_k: int) -> list[SearchResult]:
        if not query.strip():
            return []

        query_embedding = self.embedding_service.embed_query(query)
        chunks = self.note_repository.search_similar_chunks(query_embedding, top_k=top_k)

        results: list[SearchResult] = []
        for chunk in chunks:
            similarity_score = self._similarity_score(query_embedding, chunk.embedding)
            results.append(
                SearchResult(
                    note_id=chunk.note_id,
                    note_title=chunk.note.title,
                    chunk_text=chunk.chunk_text,
                    similarity_score=similarity_score,
                )
            )
        return results

    def _similarity_score(self, query_embedding: list[float], chunk_embedding: list[float]) -> float:
        if len(query_embedding) != len(chunk_embedding) or not query_embedding:
            return 0.0

        dot = sum(a * b for a, b in zip(query_embedding, chunk_embedding, strict=True))
        query_norm = sqrt(sum(value * value for value in query_embedding))
        chunk_norm = sqrt(sum(value * value for value in chunk_embedding))
        if query_norm == 0 or chunk_norm == 0:
            return 0.0

        cosine_similarity = dot / (query_norm * chunk_norm)
        cosine_similarity = max(-1.0, min(1.0, cosine_similarity))
        return round(max(0.0, min(1.0, cosine_similarity)), 4)
