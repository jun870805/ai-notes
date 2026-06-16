from __future__ import annotations


def test_create_and_get_note(client):
    create_response = client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI Auth Notes",
            "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
            "tags": ["fastapi", "auth"],
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["success"] is True
    assert created["code"] == "success"
    assert created["message"] is None
    assert created["data"]["title"] == "FastAPI Auth Notes"

    note_id = created["data"]["id"]
    get_response = client.get(f"/api/v1/notes/{note_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["success"] is True
    assert fetched["data"]["id"] == note_id


def test_create_note_deduplicates_manual_tags(client):
    create_response = client.post(
        "/api/v1/notes",
        json={
            "title": "Flutter Clean Notes",
            "content": "Clean architecture notes for Flutter.",
            "tags": ["flutter", "clean", "flutter", "Clean", "clean-architecture"],
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["data"]["tags"] == ["flutter", "clean", "clean-architecture"]


def test_create_note_auto_generates_tags_when_missing(client, monkeypatch):
    monkeypatch.setattr("app.services.tagging_service.settings.gemini_api_key", "test-key")

    def fake_gemini_tags(_self, title: str, content: str) -> list[str]:
        assert title == "FastAPI Auth Notes"
        assert "JWT middleware" in content
        return ["FastAPI", "Bearer Token", "Backend"]

    def fake_embed_documents(_self, _title: str, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 12 for _ in texts]

    monkeypatch.setattr("app.services.tagging_service.TaggingService._gemini_tags", fake_gemini_tags)
    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_documents", fake_embed_documents)

    create_response = client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI Auth Notes",
            "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["data"]["tags"] == ["fastapi", "bearer-token", "backend"]


def test_create_note_falls_back_to_rule_tags_when_auto_tag_generation_fails(client, monkeypatch):
    monkeypatch.setattr("app.services.tagging_service.settings.gemini_api_key", "test-key")

    def raise_tag_failure(_self, _title: str, _content: str) -> list[str]:
        from app.services.tagging_service import TaggingServiceError

        raise TaggingServiceError("tag_rate_limited", "Tag service is rate limited.", 429)

    def fake_embed_documents(_self, _title: str, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 12 for _ in texts]

    monkeypatch.setattr("app.services.tagging_service.TaggingService._gemini_tags", raise_tag_failure)
    monkeypatch.setattr("app.services.embedding_service.EmbeddingService.embed_documents", fake_embed_documents)

    create_response = client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI Auth Notes",
            "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
        },
    )

    assert create_response.status_code == 201
    tags = create_response.json()["data"]["tags"]
    assert "fastapi" in tags
    assert "auth" in tags
    assert len(tags) >= 3


def test_list_notes_returns_envelope(client):
    client.post(
        "/api/v1/notes",
        json={"title": "A", "content": "Alpha content", "tags": ["alpha", "notes", "test"]},
    )
    response = client.get("/api/v1/notes")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) == 1


def test_update_note(client):
    created = client.post(
        "/api/v1/notes",
        json={"title": "Old", "content": "Old content", "tags": ["old", "content", "test"]},
    ).json()
    note_id = created["data"]["id"]

    response = client.put(
        f"/api/v1/notes/{note_id}",
        json={"title": "New", "content": "New content", "tags": ["new", "content", "test"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["title"] == "New"


def test_update_note_deduplicates_manual_tags(client):
    created = client.post(
        "/api/v1/notes",
        json={"title": "Old", "content": "Old content", "tags": ["old", "content", "test"]},
    ).json()
    note_id = created["data"]["id"]

    response = client.put(
        f"/api/v1/notes/{note_id}",
        json={
            "title": "New",
            "content": "New content",
            "tags": ["flutter", "clean", "flutter", "Clean", "clean-architecture"],
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["tags"] == ["flutter", "clean", "clean-architecture"]


def test_delete_note(client):
    created = client.post(
        "/api/v1/notes",
        json={"title": "Delete", "content": "Delete content", "tags": ["delete", "content", "test"]},
    ).json()
    note_id = created["data"]["id"]

    response = client.delete(f"/api/v1/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["data"] == "note deleted"


def test_note_not_found_returns_error_envelope(client):
    response = client.get("/api/v1/notes/missing")
    assert response.status_code == 404
    payload = response.json()
    assert payload == {
        "code": "note_not_found",
        "success": False,
        "message": "Note not found.",
        "data": None,
    }
