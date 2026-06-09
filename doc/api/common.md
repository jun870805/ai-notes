# Common API Conventions

此文件定義 AI 工程筆記 MVP API 的共用規範。

## Base Path

建議 MVP API base path：

```text
/api/v1
```

範例：

```text
GET /api/v1/notes
POST /api/v1/ai/search
```

## Content Type

request / response 統一使用：

```http
Content-Type: application/json
```

## Naming Convention

API 欄位統一使用 `snake_case`。

範例：

- `note_id`
- `created_at`
- `updated_at`
- `similarity_score`

## ID Format

- `note_id`: UUID
- `chunk_id`: UUID

範例：

```text
550e8400-e29b-41d4-a716-446655440000
```

## Datetime Format

時間欄位統一使用 ISO 8601 UTC。

範例：

```text
2026-05-20T09:00:00Z
```

## Response Envelope

所有 API response 統一使用以下格式：

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {}
}
```

欄位規則：

- `code`: API 結果代碼，success 或業務錯誤碼
- `success`: `true` / `false`
- `message`: error 時必填，success 時可為 `null`
- `data`: success 時必填，可為 `string`、`object`、`array`；error 時可為 `null`

## Success Response

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "FastAPI Auth Notes",
    "content": "# FastAPI Auth Notes",
    "tags": ["fastapi", "auth"],
    "created_at": "2026-05-20T09:00:00Z",
    "updated_at": "2026-05-20T09:00:00Z"
  }
}
```

## Error Response

```json
{
  "code": "note_not_found",
  "success": false,
  "message": "Note not found.",
  "data": null
}
```

## Error Codes

建議 MVP 至少支援以下錯誤狀態：

| HTTP Status | Code | 說明 |
|---|---|---|
| 400 | `bad_request` | request 格式錯誤或缺少必要欄位 |
| 404 | `note_not_found` | 查無指定筆記 |
| 409 | `conflict` | 狀態衝突 |
| 422 | `validation_error` | 欄位驗證失敗 |
| 500 | `internal_error` | 未預期錯誤 |

## Data Field Rule

`data` 依 endpoint 可放：

- `object`
- `array`
- `string`
- `null`（僅 error）

## Validation Rules

MVP 建議共用驗證規則：

- `title` 不可為空字串
- `content` 不可為空字串
- `tags` 若提供，需為字串陣列
- `tags` 內容建議使用小寫英文或 kebab-case
- `query` 不可為空字串
- `question` 不可為空字串

## Resource Schemas

### Note

```json
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "tags": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Search Result

```json
{
  "note_id": "uuid",
  "note_title": "string",
  "chunk_text": "string",
  "similarity_score": 0.91
}
```

### Chat Source

`Chat Source` 與 `Search Result` 結構一致。

## Pagination

MVP 的 `GET /notes` 可先不做分頁。

若後續要擴充，建議使用：

- `limit`
- `offset`

## Sorting

`GET /notes` 預設依 `updated_at desc` 排序。

## Auth

MVP spec 目前未定義多使用者或登入機制，因此 API 文件暫不納入 auth header 規範。
