# Manual Acceptance Checklist

此文件用來驗收目前 MVP 的主要流程：

- Notes CRUD
- AI Auto Tagging
- Embedding Pipeline
- AI Search
- AI Chat

## 啟動環境

Backend:

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes
docker compose up --build db server
```

Frontend:

```bash
cd /Users/peter/Documents/work/product/jun870805/ai-notes/client
npm run dev -- --host 127.0.0.1 --port 5174
```

驗收網址：

- Frontend: `http://127.0.0.1:5174/notes`
- Backend: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`

## 驗收前準備

- `.env` 已設定有效的 `GEMINI_API_KEY`
- backend 已完成 migration
- 瀏覽器 DevTools `Network` 可觀察 API request / response

## A. Notes CRUD

### 建立筆記

- [ ] 進入 `新增筆記`
- [ ] 只輸入 `title` 與 `content`
- [ ] 點擊 `儲存筆記`
- [ ] 成功返回 `筆記列表`
- [ ] 右上角顯示成功提示
- [ ] 列表中出現新筆記
- [ ] Network 可看到 `POST /api/v1/notes`
- [ ] response `success=true`

### 編輯筆記

- [ ] 於列表點 `編輯筆記`
- [ ] 修改標題或內容
- [ ] 點擊 `儲存筆記`
- [ ] 成功返回 `筆記列表`
- [ ] 更新內容已反映在列表 / 詳情
- [ ] Network 可看到 `PUT /api/v1/notes/{note_id}`

### 檢視筆記

- [ ] 於列表點 `檢視筆記`
- [ ] 可看到 Markdown 內容
- [ ] 可看到 tags
- [ ] `編輯筆記` 按鈕可用

### 刪除筆記

- [ ] 於列表點 `刪除筆記`
- [ ] 筆記自列表消失
- [ ] Network 可看到 `DELETE /api/v1/notes/{note_id}`

## B. AI Auto Tagging

### 自動產生 tags

- [ ] 建立筆記時不傳 `tags`
- [ ] 儲存成功後，筆記已有 tags
- [ ] tags 數量介於 `3` 到 `6`
- [ ] tags 為小寫英文或 kebab-case
- [ ] 沒有重複 tags

### 手動 tags 優先

- [ ] 建立筆記時手動輸入 tags
- [ ] 儲存後 tags 仍保留手動值
- [ ] 若手動值含重複或大小寫混用，最終結果會被去重並正規化

### 更新時自動重產

- [ ] 編輯一篇沒有手動 tags 的筆記
- [ ] 修改內容後儲存
- [ ] tags 隨內容變更

## C. Embedding Pipeline

### 建立筆記後生成 chunks

- [ ] 建立一篇較長的筆記
- [ ] backend response 成功
- [ ] 進資料庫查 `note_chunks` 有對應資料
- [ ] `embedding_updated_at` 不為 `NULL`

PostgreSQL 檢查：

```bash
docker compose exec db psql -U postgres -d ai_notes
```

```sql
SELECT id, title, tags, embedding_updated_at
FROM notes
ORDER BY updated_at DESC
LIMIT 5;

SELECT note_id, chunk_index, chunk_text
FROM note_chunks
ORDER BY created_at DESC, chunk_index ASC;
```

## D. AI Search

### 搜尋成功

- [ ] 先建立 2 到 3 篇內容不同的筆記
- [ ] 進 `AI 搜尋`
- [ ] 輸入自然語言 query
- [ ] 點 `搜尋`
- [ ] Network 可看到 `POST /api/v1/ai/search`
- [ ] response `success=true`
- [ ] 畫面有結果時，顯示 `note_title`、`chunk_text`、`similarity_score`

### 搜尋結果規則

- [ ] 同一篇筆記只出現一次
- [ ] 結果與 query 語意大致相關
- [ ] 點擊來源可開啟原筆記

### 空結果

- [ ] 輸入一個明顯無關的 query
- [ ] response 仍為 `success=true`
- [ ] `results=[]`

## E. AI Chat

### 對話成功

- [ ] 進 `AI 對話`
- [ ] 輸入問題
- [ ] 點 `送出問題` 或按 `Enter`
- [ ] Network 可看到 `POST /api/v1/ai/chat`
- [ ] response `success=true`
- [ ] 畫面顯示 `answer`
- [ ] 畫面顯示 `sources`

### 對話規則

- [ ] `sources` 以筆記為單位去重
- [ ] 點擊來源可開啟原筆記
- [ ] 回答內容與來源大致一致

### 無資料 fallback

- [ ] 輸入一個目前筆記完全無關的問題
- [ ] 回傳 `沒有足夠的筆記資料可以回答這個問題。`
- [ ] `sources=[]`

## F. 快捷鍵與輸入行為

### AI Search / AI Chat

- [ ] 空字串時送出按鈕 disabled
- [ ] 送出中按鈕與輸入框 disabled
- [ ] `Enter` 可送出
- [ ] `Cmd + Shift + Enter` 可換行
- [ ] Windows / Linux 可用 `Ctrl + Shift + Enter` 換行

## G. 異常觀察

驗收時同時檢查：

- [ ] Console 無明顯紅字錯誤
- [ ] Network 無意外的 500
- [ ] 後端 log 無未預期 traceback

## 驗收結論

- [ ] Notes CRUD 通過
- [ ] AI Auto Tagging 通過
- [ ] Embedding Pipeline 通過
- [ ] AI Search 通過
- [ ] AI Chat 通過
- [ ] 可以進入下一階段優化
