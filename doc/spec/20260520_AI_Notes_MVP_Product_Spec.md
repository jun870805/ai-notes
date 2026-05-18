# AI Engineer Notes — MVP Product Specification

## 1. Product Overview

**AI Engineer Notes** 是一個面向工程師的 AI 筆記與知識檢索系統。使用者可以建立 Markdown 技術筆記，系統會自動將筆記內容轉換為可搜尋的語意向量，並讓使用者透過自然語言查詢過去記錄的技術知識。

MVP 版本聚焦於單一使用者的技術筆記管理、AI 語意搜尋、AI 筆記問答與自動標籤功能。

---

## 2. Product Goals

### 2.1 Primary Goals

- 提供 Markdown 筆記建立、編輯、刪除與閱讀功能
- 支援筆記內容的語意搜尋
- 支援根據筆記內容進行 AI 問答
- 自動根據筆記內容產生標籤
- 使用 Docker Compose 建立可本機啟動的開發環境

### 2.2 Success Criteria

MVP 完成後需達成：

- 使用者可以建立並管理 Markdown 筆記
- 新增或更新筆記後，系統會產生 embedding 並儲存至 vector database
- 使用者可以用自然語言搜尋筆記
- AI 回答能引用相關筆記作為回答依據
- 前端可透過 React 操作主要功能
- 後端、資料庫與 pgvector 可透過 Docker Compose 啟動

---

## 3. Target User

### 3.1 Primary User

工程師或技術工作者。

### 3.2 User Needs

- 記錄技術學習內容
- 保存 debug 過程與解法
- 快速查找過去寫過的技術筆記
- 使用 AI 整理分散的筆記內容
- 將技術知識轉換成可查詢的個人知識庫

---

## 4. MVP Feature Scope

## 4.1 Note Management

### Feature Description

使用者可以建立、編輯、刪除與查看 Markdown 筆記。

### Functional Requirements

- 使用者可以建立筆記
- 使用者可以輸入筆記標題
- 使用者可以輸入 Markdown 格式內容
- 使用者可以編輯既有筆記
- 使用者可以刪除既有筆記
- 使用者可以查看筆記列表
- 使用者可以查看單篇筆記內容
- 系統需記錄建立時間與更新時間

### Fields

#### Note

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | 筆記唯一識別碼 |
| title | string | Yes | 筆記標題 |
| content | text | Yes | Markdown 筆記內容 |
| tags | string[] | No | 筆記標籤 |
| created_at | datetime | Yes | 建立時間 |
| updated_at | datetime | Yes | 更新時間 |

---

## 4.2 AI Auto Tagging

### Feature Description

建立或更新筆記後，系統會根據筆記內容自動產生標籤。

### Functional Requirements

- 系統根據筆記 title 與 content 產生 3 至 6 個 tags
- tags 應使用小寫英文或 kebab-case
- tags 會儲存至 notes.tags
- 使用者可以在前端看到自動產生的 tags
- 使用者可以手動編輯 tags

### Example

筆記內容：

```md
FastAPI WebSocket streaming response implementation notes.
```

系統可能產生：

```json
["fastapi", "websocket", "streaming", "backend"]
```

---

## 4.3 Embedding Pipeline

### Feature Description

筆記建立或更新後，系統會將筆記內容切分為 chunks，並產生 embedding 儲存至 pgvector。

### Functional Requirements

- 新增筆記後需產生 chunks
- 更新筆記後需刪除舊 chunks 並重新產生 chunks
- 每個 chunk 需產生 embedding vector
- chunks 需與原始 note 建立關聯
- embedding pipeline 可在 MVP 階段同步執行

### Chunking Rule

MVP 使用簡單文字切分策略：

- 每個 chunk 約 500 至 800 tokens
- chunks 之間保留 50 至 100 tokens overlap
- 每個 chunk 需保存原始 note_id

### Fields

#### NoteChunk

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | chunk 唯一識別碼 |
| note_id | UUID | Yes | 對應筆記 ID |
| chunk_text | text | Yes | chunk 內容 |
| embedding | vector | Yes | embedding 向量 |
| created_at | datetime | Yes | 建立時間 |

---

## 4.4 Semantic Search

### Feature Description

使用者可以輸入自然語言問題，系統會搜尋最相關的筆記 chunks，並回傳相關筆記結果。

### Functional Requirements

- 使用者可以輸入 search query
- 系統會將 query 轉換為 embedding
- 系統會從 note_chunks 搜尋相似 chunks
- 系統需回傳相關 chunks 與對應 note
- 搜尋結果需依相似度排序
- MVP 預設回傳 Top 5 results

