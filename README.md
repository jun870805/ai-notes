# AI Engineer Notes

AI Engineer Notes 是一個面向工程師的 AI 筆記與知識檢索系統。現在這個 repo 已經有可執行的 React 前端、FastAPI 後端、PostgreSQL / pgvector 開發環境，以及建立筆記後的 chunk + embedding pipeline。

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
Gemini API
```

## 主要元件

| 元件 | 技術 | 職責 |
|---|---|---|
| Frontend | React, TypeScript, Vite | 筆記管理、搜尋與 AI Chat UI |
| Backend API | FastAPI | API、資料處理、AI workflow |
| Database | PostgreSQL | 儲存 notes 與 metadata |
| Vector Search | pgvector | 儲存與搜尋 note chunks embeddings |
| AI Provider | Gemini API | embeddings、tagging、chat response |
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
- 筆記檢視頁與編輯頁分流
- Markdown editor 與 preview
- AI auto tagging placeholder
- 建立 / 更新筆記後自動切 chunk 並建立 embedding
- AI 搜尋前後端已接通 Gemini query embedding + pgvector search
- AI 對話前後端已接通 retrieval + Gemini RAG answer generation
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
- `GEMINI_API_KEY`
- `GEMINI_EMBEDDING_MODEL`
- `GEMINI_EMBEDDING_DIMENSIONS`
- `GEMINI_CHAT_MODEL`
- `CORS_ALLOW_ORIGINS`

## Local Development

先啟動 backend 與 database：

```bash
docker compose up --build db server
```

再啟動 frontend：

```bash
cd client
npm install
npm run dev -- --host 127.0.0.1 --port 5174
```

建議開啟：

- Frontend: `http://127.0.0.1:5174/notes`
- Backend API: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`

## 目前狀態

- `client` 已經串接 backend API，不再使用本地 mock state 作為主資料來源
- `POST /notes`、`PUT /notes/{note_id}` 會同步重建 `note_chunks`
- 若有設定有效的 `GEMINI_API_KEY`，embedding pipeline 會呼叫 Gemini embeddings
- 若未設定 key，或目前只是跑測試，會退回 deterministic fallback embeddings
- `note_chunks.embedding` 已改成真正的 `pgvector` 欄位
- `/ai/search` 已正式接上 Gemini query embedding + `pgvector` similarity search
- `/ai/search` 目前會以筆記去重，同一篇筆記只顯示最相近的一筆結果
- `/ai/chat` 已正式接上 retrieval + Gemini chat generation；查無資料時會回 fallback answer
- `/ai/chat` 的 `sources` 目前也會以筆記去重，同一篇筆記只保留一筆來源
- 目前尚未加入 ANN vector index；現階段先以可用的向量欄位與查詢能力為主

## 驗證指令

前端：

```bash
cd client
npm run build
```

後端：

```bash
cd server
pytest -q
alembic upgrade head
```

## 文件

- 產品規格：[doc/spec/20260520_AI_Notes_MVP_Product_Spec.md](doc/spec/20260520_AI_Notes_MVP_Product_Spec.md)
- 文件目錄說明：[doc/README.md](doc/README.md)
- 前端說明：[client/README.md](client/README.md)
- 後端說明：[server/README.md](server/README.md)
- Infra 說明：[infra/README.md](infra/README.md)
- Skills 說明：[skills/README.md](skills/README.md)
