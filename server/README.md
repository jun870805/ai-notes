# Server

`server/` 是 AI Engineer Notes 的 FastAPI 後端。它負責 notes API、AI tagging、embedding pipeline、semantic search 與 RAG chat workflow。

## 目標

- 提供 notes CRUD API。
- 管理 PostgreSQL / pgvector 資料存取。
- 在筆記建立或更新後產生 tags。
- 將筆記切成 chunks 並產生 embeddings。
- 搜尋最相關的 chunks。
- 組合 context 並呼叫 LLM 產生回答與引用來源。

## 建議結構

```text
server/
  app/
    main.py
    config.py
    database.py
    models/          # SQLAlchemy models
    schemas/         # Pydantic request/response schemas
    routers/         # FastAPI routers
    services/        # business logic 與 AI workflow
    repositories/    # database access layer
  alembic/           # database migrations
  tests/             # backend tests
```

## 分層責任

| Layer | Responsibility |
|---|---|
| `routers/` | HTTP request/response、status code、dependency wiring |
| `schemas/` | request/response validation 與序列化 |
| `services/` | use case、AI workflow、chunking、tagging、RAG |
| `repositories/` | SQLAlchemy query 與資料存取 |
| `models/` | database table mapping |

## 核心服務

建議服務：

- `note_service.py`
- `embedding_service.py`
- `rag_service.py`
- `tagging_service.py`

## Database

MVP 主要資料表：

- `notes`
- `note_chunks`

`note_chunks.embedding` 使用 pgvector 型別，維度需與 `OPENAI_EMBEDDING_MODEL` 輸出一致。

目前 Phase 1 已接好：

- PostgreSQL via Docker Compose
- Alembic migration on startup
- `notes`
- `note_chunks`

## API Scope

- `GET /notes`
- `GET /notes/{note_id}`
- `POST /notes`
- `PUT /notes/{note_id}`
- `DELETE /notes/{note_id}`
- `POST /ai/search`
- `POST /ai/chat`
- `POST /ai/tag`

## Local Development

安裝依賴：

```bash
cd server
python3 -m pip install -e '.[dev]'
```

本機直接啟動 API：

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

如果要走 Docker Compose：

```bash
docker compose up --build db server
```

啟動後可用：

- API: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

## 開發注意事項

- OpenAI API key 只能透過環境變數讀取。
- 新增或更新 note 時，MVP 可同步執行 tagging 與 embedding pipeline。
- 更新 note 時，應刪除舊 chunks 後重新建立 chunks。
- 刪除 note 時，相關 chunks 應透過 FK cascade 或 repository 邏輯一併刪除。
- AI chat 若找不到相關內容，應明確回覆沒有足夠筆記資料。
