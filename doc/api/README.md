# API Documentation

此目錄放 AI 工程筆記的 API contract、request/response 範例、錯誤格式與後續 OpenAPI 規格來源。

目前先以 MVP 為範圍，依照 [doc/spec/20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) 規劃。

## 文件目標

- 讓前後端對 API 邊界有同一份定義
- 明確定義 request / response 格式
- 明確定義錯誤格式與 status code
- 作為後續 OpenAPI / Swagger 文件的基礎來源

## 建議拆分

```text
doc/api/
  README.md           # API 文件總覽、命名規則、端點矩陣
  openapi.yaml        # Swagger / OpenAPI 規格
  common.md           # 共用格式、欄位命名、錯誤格式、分頁與時間格式
  notes.md            # Notes CRUD API
  ai-search.md        # Semantic Search API
  ai-chat.md          # AI Chat with Notes API
  ai-tag.md           # AI Tag API
```

## MVP 端點矩陣

| Method | Path | 文件檔案 | 說明 |
|---|---|---|---|
| GET | `/notes` | `notes.md` | 取得筆記列表 |
| GET | `/notes/{note_id}` | `notes.md` | 取得單篇筆記 |
| POST | `/notes` | `notes.md` | 建立筆記 |
| PUT | `/notes/{note_id}` | `notes.md` | 更新筆記 |
| DELETE | `/notes/{note_id}` | `notes.md` | 刪除筆記 |
| POST | `/ai/search` | `ai-search.md` | 語意搜尋筆記 chunks |
| POST | `/ai/chat` | `ai-chat.md` | 根據筆記內容回答問題 |
| POST | `/ai/tag` | `ai-tag.md` | 根據 title 與 content 產生 tags |

## 每份 API 文件建議章節

每個 endpoint 文件建議固定使用以下結構，避免不同檔案寫法漂移：

1. Endpoint Summary
2. Request Method / Path
3. Purpose
4. Request Headers
5. Path Parameters
6. Query Parameters
7. Request Body Schema
8. Response Body Schema
9. Success Example
10. Error Cases
11. Notes / Business Rules

## 共用規範

建議先在 `common.md` 定義以下內容，後續各 API 文件直接引用：

- Base URL
  - 本機開發可先用 `/api/v1`
- Content Type
  - `application/json`
- 欄位命名
  - API 欄位統一使用 `snake_case`
- 時間格式
  - 使用 ISO 8601 UTC，例如 `2026-05-20T09:00:00Z`
- ID 格式
  - `UUID`
- 錯誤格式
  - 統一 success / error 結構，避免每個 endpoint 自訂

## 建議錯誤回應格式

```json
{
  "error": {
    "code": "note_not_found",
    "message": "Note not found.",
    "details": null
  }
}
```

建議至少定義這幾類錯誤：

- `400 Bad Request`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `500 Internal Server Error`

## 各文件應包含的重點

### `notes.md`

- `Note` schema
- 建立 / 更新時 `tags` 是否可選填
- 列表是否需要排序與預設排序方式
- 刪除後回應格式
- 建立 / 更新後是否同步觸發 tagging 與 embedding pipeline

### `ai-search.md`

- request body 至少包含 `query`
- 是否支援 `top_k`
- response 應包含：
  - `note_id`
  - `note_title`
  - `chunk_text`
  - `similarity_score`
- 預設 Top 5 結果

### `ai-chat.md`

- request body 至少包含 `question`
- 是否支援 `top_k`
- response 應包含：
  - `answer`
  - `sources`
- `sources` 內容應與 search result schema 對齊
- 查無資料時的回覆規則

### `ai-tag.md`

- request body 至少包含：
  - `title`
  - `content`
- response 應返回 `tags`
- tags 規則：
  - 3 至 6 個
  - 小寫英文或 kebab-case

## 建議撰寫順序

1. `common.md`
2. `notes.md`
3. `ai-search.md`
4. `ai-chat.md`
5. `ai-tag.md`

這個順序的原因是 `ai-search`、`ai-chat`、`ai-tag` 都會依賴前面定義的共用欄位與 note schema。

## 下一步建議

目前已補出文字版 API 文件與 `openapi.yaml`。

你可以直接把 [openapi.yaml](/Users/peter/Documents/work/product/jun870805/ai-notes/doc/api/openapi.yaml) 貼到以下工具 review：

- Swagger Editor
- Redocly
- Stoplight

如果要開始實作文件，我建議下一步直接 review 以下檔案：

- `doc/api/openapi.yaml`
- `doc/api/common.md`
- `doc/api/notes.md`
- `doc/api/ai-search.md`
- `doc/api/ai-chat.md`
- `doc/api/ai-tag.md`

下一步若你確認 Swagger 結構沒問題，我可以再幫你做：

- 補齊更細的 error code matrix
- 補 query/path/body validation 規則
- 對齊未來 FastAPI router / schema 命名
- 產出 JSON 版 OpenAPI