### Search Result Fields

| Field | Type | Description |
|---|---|---|
| note_id | UUID | 筆記 ID |
| note_title | string | 筆記標題 |
| chunk_text | string | 命中的 chunk 內容 |
| similarity_score | float | 相似度分數 |

---

## 4.5 AI Chat with Notes

### Feature Description

使用者可以對自己的筆記提問，系統會根據語意搜尋結果組合 context，並透過 LLM 產生回答。

### Functional Requirements

- 使用者可以輸入問題
- 系統需先執行 semantic search
- 系統需將 Top K chunks 注入 prompt context
- AI 回答需基於檢索到的筆記內容
- 回答需包含引用來源
- 若找不到相關內容，系統需明確回覆沒有足夠筆記資料

### Response Format

```json
{
  "answer": "根據你的筆記，你之前在 FastAPI auth 筆記中記錄了 JWT middleware 與 token validation 的做法...",
  "sources": [
    {
      "note_id": "uuid",
      "note_title": "FastAPI Auth Notes",
      "chunk_text": "JWT middleware validates bearer token..."
    }
  ]
}
```

---

## 4.6 React Frontend

### Feature Description

MVP 前端使用 React 實作，提供筆記管理、AI 搜尋與 AI 問答介面。

### Frontend Pages

#### 1. Notes List Page

功能：

- 顯示所有筆記
- 顯示筆記標題
- 顯示 tags
- 顯示 updated_at
- 提供新增筆記入口
- 點擊筆記可進入 detail page

#### 2. Note Detail / Editor Page

功能：

- 顯示筆記標題
- 編輯 Markdown 內容
- 顯示 Markdown preview
- 顯示 tags
- 儲存筆記
- 刪除筆記

#### 3. AI Search Page

功能：

- 輸入自然語言搜尋
- 顯示相關筆記結果
- 顯示命中 chunk
- 點擊結果可開啟原筆記

#### 4. AI Chat Page

功能：

- 輸入問題
- 顯示 AI 回答
- 顯示引用來源
- 點擊來源可開啟原筆記

---

## 5. System Architecture

## 5.1 Architecture Components

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | React | 使用者介面 |
| Backend API | FastAPI | API、AI workflow、資料處理 |
| Database | PostgreSQL | 儲存筆記資料 |
| Vector Search | pgvector | 儲存與搜尋 embedding |
| LLM Provider | OpenAI API | embedding、tagging、chat response |
| Local Runtime | Docker Compose | 本機開發與部署 |

---

## 5.2 High-Level Flow

### Note Creation Flow

```text
User creates note
↓
React sends request to FastAPI
↓
FastAPI stores note in PostgreSQL
↓
FastAPI chunks note content
↓
FastAPI calls embedding API
↓
FastAPI stores chunks + vectors in pgvector
↓
FastAPI calls LLM for auto tags
↓
FastAPI updates note tags
↓
React displays saved note
```

### AI Chat Flow

```text
User asks question
↓
React sends question to FastAPI
↓
FastAPI creates query embedding
↓
FastAPI searches pgvector
↓
FastAPI retrieves top relevant chunks
↓
FastAPI builds prompt context
↓
FastAPI calls LLM
↓
FastAPI returns answer + sources
↓
React displays answer and citations
```

---

## 6. API Specification

## 6.1 Notes API

### GET /notes

Returns all notes.

#### Response

```json
[
  {
    "id": "uuid",
    "title": "FastAPI Auth Notes",
    "content": "Markdown content",
    "tags": ["fastapi", "auth", "jwt"],
    "created_at": "2026-05-13T10:00:00Z",
    "updated_at": "2026-05-13T10:00:00Z"
  }
]
```

---

### GET /notes/{note_id}

Returns a single note.

---

### POST /notes

Creates a new note.

#### Request

```json
{
  "title": "FastAPI Auth Notes",
  "content": "# JWT Auth\n..."
}
```

#### Response

```json
{
  "id": "uuid",
  "title": "FastAPI Auth Notes",
  "content": "# JWT Auth\n...",
  "tags": ["fastapi", "auth", "jwt"],
  "created_at": "2026-05-13T10:00:00Z",
  "updated_at": "2026-05-13T10:00:00Z"
}
```

---

### PUT /notes/{note_id}

Updates a note.

#### Request

