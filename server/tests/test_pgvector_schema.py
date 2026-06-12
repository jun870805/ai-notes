from __future__ import annotations

from sqlalchemy.dialects import postgresql, sqlite

from app.config import settings
from app.models.note_chunk import NoteChunk
from app.repositories.note_repository import NoteRepository


def test_note_chunk_embedding_uses_vector_for_postgresql():
    impl = NoteChunk.__table__.c.embedding.type.dialect_impl(postgresql.dialect())

    assert impl.__class__.__name__ == "VECTOR"


def test_note_chunk_embedding_uses_json_for_sqlite():
    impl = NoteChunk.__table__.c.embedding.type.dialect_impl(sqlite.dialect())

    assert impl.__class__.__name__ == "_SQliteJson"


def test_repository_similarity_search_statement_uses_cosine_distance(session):
    repository = NoteRepository(session)

    query_embedding = [0.1] * settings.gemini_embedding_dimensions
    statement = repository.build_similarity_search_stmt(query_embedding, top_k=5)
    compiled = str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

    assert "ORDER BY" in compiled
    assert "<=>" in compiled
    assert "LIMIT 5" in compiled
