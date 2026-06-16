# AI Tag API

此文件定義自動產生筆記 tags 的 API。

Base path：`/api/v1`

## POST `/ai/tag`

### Purpose

根據筆記的 `title` 與 `content` 產生 3 至 6 個 tags。

### Request Body

```json
{
  "title": "FastAPI WebSocket streaming response implementation notes",
  "content": "FastAPI WebSocket streaming response implementation notes."
}
```

### Field Rules

| Field | Type | Required | 說明 |
|---|---|---|---|
| `title` | string | Yes | 筆記標題 |
| `content` | string | Yes | 筆記內容 |

## Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "tags": ["fastapi", "websocket", "streaming", "backend"]
  }
}
```

## Business Rules

- tags 數量應為 `3` 至 `6`
- tags 應為小寫英文或 kebab-case
- 同一個 tag 不應重複
- 手動提供給 `POST /notes` / `PUT /notes/{note_id}` 的 tags 也應走相同的 sanitize / dedupe 規則
- 回傳結果可供 `POST /notes` 或 `PUT /notes/{note_id}` 寫回 `notes.tags`
- `POST /notes` / `PUT /notes/{note_id}` 在 request 未提供 `tags` 時，後端可使用同一套邏輯自動產生 tags

## Error Cases

- `400 bad_request`
- `422 validation_error`
- `429 tag_rate_limited`
- `401 tag_auth_failed`
- `503 tag_unavailable`
- `500 tag_request_failed`
- `500 tag_response_invalid`
- `500 internal_error`
