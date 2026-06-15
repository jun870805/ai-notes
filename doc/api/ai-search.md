# AI Search API

此文件定義筆記語意搜尋 API。

Base path：`/api/v1`

## POST `/ai/search`

### Purpose

將自然語言 query 轉為 embedding，並從筆記 chunks 中找出最相關結果。

### Request Body

```json
{
  "query": "How did I wire pgvector for semantic search?",
  "top_k": 5
}
```

### Field Rules

| Field | Type | Required | 說明 |
|---|---|---|---|
| `query` | string | Yes | 自然語言搜尋內容 |
| `top_k` | integer | No | 要回傳的結果數量，MVP 預設 `5` |

## Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "results": [
      {
        "note_id": "550e8400-e29b-41d4-a716-446655440000",
        "note_title": "pgvector Setup",
        "chunk_text": "Enable vector extension in the database init script.",
        "similarity_score": 0.91
      },
      {
        "note_id": "550e8400-e29b-41d4-a716-446655440001",
        "note_title": "Retrieval Notes",
        "chunk_text": "Return Top 5 search results ordered by similarity score.",
        "similarity_score": 0.84
      }
    ]
  }
}
```

## Response Fields

| Field | Type | 說明 |
|---|---|---|
| `results` | SearchResult[] | 命中的結果列表 |

### SearchResult

| Field | Type | 說明 |
|---|---|---|
| `note_id` | UUID | 筆記 ID |
| `note_title` | string | 筆記標題 |
| `chunk_text` | string | 命中的 chunk 內容 |
| `similarity_score` | float | 相似度分數 |

## Business Rules

- `query` 需先轉為 Gemini retrieval query embedding
- 搜尋範圍為 `note_chunks`
- 結果依 cosine distance 由近到遠排序
- `similarity_score` 為對 cosine similarity 做 `0..1` clamp 後的數值
- MVP 預設 Top 5

## Empty Result

若無相關結果，回傳空陣列：

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "results": []
  }
}
```

## Error Cases

- `400 bad_request`
- `422 validation_error`
- `429 embedding_rate_limited`
- `401 embedding_auth_failed`
- `503 embedding_unavailable`
- `500 internal_error`
