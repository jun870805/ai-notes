from __future__ import annotations


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


def test_search_notes(client):
    client.post(
        "/api/v1/notes",
        json={
            "title": "pgvector Setup",
            "content": "Enable vector extension in the database init script.",
            "tags": ["pgvector", "retrieval", "backend"],
        },
    )
    response = client.post("/api/v1/ai/search", json={"query": "pgvector database", "top_k": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "results" in payload["data"]
    assert payload["data"]["results"][0]["note_title"] == "pgvector Setup"


def test_chat_with_notes_returns_sources(client):
    client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI Auth Notes",
            "content": "JWT middleware validates bearer token before route logic.",
            "tags": ["fastapi", "auth", "jwt"],
        },
    )
    response = client.post(
        "/api/v1/ai/chat",
        json={"question": "What do my notes say about bearer token validation?", "top_k": 3},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["sources"]
    assert "回答" in payload["data"]["answer"] or "根據" in payload["data"]["answer"]


def test_chat_with_notes_fallback_when_no_data(client):
    response = client.post("/api/v1/ai/chat", json={"question": "kubernetes ingress", "top_k": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["sources"] == []
    assert payload["data"]["answer"] == "沒有足夠的筆記資料可以回答這個問題。"


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "code": "success",
        "success": True,
        "message": None,
        "data": "ok",
    }
