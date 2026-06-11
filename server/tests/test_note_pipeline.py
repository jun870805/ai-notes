from __future__ import annotations

from sqlalchemy import select

from app.models.note_chunk import NoteChunk
from app.services.chunking_service import chunk_markdown
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError


def test_chunk_markdown_splits_content_into_ordered_chunks():
    content = "# API\n\nJWT middleware validates bearer token.\n\npgvector stores embeddings for note search."

    chunks = chunk_markdown(content, max_chars=80)

    assert len(chunks) == 3
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert chunks[0].chunk_text == "# API"
    assert chunks[1].chunk_text == "JWT middleware validates bearer token."
    assert chunks[2].chunk_text == "pgvector stores embeddings for note search."
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_create_note_builds_note_chunks(client, session):
    response = client.post(
        "/api/v1/notes",
        json={
            "title": "Pipeline Note",
            "content": "# API\n\nJWT middleware validates bearer token.\n\npgvector stores embeddings.",
            "tags": ["api", "search"],
        },
    )

    assert response.status_code == 201
    note_id = response.json()["data"]["id"]

    chunks = list(session.scalars(select(NoteChunk).where(NoteChunk.note_id == note_id).order_by(NoteChunk.chunk_index)))
    assert len(chunks) == 3
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert chunks[0].chunk_text == "# API"
    assert chunks[1].embedding is not None
    assert len(chunks[1].embedding) > 0


def test_update_note_replaces_existing_note_chunks(client, session):
    created = client.post(
        "/api/v1/notes",
        json={
            "title": "Original",
            "content": "# API\n\nJWT middleware validates bearer token.\n\npgvector stores embeddings.",
            "tags": ["api", "search"],
        },
    ).json()
    note_id = created["data"]["id"]

    update_response = client.put(
        f"/api/v1/notes/{note_id}",
        json={
            "title": "Updated",
            "content": "# Updated\n\nA single replacement paragraph.",
            "tags": ["updated"],
        },
    )

    assert update_response.status_code == 200

    chunks = list(session.scalars(select(NoteChunk).where(NoteChunk.note_id == note_id).order_by(NoteChunk.chunk_index)))
    assert len(chunks) == 2
    assert [chunk.chunk_text for chunk in chunks] == ["# Updated", "A single replacement paragraph."]
    assert [chunk.chunk_index for chunk in chunks] == [0, 1]


def test_create_note_returns_meaningful_error_when_embedding_is_rate_limited(client, monkeypatch):
    def raise_rate_limited(_self, _texts):
        raise EmbeddingServiceError("embedding_rate_limited", "Embedding service is rate limited.", 429)

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_texts", raise_rate_limited)

    response = client.post(
        "/api/v1/notes",
        json={
            "title": "Pipeline Note",
            "content": "# API\n\nJWT middleware validates bearer token before route logic.",
            "tags": ["api", "search"],
        },
    )

    assert response.status_code == 429
    assert response.json() == {
        "code": "embedding_rate_limited",
        "success": False,
        "message": "Embedding service is rate limited.",
        "data": None,
    }


def test_embedding_service_formats_documents_for_gemini_retrieval():
    service = EmbeddingService(api_key=None, model="gemini-embedding-2")

    formatted = service._format_document_for_retrieval("FastAPI Auth", "JWT middleware validates bearer token.")

    assert formatted == "title: FastAPI Auth | text: JWT middleware validates bearer token."
