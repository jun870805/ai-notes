# Search / Chat Test Cases

此文件提供一組可直接拿來建立筆記的測試資料，以及建議搜尋詞與預期結果方向。

用途：

- 驗收 `AI Search`
- 驗收 `AI Chat`
- 驗收 `AI Auto Tagging`

## 使用方式

1. 先在前端建立以下筆記
2. 確認每篇筆記都有成功儲存
3. 再用後面的 search / chat query 驗證結果

## 測試資料

### 1. FastAPI Auth Notes

Title:

```text
FastAPI Auth Notes
```

Content:

```md
# FastAPI Auth Notes

## Middleware flow

JWT middleware validates bearer token before route logic.

## Claims

Token payload stores `user_id`, `session_version`, and expiration.

## Failure handling

If token validation fails, the API should return `401 Unauthorized`.
```

預期 tag 方向：

- `fastapi`
- `auth`
- `jwt`
- `middleware`

### 2. pgvector Search Setup

Title:

```text
pgvector Search Setup
```

Content:

```md
# pgvector Search Setup

## Database init

Enable the `vector` extension during PostgreSQL initialization.

## Retrieval rule

Store note chunks in `note_chunks` and search them with cosine distance.

## Product behavior

Even if multiple chunks match, the API should return one result per note.
```

預期 tag 方向：

- `pgvector`
- `retrieval`
- `postgresql`
- `search`

### 3. Flutter Clean Architecture

Title:

```text
Flutter Clean Architecture
```

Content:

```md
# Flutter Clean Architecture

## Layers

Split the app into presentation, domain, and data layers.

## State management

Use Riverpod for dependency injection and state management.

## Testing

Keep use cases pure and test business logic separately from UI widgets.
```

預期 tag 方向：

- `flutter`
- `clean-architecture`
- `riverpod`
- `testing`

### 4. Docker Compose Notes

Title:

```text
Docker Compose Notes
```

Content:

```md
# Docker Compose Notes

## Startup order

Use healthcheck and depends_on so the API starts after PostgreSQL is ready.

## Common issue

If the service cannot connect to the database, verify the compose service name and port.

## Local workflow

Use `docker compose up --build db server` for local backend development.
```

預期 tag 方向：

- `docker`
- `compose`
- `postgresql`
- `backend`

## AI Search 測試案例

### Case 1: FastAPI token 驗證

Query:

```text
我之前怎麼做 bearer token 驗證？
```

預期：

- 第一筆或前幾筆應命中 `FastAPI Auth Notes`
- `chunk_text` 應接近：
  - `JWT middleware validates bearer token before route logic.`
  - 或 `If token validation fails, the API should return 401 Unauthorized.`
- 不應優先命中 Flutter 或 Docker 筆記

### Case 2: pgvector 檢索

Query:

```text
How did I set up pgvector search?
```

預期：

- 應命中 `pgvector Search Setup`
- `chunk_text` 應接近：
  - `Enable the vector extension during PostgreSQL initialization.`
  - 或 `Store note chunks in note_chunks and search them with cosine distance.`
- 結果應只出現一筆 `pgvector Search Setup`

### Case 3: Flutter architecture

Query:

```text
Flutter clean architecture layers
```

預期：

- 應命中 `Flutter Clean Architecture`
- `chunk_text` 應接近：
  - `Split the app into presentation, domain, and data layers.`

### Case 4: Docker 啟動順序

Query:

```text
docker compose database ready healthcheck
```

預期：

- 應命中 `Docker Compose Notes`
- `chunk_text` 應接近：
  - `Use healthcheck and depends_on so the API starts after PostgreSQL is ready.`

### Case 5: 無關內容

Query:

```text
kubernetes ingress controller tls
```

預期：

- 可能回空結果
- 若有結果，也不應高度相關
- 這一題可拿來觀察目前 embedding 品質是否過度擴張

## AI Chat 測試案例

### Case 1: FastAPI Auth 摘要

Question:

```text
我之前在 FastAPI auth 筆記裡記了哪些重點？
```

預期：

- `answer` 應提到：
  - bearer token 驗證
  - token payload 欄位
  - 401 Unauthorized
- `sources` 應包含 `FastAPI Auth Notes`
- `sources` 不應重複出現同一篇筆記

### Case 2: pgvector 產品規則

Question:

```text
搜尋結果為什麼只會回一篇筆記一筆？
```

預期：

- `answer` 應提到：
  - 內部以 chunks 檢索
  - 對外以 note 去重
- `sources` 應包含 `pgvector Search Setup`

### Case 3: Flutter 架構說明

Question:

```text
我的 Flutter clean architecture 筆記有提到哪些分層？
```

預期：

- `answer` 應提到：
  - presentation
  - domain
  - data
- `sources` 應包含 `Flutter Clean Architecture`

### Case 4: Docker 啟動順序

Question:

```text
本機 backend 啟動時，為什麼要等資料庫 ready？
```

預期：

- `answer` 應提到：
  - healthcheck
  - depends_on
  - API 要在 PostgreSQL ready 後啟動
- `sources` 應包含 `Docker Compose Notes`

### Case 5: 無資料 fallback

Question:

```text
我之前怎麼設定 Kubernetes ingress？
```

預期：

- 若目前資料集中沒有相關內容：
  - `answer` 應為 `沒有足夠的筆記資料可以回答這個問題。`
  - `sources = []`

## 額外驗證點

### Search

- [ ] 同一篇筆記不重複出現
- [ ] `similarity_score` 有值
- [ ] 點擊結果可回原筆記

### Chat

- [ ] `sources` 不重複
- [ ] `answer` 和 `sources` 有語意關聯
- [ ] 問題完全無關時有 fallback

### Tags

- [ ] `FastAPI Auth Notes` 有機會產出 `fastapi` / `auth` / `jwt`
- [ ] `pgvector Search Setup` 有機會產出 `pgvector` / `retrieval`
- [ ] `Flutter Clean Architecture` 有機會產出 `flutter` / `clean-architecture`
- [ ] tags 不重複
