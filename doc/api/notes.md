# Notes API

此文件定義筆記 CRUD API。

Base path：`/api/v1`

## Note Schema

```json
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "tags": ["string"],
  "created_at": "2026-05-20T09:00:00Z",
  "updated_at": "2026-05-20T09:00:00Z"
}
```

## GET `/notes`

### Purpose

取得筆記列表。

### Query Parameters

MVP 先不提供 query parameters。

### Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "FastAPI Auth Notes",
      "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
      "tags": ["fastapi", "auth", "backend"],
      "created_at": "2026-05-20T09:00:00Z",
      "updated_at": "2026-05-27T08:15:00Z"
    }
  ]
}
```

### Business Rules

- 預設依 `updated_at desc` 排序
- MVP 不做分頁

## GET `/notes/{note_id}`

### Purpose

取得單篇筆記。

### Path Parameters

| Name | Type | Required | 說明 |
|---|---|---|---|
| `note_id` | UUID | Yes | 筆記 ID |

### Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "FastAPI Auth Notes",
    "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
    "tags": ["fastapi", "auth", "backend"],
    "created_at": "2026-05-20T09:00:00Z",
    "updated_at": "2026-05-27T08:15:00Z"
  }
}
```

### Error Cases

- `404 note_not_found`

## POST `/notes`

### Purpose

建立新筆記。

### Request Body

```json
{
  "title": "FastAPI Auth Notes",
  "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
  "tags": ["fastapi", "auth", "backend"]
}
```

### Field Rules

| Field | Type | Required | 說明 |
|---|---|---|---|
| `title` | string | Yes | 筆記標題 |
| `content` | string | Yes | Markdown 內容 |
| `tags` | string[] | No | 可手動提供 tags |

### Response `201 Created`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "FastAPI Auth Notes",
    "content": "# FastAPI Auth Notes\n\nJWT middleware validates bearer token.",
    "tags": ["fastapi", "auth", "backend"],
    "created_at": "2026-05-20T09:00:00Z",
    "updated_at": "2026-05-20T09:00:00Z"
  }
}
```

### Business Rules

- 若 `tags` 未提供，可由後端自動產生
- 建立成功後應同步觸發：
  - auto tagging
  - embedding pipeline

### Error Cases

- `400 bad_request`
- `422 validation_error`

## PUT `/notes/{note_id}`

### Purpose

更新既有筆記。

### Path Parameters

| Name | Type | Required | 說明 |
|---|---|---|---|
| `note_id` | UUID | Yes | 筆記 ID |

### Request Body

```json
{
  "title": "FastAPI Auth Notes Updated",
  "content": "# FastAPI Auth Notes\n\nUpdated content.",
  "tags": ["fastapi", "auth", "jwt"]
}
```

### Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "FastAPI Auth Notes Updated",
    "content": "# FastAPI Auth Notes\n\nUpdated content.",
    "tags": ["fastapi", "auth", "jwt"],
    "created_at": "2026-05-20T09:00:00Z",
    "updated_at": "2026-05-27T08:15:00Z"
  }
}
```

### Business Rules

- 更新後需刪除舊 chunks 並重新建立 embeddings
- 若 `tags` 未提供，可重新自動產生

### Error Cases

- `404 note_not_found`
- `422 validation_error`

## DELETE `/notes/{note_id}`

### Purpose

刪除筆記。

### Path Parameters

| Name | Type | Required | 說明 |
|---|---|---|---|
| `note_id` | UUID | Yes | 筆記 ID |

### Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": "note deleted"
}
```

### Business Rules

- 刪除 note 時，應一併刪除關聯的 note chunks

### Error Cases

- `404 note_not_found`
