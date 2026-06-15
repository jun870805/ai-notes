# Spec / Plan：AI Search pgvector 實作

> 技術規格與開發計畫

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 功能名稱 | AI Search pgvector 實作 |
| Brief 連結 | [20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) |
| Owner (RD) | TBD |
| 歸屬模組 | AI Notes / Backend AI Search |
| Spec 日期 | 2026-06-12 |
| Sprint | TBD |
| Review 狀態 | 已實作 |

## 一、需求理解確認

目前專案已完成 `notes` CRUD、chunk/embedding pipeline、`note_chunks.embedding` 的 `pgvector` schema 升級，以及 `POST /api/v1/ai/search` 的正式語意搜尋流程。`/ai/search` 現在會先產生 Gemini query embedding，再基於 PostgreSQL `pgvector` cosine distance 從 `note_chunks` 找出最相近的 chunks。

這份計畫現在用來記錄本階段的實際落地結果、保留的設計決策，以及後續還沒做的優化項目。

完成標準是：

- `/ai/search` 已不再依賴 placeholder lexical search
- query 已先轉為 Gemini embedding
- 搜尋來源已改為 `note_chunks`
- 結果已依 similarity 排序並回傳 top-k
- 對外 API 結果已依 `note_id` 去重，同一篇筆記只保留最相近的一筆
- API contract 已與目前前端串接格式保持相容

本階段仍不包含：

- `/ai/chat` 的 RAG answer generation
- `AI tag` 實作
- ANN vector index 優化
- 搜尋結果摘要改寫或 reranking

## 二、技術方案

### 2.1 架構選型

本功能沿用既有的 Gemini embedding 與 PostgreSQL `pgvector` 架構，不引入外部向量資料庫。

核心技術選擇如下：

- Query embedding provider：Gemini embeddings API
- 向量儲存：PostgreSQL `note_chunks.embedding`
- 相似度計算：`pgvector` cosine distance
- 查詢邊界：`NoteRepository.search_similar_chunks`
- API 出口：沿用 `POST /api/v1/ai/search`

選擇這條路的理由：

- `note_chunks` 已是正式檢索資料來源，不需要再從 `notes.content` 臨時切片
- `pgvector` schema 已落地，現在直接接 repository query 風險最低
- 與 `/ai/chat` 後續 RAG 流程共用同一套 retrieval 基礎

替代方案與取捨：

- 繼續使用 lexical search：實作簡單，但和產品 spec 的 semantic search 目標不符
- 外接 Qdrant / 專門向量 DB：可行，但目前會增加額外維運與搬移成本
- 先做 hybrid search：品質可能更好，但現階段先把純 vector search 做通較合理

目前實作採：

1. 純 query embedding + `pgvector` cosine search
2. exact search，不先做 ANN index
3. 若搜尋結果品質不足，再評估 hybrid 或 reranking

### 2.2 核心流程

#### 搜尋流程

1. API 收到 `query`、`top_k`
2. 驗證 `query` 非空、`top_k >= 1`
3. 將 query 格式化為 Gemini retrieval query 文字
   - `task: search result | query: {query}`
4. 呼叫 Gemini embedding API 產生 query embedding
5. 透過 repository 執行 `note_chunks.embedding` cosine distance 查詢
6. 取回 top-k `NoteChunk`
7. 以 cosine similarity 計算對外使用的 `similarity_score`
8. 依 `note_id` 去重，只保留每篇筆記最相近的一筆
9. 組成 `SearchResponseData`
10. 以統一 envelope 回傳

#### 空結果流程

1. query embedding 成功
2. similarity search 沒有命中任何 chunk
3. 回傳 `results: []`
4. `success = true`

#### 失敗處理

- Gemini embedding API 失敗：
  - 已回傳既有 `embedding_*` error envelope
- DB 查詢失敗：
  - 仍由既有 `internal_error` 路徑處理
- query 合法但找不到結果：
  - 已回空陣列，不視為錯誤

### 2.3 資料模型

本階段不新增新表，沿用現有 schema，重點是確認查詢使用欄位。

#### `note_chunks`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | chunk 唯一 ID |
| `note_id` | UUID | Yes | 關聯 `notes.id` |
| `chunk_index` | integer | Yes | chunk 順序 |
| `chunk_text` | text | Yes | 檢索命中內容 |
| `token_count` | integer | No | token 粗估數 |
| `embedding` | vector(3072) | Yes | query similarity search 目標欄位 |
| `created_at` | timestamptz | Yes | 建立時間 |

#### `notes`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | 筆記 ID |
| `title` | text | Yes | 回傳 `note_title` |
| `content` | text | Yes | 不直接作 search，但作為資料來源背景 |
| `tags` | jsonb | No | 本階段不直接使用 |
| `embedding_updated_at` | timestamptz | No | 可輔助檢查向量是否已更新 |

### 2.4 API 設計

本階段維持既有 endpoint 與 response 格式，未改前端 contract。

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/ai/search` | `{ "query": string, "top_k"?: int }` | `{ "results": SearchResult[] }` |

#### Request

```json
{
  "query": "How did I wire pgvector for semantic search?",
  "top_k": 5
}
```

#### Response

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
      }
    ]
  }
}
```

