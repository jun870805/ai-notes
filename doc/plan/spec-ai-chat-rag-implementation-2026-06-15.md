# Spec / Plan：AI Chat RAG 實作

> 技術規格與開發計畫

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 功能名稱 | AI Chat RAG 實作 |
| Brief 連結 | [20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) |
| Owner (RD) | TBD |
| 歸屬模組 | AI Notes / Backend AI Chat |
| Spec 日期 | 2026-06-15 |
| Sprint | TBD |
| Review 狀態 | 已實作 |

## 一、需求理解確認

目前專案已完成：

- `notes` CRUD
- chunk / embedding pipeline
- `note_chunks.embedding` 的 `pgvector` schema
- `POST /api/v1/ai/search` 的 Gemini query embedding + pgvector semantic search

目前專案已完成 `POST /api/v1/ai/chat` 的真正 RAG 流程。`/ai/chat` 現在會先檢索相關 `note_chunks`，再把檢索結果作為 context 注入 Gemini chat model；若查無來源，則直接回傳 fallback answer。

這份計畫現在用來記錄本階段的實際落地結果、保留的設計決策，以及後續還沒做的優化項目。

完成標準是：

- `/ai/chat` 已先執行 retrieval，而不是直接用 placeholder answer
- 回答已由 Gemini chat model 生成
- `sources` 已與實際注入 prompt 的檢索內容一致
- 對外 API 的 `sources` 已依 `note_id` 去重，同一篇筆記只保留一筆
- 找不到足夠內容時，已回傳明確 fallback answer
- API response 已維持 `code / success / message / data`

本階段仍不包含：

- 前端 UI 大改版
- 多輪對話記憶
- 對話歷史持久化
- reranking / re-query
- Gemini function calling 或 structured output 強綁定

## 二、技術方案

### 2.1 架構選型

本功能沿用既有 Gemini + PostgreSQL `pgvector` 架構，不新增外部向量資料庫，也不引入獨立 conversation store。

核心技術選擇如下：

- Retrieval：沿用既有 `/ai/search` 背後的 `SearchService`
- Context source：`note_chunks`
- Answer generation：Gemini chat model
- API 出口：沿用 `POST /api/v1/ai/chat`
- Error handling：沿用現有 envelope 與 service exception 模式

選擇這條路的理由：

- `/ai/search` 已打通，`/ai/chat` 可以直接重用 query embedding + pgvector retrieval
- 先讓單輪問答可用，比較符合 MVP 階段價值
- 不增加 conversation persistence，可保持資料結構與 API 簡單

替代方案與取捨：

- 繼續維持 placeholder answer：實作最省，但已無法支撐產品價值
- 先只做 retrieval，不呼叫 LLM：結果可追溯，但不算真正 chat experience
- 直接做多輪對話：體驗更完整，但 scope 明顯超出現在需求

目前實作採：

1. 單輪 QA
2. 先檢索 top-k chunks
3. 將 context 與問題注入 Gemini
4. 回答只基於提供的 sources，不做外部知識延伸

### 2.2 核心流程

#### AI Chat 流程

1. API 收到 `question`、`top_k`
2. 驗證 `question` 非空、`top_k >= 1`
3. 使用 `SearchService` 檢索相關 chunks
4. 若查無來源：
   - 回傳 fallback answer
   - `sources = []`
5. 若有來源：
   - 將依筆記去重後的 `sources` 組成 Gemini chat prompt
   - 呼叫 Gemini chat model
   - 取得 answer
6. 回傳 `answer + sources`

#### Prompt 組裝原則

- system / instruction 要求：
  - 僅根據提供的筆記內容回答
  - 若資訊不足，要明確說明不足
  - 不要捏造未出現在來源中的細節
- user payload 要包含：
  - 原始問題
  - 格式化後的 sources 清單

#### 無資料流程

1. retrieval 結果為空
2. 不呼叫 Gemini chat API
3. 直接回傳：
   - `answer = "沒有足夠的筆記資料可以回答這個問題。"`
   - `sources = []`

#### 失敗處理

- query embedding 失敗：
  - 已沿用既有 `embedding_*` error envelope
- Gemini chat API 失敗：
  - 已補明確 `chat_*` 錯誤碼
- DB 查詢失敗：
  - 仍沿用 `internal_error`

### 2.3 資料模型

本階段不新增資料表，沿用現有 retrieval schema 與 response schema。

#### `note_chunks`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `note_id` | UUID | Yes | 對應來源筆記 |
| `chunk_index` | integer | Yes | chunk 順序 |
| `chunk_text` | text | Yes | 注入 prompt 的主要內容 |
| `embedding` | vector(3072) | Yes | retrieval 依據 |

#### `notes`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | 筆記 ID |
| `title` | text | Yes | 回傳 `note_title` |

#### Response Schema

沿用既有：

- `ChatRequest`
- `ChatResponseData`
- `SearchResult`

本階段不新增 conversation ID 或 message history schema。

### 2.4 API 設計

