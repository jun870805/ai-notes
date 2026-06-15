from __future__ import annotations

from sqlalchemy import select

from app.models.note_chunk import NoteChunk
from app.services.chat_service import ChatServiceError
from app.services.embedding_service import EmbeddingServiceError


def test_generate_tags(client):
    response = client.post(
        "/api/v1/ai/tag",
        json={
            "title": "FastAPI WebSocket streaming response implementation notes",
            "content": "FastAPI WebSocket streaming response implementation notes.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["tags"]) >= 3


def test_search_notes_returns_chunk_matches_from_note_chunks(client, session, monkeypatch):
    client.post(
        "/api/v1/notes",
        json={
            "title": "pgvector Setup",
            "content": "# Setup\n\nEnable vector extension in the database init script.\n\nUse cosine distance for retrieval.",
            "tags": ["pgvector", "retrieval", "backend"],
        },
    )
    chunks = list(session.scalars(select(NoteChunk).order_by(NoteChunk.chunk_index)))
    assert len(chunks) == 3

    target_chunk = chunks[1]

    def fake_embed_query(_self, query: str) -> list[float]:
        assert query == "How did I enable pgvector?"
        return target_chunk.embedding

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_query", fake_embed_query)

    response = client.post("/api/v1/ai/search", json={"query": "How did I enable pgvector?", "top_k": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "results" in payload["data"]
    assert payload["data"]["results"][0]["note_title"] == "pgvector Setup"
    assert payload["data"]["results"][0]["chunk_text"] == "Enable vector extension in the database init script."
    assert payload["data"]["results"][0]["similarity_score"] == 1.0


def test_search_notes_returns_empty_results_when_no_chunks_exist(client):
    response = client.post("/api/v1/ai/search", json={"query": "pgvector database", "top_k": 5})

    assert response.status_code == 200
    assert response.json() == {
        "code": "success",
        "success": True,
        "message": None,
        "data": {"results": []},
    }


def test_search_notes_deduplicates_results_by_note(client, session, monkeypatch):
    client.post(
        "/api/v1/notes",
        json={
            "title": "pgvector Setup",
            "content": "# Setup\n\nEnable vector extension.\n\nUse cosine distance for retrieval.",
            "tags": ["pgvector"],
        },
    )
    client.post(
        "/api/v1/notes",
        json={
            "title": "JWT Notes",
            "content": "# Auth\n\nValidate bearer token.\n\nRefresh token rotation notes.",
            "tags": ["auth"],
        },
    )

    chunks = list(session.scalars(select(NoteChunk).order_by(NoteChunk.note_id, NoteChunk.chunk_index)))
    assert len(chunks) >= 4

    note_vectors: dict[str, list[float]] = {}
    for chunk in chunks:
        note_vectors.setdefault(chunk.note_id, chunk.embedding)

    query_embedding = list(note_vectors.values())[0]

    def fake_embed_query(_self, _query: str) -> list[float]:
        return query_embedding

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_query", fake_embed_query)

    response = client.post("/api/v1/ai/search", json={"query": "setup retrieval", "top_k": 5})

    assert response.status_code == 200
    payload = response.json()
    note_ids = [result["note_id"] for result in payload["data"]["results"]]
    assert len(note_ids) == len(set(note_ids))
    assert len(note_ids) == 2


def test_search_notes_returns_embedding_error_when_query_embedding_fails(client, monkeypatch):
    def raise_rate_limited(_self, _query: str):
        raise EmbeddingServiceError("embedding_rate_limited", "Embedding service is rate limited.", 429)

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_query", raise_rate_limited)

    response = client.post("/api/v1/ai/search", json={"query": "pgvector database", "top_k": 5})

    assert response.status_code == 429
    assert response.json() == {
        "code": "embedding_rate_limited",
        "success": False,
        "message": "Embedding service is rate limited.",
        "data": None,
    }


def test_chat_with_notes_returns_model_answer_and_sources(client, session, monkeypatch):
    def fake_gemini_answer(_self, question: str, sources):
        assert question == "What do my notes say about bearer token validation?"
        assert sources
        return "JWT middleware 會先驗證 bearer token，再進入 route logic。"

    client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI Auth Notes",
            "content": "JWT middleware validates bearer token before route logic.",
            "tags": ["fastapi", "auth", "jwt"],
        },
    )
    target_chunk = session.scalars(select(NoteChunk).order_by(NoteChunk.chunk_index)).first()
    assert target_chunk is not None
    monkeypatch.setattr("app.services.chat_service.settings.gemini_api_key", "test-key")
    monkeypatch.setattr("app.services.chat_service.ChatService._gemini_answer", fake_gemini_answer)

    def fake_embed_query(_self, _query: str) -> list[float]:
        return target_chunk.embedding

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_query", fake_embed_query)

    response = client.post(
        "/api/v1/ai/chat",
        json={"question": "What do my notes say about bearer token validation?", "top_k": 3},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["sources"]
    assert payload["data"]["answer"] == "JWT middleware 會先驗證 bearer token，再進入 route logic。"


def test_chat_with_notes_fallback_when_no_data(client):
    response = client.post("/api/v1/ai/chat", json={"question": "kubernetes ingress", "top_k": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["sources"] == []
    assert payload["data"]["answer"] == "沒有足夠的筆記資料可以回答這個問題。"


def test_chat_with_notes_deduplicates_sources_by_note(client, session, monkeypatch):
    def fake_gemini_answer(_self, _question: str, sources):
        assert len({source.note_id for source in sources}) == len(sources)
        return "這是去重後的回答。"

    client.post(
        "/api/v1/notes",
        json={
            "title": "pgvector Setup",
            "content": "# Setup\n\nEnable vector extension.\n\nUse cosine distance for retrieval.",
            "tags": ["pgvector"],
        },
    )
    client.post(
        "/api/v1/notes",
        json={
            "title": "JWT Notes",
            "content": "# Auth\n\nValidate bearer token.\n\nRefresh token rotation notes.",
            "tags": ["auth"],
        },
    )

    chunks = list(session.scalars(select(NoteChunk).order_by(NoteChunk.note_id, NoteChunk.chunk_index)))
    assert len(chunks) >= 4

    note_vectors: dict[str, list[float]] = {}
    for chunk in chunks:
        note_vectors.setdefault(chunk.note_id, chunk.embedding)

    query_embedding = list(note_vectors.values())[0]

    monkeypatch.setattr("app.services.chat_service.settings.gemini_api_key", "test-key")
    monkeypatch.setattr("app.services.chat_service.ChatService._gemini_answer", fake_gemini_answer)

    def fake_embed_query(_self, _query: str) -> list[float]:
        return query_embedding

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_query", fake_embed_query)

    response = client.post("/api/v1/ai/chat", json={"question": "setup retrieval", "top_k": 3})

    assert response.status_code == 200
    payload = response.json()
    note_ids = [source["note_id"] for source in payload["data"]["sources"]]
    assert len(note_ids) == len(set(note_ids))
    assert payload["data"]["answer"] == "這是去重後的回答。"


def test_chat_with_notes_returns_chat_error_when_generation_fails(client, session, monkeypatch):
    def raise_chat_rate_limited(_self, _question: str, _sources):
        raise ChatServiceError("chat_rate_limited", "Chat service is rate limited.", 429)

    client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI Auth Notes",
            "content": "JWT middleware validates bearer token before route logic.",
            "tags": ["fastapi", "auth", "jwt"],
        },
    )
    target_chunk = session.scalars(select(NoteChunk).order_by(NoteChunk.chunk_index)).first()
    assert target_chunk is not None
    monkeypatch.setattr("app.services.chat_service.settings.gemini_api_key", "test-key")
    monkeypatch.setattr("app.services.chat_service.ChatService._gemini_answer", raise_chat_rate_limited)

    def fake_embed_query(_self, _query: str) -> list[float]:
        return target_chunk.embedding

    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_query", fake_embed_query)

    response = client.post(
        "/api/v1/ai/chat",
        json={"question": "What do my notes say about bearer token validation?", "top_k": 3},
    )

    assert response.status_code == 429
    assert response.json() == {
        "code": "chat_rate_limited",
        "success": False,
        "message": "Chat service is rate limited.",
        "data": None,
    }


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "code": "success",
        "success": True,
        "message": None,
        "data": "ok",
    }