#### `similarity_score` 規則

- 內部 DB 查詢使用 cosine distance
- 對外輸出轉為較直觀的相似度分數
- 目前實作：
  - `similarity_score = clamp(cosine_similarity, 0, 1)`
- 若後續發現 Gemini embedding 實際分布不適合，再調整 normalization

### 2.5 與現有系統整合

- 與 [server/app/routers/ai.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/routers/ai.py) 整合：
  - `search_notes()` 改為呼叫真正的 vector search service
- 與 [server/app/services/search_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/search_service.py) 整合：
  - 已取代 lexical placeholder 邏輯
- 與 [server/app/services/embedding_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/embedding_service.py) 整合：
  - 新增 query embedding 方法，與 document embedding 格式分流
- 與 [server/app/repositories/note_repository.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/repositories/note_repository.py) 整合：
  - 已使用 `search_similar_chunks()`
  - 已在 query statement 中 eager load `Note`
- 與 [doc/api/ai-search.md](/Users/peter/Documents/work/product/jun870805/ai-notes/doc/api/ai-search.md) / OpenAPI 整合：
  - 若行為細節有補充，需同步文件

## 三、任務拆解與時間估算

| 子任務 | 預估工時 | 實際工時 | 偏差 | 說明 |
|--------|----------|----------|------|------|
| 盤點現有 `/ai/search` placeholder 與 contract | 1h | 已完成 | - | 確認 router、schema、前端格式不變 |
| 補 query embedding service 方法 | 2h | 已完成 | - | 新增 Gemini retrieval query 格式化與呼叫 |
| 調整 repository similarity query | 2h | 已完成 | - | 補 join/load note title、排序與 top-k |
| 實作正式 `SearchService` | 3h | 已完成 | - | 串 embedding + repository + response mapping |
| 更新 `/ai/search` router | 1h | 已完成 | - | 改用新 service，保留 envelope |
| 移除 lexical placeholder 邏輯 | 1h | 已完成 | - | 舊邏輯已被取代 |
| 撰寫 API tests：`POST /ai/search` | 3h | 已完成 | - | 驗證 success、empty、embedding error |
| 更新 API 文件 / README | 1h | 已完成 | - | 已同步目前行為 |
| 手動驗證 PostgreSQL 結果合理性 | 2h | 未完成 | - | 尚需用真實資料與 query 做人工驗收 |
| **總計** | **16h** | | | |

## 四、生產環境目標

| 指標 | 目前 Baseline | 本次交付目標 |
|------|--------------|-------------|
| 搜尋正確性 | placeholder lexical search，結果不穩定 | 已切換為 chunk-based semantic search；仍需人工驗收 Top 5 品質 |
| 搜尋延遲 P50 | N/A | ≤ 3s |
| 搜尋延遲 P95 | N/A | ≤ 6s |
| 結果可追溯性 | 只有整篇 note 粗略比對 | 每筆結果可對應 `note_id`、`note_title`、`chunk_text` |

## 五、風險與相依

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| Gemini query embedding 與 document embedding 格式不一致 | 中 | 搜尋品質不穩 | 明確分開 query/document formatting，補測試驗證 |
| cosine distance 轉 similarity score 後數值不直觀 | 中 | 前端顯示分數難理解 | 先採單一 normalization，若需要再調整 |
| 無 ANN index 下資料量增長會拖慢查詢 | 中 | latency 上升 | MVP 先 exact search，後續再做 halfvec/降維優化 |
| repository 回傳 chunk 但未正確帶出 note title | 低 | API contract 不完整 | 已在 query 階段 eager load `notes` |
| embedding API rate limit / quota 問題 | 中 | `/ai/search` 無法穩定回應 | 沿用既有 `EmbeddingServiceError`，先給清楚錯誤 |

**外部相依：**

- Gemini API key 與 embeddings quota
- PostgreSQL `pgvector` 已啟用且 schema 為最新 migration
- 現有 `note_chunks` 已有足夠測試樣本可供手動驗證

## 六、驗收清單

### 功能驗收

- [x] `POST /api/v1/ai/search` 已不再使用 lexical placeholder search
- [x] query 會先轉為 Gemini query embedding
- [x] 搜尋來源為 `note_chunks`
- [x] 回傳結果包含 `note_id`、`note_title`、`chunk_text`、`similarity_score`
- [x] 同一篇筆記若命中多個 chunks，對外結果只保留一筆
- [x] `top_k` 可正常限制回傳筆數
- [x] 查無結果時回傳空陣列而非錯誤
- [x] embedding 失敗時回傳既有錯誤 envelope

### 生產環境驗收

- [ ] 真實 PostgreSQL + pgvector 環境下可查出合理結果
- [ ] 搜尋延遲符合第四節目標
- [ ] 前端 `AI 搜尋` 頁面可直接顯示真實語意搜尋結果

### 品質驗收

- [ ] Code Review 通過
- [x] 測試覆蓋已補 search success / empty / error 路徑
- [ ] 靜態分析零 critical issue