```json
{
  "title": "Updated Title",
  "content": "Updated markdown content",
  "tags": ["fastapi", "backend"]
}
```

---

### DELETE /notes/{note_id}

Deletes a note and associated chunks.

---

## 6.2 AI API

### POST /ai/search

Performs semantic search over notes.

#### Request

```json
{
  "query": "我之前怎麼做 JWT auth？",
  "top_k": 5
}
```

#### Response

```json
{
  "results": [
    {
      "note_id": "uuid",
      "note_title": "FastAPI Auth Notes",
      "chunk_text": "JWT middleware validates bearer token...",
      "similarity_score": 0.86
    }
  ]
}
```

---

### POST /ai/chat

Answers a question based on notes.

#### Request

```json
{
  "question": "我之前怎麼做 JWT auth？",
  "top_k": 5
}
```

#### Response

```json
{
  "answer": "你之前的筆記中提到使用 JWT middleware 驗證 bearer token...",
  "sources": [
    {
      "note_id": "uuid",
      "note_title": "FastAPI Auth Notes",
      "chunk_text": "JWT middleware validates bearer token..."
    }
  ]
}
```

---

### POST /ai/tag

Generates tags for a note.

#### Request

```json
{
  "title": "FastAPI WebSocket Streaming",
  "content": "Notes about implementing streaming response..."
}
```

#### Response

```json
{
  "tags": ["fastapi", "websocket", "streaming", "backend"]
}
```

---

## 7. Database Schema

## 7.1 notes

```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 7.2 note_chunks

```sql
CREATE TABLE note_chunks (
    id UUID PRIMARY KEY,
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 8. Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_notes
OPENAI_API_KEY=your_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4.1-mini
```

---

## 9. Docker Compose Scope

Services:

- frontend
- backend
- db

### Expected Commands

```bash
docker compose up --build
```

---

## 10. Frontend Technical Requirements

### Recommended Stack

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS
- Markdown renderer

### Frontend State

- Server state managed by TanStack Query
- Local editor state managed by React state
- API client isolated in `/src/api`

### Suggested Folder Structure

```text
frontend/
  src/
    api/
      notes.ts
      ai.ts
    components/
      MarkdownEditor.tsx
      MarkdownPreview.tsx
      NoteCard.tsx
      SourceList.tsx
    pages/
      NotesListPage.tsx
      NoteEditorPage.tsx
      AISearchPage.tsx
      AIChatPage.tsx
    routes/
      index.tsx
    App.tsx
```

---

## 11. Backend Technical Requirements

### Recommended Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector
- OpenAI SDK

### Suggested Folder Structure

```text
backend/
  app/
    main.py
    config.py
    database.py
    models/
      note.py
      note_chunk.py
    schemas/
      note.py
      ai.py
    routers/
      notes.py
      ai.py
    services/
      note_service.py
      embedding_service.py
      rag_service.py
      tagging_service.py
    repositories/
      note_repository.py
      chunk_repository.py
```

---

## 12. MVP Acceptance Criteria

### Product Acceptance

- 使用者可以從 React 前端建立 Markdown 筆記
- 使用者可以查看、編輯、刪除筆記
- 系統可以自動產生 tags
- 系統可以將筆記切 chunk 並建立 embedding
- 使用者可以用自然語言搜尋筆記
- 使用者可以透過 AI Chat 根據筆記內容取得回答
- AI 回答會附上來源筆記
- Docker Compose 可成功啟動完整系統

### Engineering Acceptance

- Backend API 有清楚 router / service / repository 分層
- PostgreSQL schema 可透過 migration 建立
- pgvector 可正常進行 similarity search
- OpenAI API key 透過 environment variables 管理
- README 包含系統架構、啟動方式與 API 說明

---

## 13. Resume Description

完成 MVP 後可於履歷描述：

> 開發 AI 工程筆記系統，使用 React、FastAPI、PostgreSQL/pgvector 與 OpenAI API 建立個人技術知識庫。系統支援 Markdown 筆記管理、AI 自動標籤、語意搜尋與 RAG 問答，並透過 Docker Compose 完成本機部署環境。專案實作 embedding pipeline、chunking strategy、vector similarity search 與 LLM context injection，用於提升工程知識檢索與技術筆記整理效率。

---

## 14. Future Enhancements

- 使用者登入與多帳號
- Redis queue 處理 embedding pipeline
- SSE streaming response
- Workspace / Project 分類
- Daily digest
- Git commit summary
- GitHub issue / PR summary
- AI TODO generation
- Observability dashboard
- Token usage tracking