本階段維持既有 endpoint 與 response contract。

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/ai/chat` | `{ "question": string, "top_k"?: int }` | `{ "answer": string, "sources": SearchResult[] }` |

#### Request

```json
{
  "question": "What do my notes say about FastAPI token validation?",
  "top_k": 3
}
```

#### Response

```json
{
  "code": "success",
  "success": true,
  "message": null,
  "data": {
    "answer": "根據你的筆記，JWT middleware 會先驗證 bearer token，之後才進入 route logic。",
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

#### Chat 錯誤碼建議

- `chat_rate_limited`
- `chat_auth_failed`
- `chat_request_failed`
- `chat_unavailable`
- `chat_response_invalid`

### 2.5 與現有系統整合

- 與 [server/app/routers/ai.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/routers/ai.py) 整合：
  - `chat_with_notes()` 改為呼叫真正的 RAG chat service
- 與 [server/app/services/search_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/search_service.py) 整合：
  - 重用 retrieval 結果
  - 目前使用預設 `dedupe_by_note=True`
- 與 [server/app/services/chat_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/chat_service.py) 整合：
  - 由 placeholder answer 改成 Gemini chat generation
- 與 [server/app/services/embedding_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/embedding_service.py) 整合：
  - 沿用 query embedding
- 與 [doc/api/ai-chat.md](/Users/peter/Documents/work/product/jun870805/ai-notes/doc/api/ai-chat.md) / OpenAPI 整合：
  - 補實際錯誤類型與 fallback 行為

## 三、任務拆解與時間估算

| 子任務 | 預估工時 | 實際工時 | 偏差 | 說明 |
|--------|----------|----------|------|------|
| 盤點現有 `/ai/chat` placeholder 與 contract | 1h | 已完成 | - | 確認前端/文件格式不變 |
| 定義 chat prompt 組裝格式 | 2h | 已完成 | - | system instruction、sources rendering、fallback 規則 |
| 補 Gemini chat service client | 3h | 已完成 | - | 呼叫 chat model、解析回應、處理錯誤 |
| 重構 `ChatService` | 2h | 已完成 | - | 改為 answer generation use case，而非字串拼接 |
| 更新 `/ai/chat` router wiring | 1h | 已完成 | - | 接上真正的 RAG 流程 |
| 撰寫 API tests：`POST /ai/chat` | 3h | 已完成 | - | 驗證 success、no data、chat error |
| 更新 API 文件 / README | 1h | 已完成 | - | 已同步目前行為 |
| 手動驗證真實 Gemini 回答品質 | 2h | 未完成 | - | 尚需用真實資料與問題做人工驗收 |
| **總計** | **15h** | | | |

## 四、生產環境目標

| 指標 | 目前 Baseline | 本次交付目標 |
|------|--------------|-------------|
| 回答可用性 | placeholder answer，無真正 LLM generation | 已切換為基於來源內容的 Gemini 回答；仍需人工驗收品質 |
| 回答可追溯性 | sources 有，但 answer 並非模型生成 | `answer` 與 `sources` 一致，可人工檢查 |
| 延遲 P50 | N/A | ≤ 5s |
| 延遲 P95 | N/A | ≤ 10s |

## 五、風險與相依

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| chat model 對來源約束不夠，產生幻覺 | 中 | answer 不可信 | prompt 明確要求只根據 sources，資訊不足時直接承認 |
| sources 太多或太長導致 prompt 膨脹 | 中 | latency / cost 上升 | 先限制 `top_k` 與 chunk 長度 |
| Gemini chat API quota / rate limit | 中 | `/ai/chat` 不穩定 | 補清楚 `chat_*` 錯誤碼與 fallback |
| retrieval 正確但 answer 摘要品質不佳 | 中 | 使用者體感差 | 先做 MVP prompt，後續再調 prompt 或加 reranking |
| 前端期待單輪 answer，但未來要多輪 | 低 | API 演進成本 | 現階段先維持單輪 contract，後續再擴充 |

**外部相依：**

- Gemini API key、chat model 與 quota
- `/ai/search` retrieval 已可穩定使用
- 幾篇真實技術筆記作為手動驗收樣本

## 六、驗收清單

### 功能驗收

- [x] `POST /api/v1/ai/chat` 已不再使用 placeholder answer generation
- [x] 回答前會先執行 retrieval
- [x] `sources` 與實際注入 prompt 的檢索結果一致
- [x] `sources` 對外回傳時會依 `note_id` 去重
- [x] 找不到來源時回傳 fallback answer 與空 sources
- [x] chat API 失敗時回傳明確 `chat_*` error envelope

### 生產環境驗收

- [ ] 真實 PostgreSQL + Gemini 環境下可回傳合理 answer
- [ ] 回答延遲符合第四節目標
- [ ] 前端 `AI 對話` 頁面可直接顯示真實回答與來源

### 品質驗收

- [ ] Code Review 通過
- [x] 測試覆蓋已補 success / no data / chat error 路徑
- [ ] 靜態分析零 critical issue
