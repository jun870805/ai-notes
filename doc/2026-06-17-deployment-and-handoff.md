# Deployment And Handoff

此文件整理目前 MVP 的啟動、交付、驗收與常見維護操作。

適用情境：

- 第一次在新機器上啟動專案
- 交付給下一位開發者
- demo 前自我檢查
- 本機資料庫或 migration 問題排查

## 系統組成

- `client/`：React + Vite 前端
- `server/`：FastAPI 後端
- `db`：PostgreSQL + pgvector
- `Gemini API`：embeddings / chat / tagging

## 交付前提

本機需具備：

- `Docker Desktop`
- `docker compose`
- `Node.js 20+`
- `npm`
- `Python 3.13`：只有在不走 Docker 啟動 backend 或執行本機測試時需要

## 環境變數

根目錄建立 `.env`，至少包含：

```env
GEMINI_API_KEY=your_real_api_key
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
GEMINI_EMBEDDING_DIMENSIONS=3072
GEMINI_CHAT_MODEL=gemini-3.5-flash
GEMINI_TAG_MODEL=gemini-3.5-flash
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

補充：

- `DATABASE_URL` 在 Docker Compose 啟動 `server` 時已內建，不一定要手動寫在 `.env`
- 若 Gemini key 無效：
  - tagging 會 fallback
  - chat / search / embedding 可能回 provider error

## 第一次啟動

### 1. 啟動資料庫與 backend

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose up --build db server
```

預期：

- `db` healthy
- `server` 啟動前自動執行 `alembic upgrade head`
- `http://127.0.0.1:8000/health` 可回 `success=true`

### 2. 啟動 frontend

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes/client
npm install
npm run dev -- --host 127.0.0.1 --port 5174
```

使用網址：

- Frontend: `http://127.0.0.1:5174/notes`
- Backend: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`

## 日常啟停

### 啟動 backend

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose up db server
```

### 重建 backend image

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose up --build db server
```

### 停止 backend / db

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose down
```

### 清空資料庫重來

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose down -v
docker compose up --build db server
```

注意：

- `down -v` 會刪掉 PostgreSQL volume
- 所有本機 `notes` 與 `note_chunks` 都會消失

## Migration 與資料庫維護

### 檢查 migration

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes/server
alembic current
alembic history
```

### 本機手動執行 migration

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes/server
alembic upgrade head
```

### 查 PostgreSQL 內容

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose exec db psql -U postgres -d ai_notes
```

常用 SQL：

```sql
SELECT id, title, tags, embedding_updated_at
FROM notes
ORDER BY updated_at DESC
LIMIT 10;

SELECT note_id, chunk_index, chunk_text
FROM note_chunks
ORDER BY created_at DESC, chunk_index ASC
LIMIT 20;
```

## 交付驗收

交付前至少確認：

1. `docker compose up --build db server` 可正常啟動
2. `curl http://127.0.0.1:8000/health` 成功
3. `cd client && npm run build` 通過
4. `pytest -q server/tests` 通過
5. 前端可完成：
   - 新增筆記
   - 編輯筆記
   - 刪除筆記
   - AI 搜尋
   - AI 對話
6. 建立筆記後 `note_chunks` 有資料

建議搭配：

- [2026-06-16-manual-acceptance-checklist.md](/Users/peter/Documents/work/product/jun870805/ai-notes/doc/2026-06-16-manual-acceptance-checklist.md)
- [2026-06-16-search-chat-test-cases.md](/Users/peter/Documents/work/product/jun870805/ai-notes/doc/2026-06-16-search-chat-test-cases.md)

## 常見問題

### 1. 前端空白或一直轉圈

先固定前端啟動方式：

```bash
cd client
npm run dev -- --host 127.0.0.1 --port 5174
```

再用：

```text
http://127.0.0.1:5174/notes
```

### 2. CORS 錯誤

檢查 `.env` 的：

```env
CORS_ALLOW_ORIGINS=...
```

修改後重啟 backend container。

### 3. Gemini request failed / rate limited

檢查：

- `GEMINI_API_KEY` 是否有效
- Gemini quota 是否足夠
- backend log 是否出現 `embedding_*` / `chat_*` / `tag_*` 錯誤碼

### 4. 搜尋命中品質不佳

先確認：

- 筆記是否真的有被寫進 `note_chunks`
- `embedding_updated_at` 是否不是 `NULL`
- 問題是否太泛

目前仍是 MVP：

- 檢索為 exact search
- 尚未加入 ANN vector index

## 目前不在交付範圍內

- 正式雲端部署腳本
- CI/CD pipeline
- 監控 / tracing / metrics
- ANN vector index
- production secrets manager

如果之後要進 production，這些需要另外補。
