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
- 回傳結果可供 `POST /notes` 或 `PUT /notes/{note_id}` 寫回 `notes.tags`

## Error Cases

- `400 bad_request`
- `422 validation_error`
- `500 internal_error`
