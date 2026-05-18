# AI Engineer Notes

AI Engineer Notes 是一個面向工程師的 AI 筆記與知識檢索系統。MVP 目標是讓使用者可以建立 Markdown 技術筆記，系統會自動產生標籤、建立 embedding，並支援語意搜尋與基於筆記內容的 AI 問答。

## 產品目標

- 建立、閱讀、編輯與刪除 Markdown 技術筆記。
- 根據筆記內容自動產生 tags。
- 將筆記內容切成 chunks 並寫入 pgvector。
- 使用自然語言搜尋過去筆記。
- 使用 AI Chat 根據筆記內容回答問題並附上來源。
- 使用 Docker Compose 啟動本機前端、後端與資料庫。

## 技術架構

```text
React client
  |
  | HTTP API
  v
FastAPI server
  |
  | SQLAlchemy / pgvector query
  v
PostgreSQL + pgvector

FastAPI server
  |
  | embeddings / chat / tagging
  v
OpenAI API
```

## 主要元件

| 元件 | 技術 | 職責 |
|---|---|---|
| Frontend | React, TypeScript, Vite | 筆記管理、搜尋與 AI Chat UI |
| Backend API | FastAPI | API、資料處理、AI workflow |
| Database | PostgreSQL | 儲存 notes 與 metadata |
| Vector Search | pgvector | 儲存與搜尋 note chunks embeddings |
| AI Provider | OpenAI API | embeddings、tagging、chat response |
| Local Runtime | Docker Compose | 本機開發環境 |

## 專案結構

```text
ai-notes/
  client/              # React frontend
  server/              # FastAPI backend
  infra/               # Docker、DB init、部署與本機環境輔助檔
  doc/                 # 產品規格、API 文件、架構設計與開發計畫
  skills/              # Codex skills
  services/            # 預留給未來獨立 service 或 worker

  README.md            # 專案總說明
  .env.example         # 環境變數範例
  docker-compose.yml   # 本機整合啟動設定
```

## MVP 功能範圍

- Notes CRUD
- Markdown editor 與 preview
- AI auto tagging
- Embedding pipeline
- Semantic search
- AI chat with citations
- PostgreSQL + pgvector
- Docker Compose local development

## API 範圍

| Method | Path | Description |
|---|---|---|
| GET | `/notes` | 取得筆記列表 |
| GET | `/notes/{note_id}` | 取得單篇筆記 |
| POST | `/notes` | 建立筆記 |
| PUT | `/notes/{note_id}` | 更新筆記 |
| DELETE | `/notes/{note_id}` | 刪除筆記 |
| POST | `/ai/search` | 語意搜尋筆記 |
| POST | `/ai/chat` | 根據筆記回答問題 |
| POST | `/ai/tag` | 根據筆記產生 tags |

## Environment Variables

請參考 `.env.example`。

主要變數：

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_CHAT_MODEL`

## Local Development

預期本機啟動方式：

```bash
docker compose up --build
```

目前此 repo 是專案骨架與文件結構；實際前後端程式碼、migration 與 Docker 設定會依開發進度補上。

## 文件

- 產品規格：[doc/spec/20260520_AI_Notes_MVP_Product_Spec.md](doc/spec/20260520_AI_Notes_MVP_Product_Spec.md)
- 文件目錄說明：[doc/README.md](doc/README.md)
- 前端說明：[client/README.md](client/README.md)
- 後端說明：[server/README.md](server/README.md)
- Infra 說明：[infra/README.md](infra/README.md)
- Skills 說明：[skills/README.md](skills/README.md)
