# AI Chat API

此文件定義根據筆記內容回答問題的 API。

Base path：`/api/v1`

## POST `/ai/chat`

### Purpose

先執行 semantic search，再把檢索結果作為 context 注入 LLM，產生帶引用來源的回答。

### Request Body

```json
{
  "question": "What do my notes say about FastAPI token validation?",
  "top_k": 3
}
```

### Field Rules

| Field | Type | Required | 說明 |
|---|---|---|---|
| `question` | string | Yes | 使用者問題 |
| `top_k` | integer | No | 要注入 prompt 的結果數量，MVP 可預設 `3` |

## Response `200 OK`

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "answer": "根據你的筆記，你之前記錄了 JWT middleware 會先驗證 bearer token，token payload 會保存 user id 與 session version。",
    "sources": [
      {
        "note_id": "550e8400-e29b-41d4-a716-446655440000",
        "note_title": "FastAPI Auth Notes",
        "chunk_text": "JWT middleware validates bearer token before route logic.",
        "similarity_score": 0.93
      }
    ]
  }
}
```

## Response Fields

| Field | Type | 說明 |
|---|---|---|
| `answer` | string | AI 回答 |
| `sources` | SearchResult[] | 本次引用來源 |

## Business Rules

- 回答前需先執行 `semantic search`
- `sources` 應對應實際注入 prompt 的檢索結果
- 回答需明確基於檢索內容，不應憑空擴寫
- `sources` 對外回傳時，會依 `note_id` 去重，同一篇筆記只保留最相近的一筆來源
- 若 `sources` 為空，直接回傳 fallback answer，不呼叫 chat model

## No Data Case

若找不到足夠相關內容，回傳：

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "answer": "沒有足夠的筆記資料可以回答這個問題。",
    "sources": []
  }
}
```

## Error Cases

- `400 bad_request`
- `422 validation_error`
- `429 embedding_rate_limited`
- `401 embedding_auth_failed`
- `503 embedding_unavailable`
- `429 chat_rate_limited`
- `401 chat_auth_failed`
- `503 chat_unavailable`
- `500 chat_request_failed`
- `500 internal_error`
