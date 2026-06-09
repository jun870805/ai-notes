# Spec / Plan：AI 工程筆記 MVP Phase 1

> 技術規格與開發計畫

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 功能名稱 | AI 工程筆記 MVP Phase 1 |
| Brief 連結 | [20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) |
| Owner (RD) | TBD |
| 歸屬模組 | AI Notes / Backend API |
| Spec 日期 | 2026-06-08 |
| Sprint | TBD |
| Review 狀態 | 草稿 |

## 一、需求理解確認

本階段先完成 AI 工程筆記 MVP 的後端第一段基礎能力，目標不是一次做完整產品，而是先把後端核心邊界立起來，讓前後端可以開始接真實 API。範圍只包含三個部分：

1. 後端資料模型與 schema
2. Notes CRUD API
3. AI Tag / Search / Chat API

完成標準是：

- 後端有明確的資料模型與 request / response schema
- Notes CRUD API 可供前端改接真實資料
- AI 相關 API contract 明確，並可先用 stub / placeholder service 回傳結構正確的資料
- API 文件與 Swagger 已能作為後續實作依據

本階段先不包含：

- 真實 OpenAI 串接
- embedding pipeline 實作
- pgvector 搜尋查詢實作
- 前端改接 API

## 二、技術方案

### 2.1 架構選型

本階段以 FastAPI + Pydantic schema + SQLAlchemy model 為核心，原因如下：

- FastAPI 適合快速定義清楚的 API contract
- Pydantic 可直接對齊目前已整理好的 Swagger / response envelope
- SQLAlchemy model 可先建立 `notes` 與後續 `note_chunks` 的資料邊界
- 即使 AI 功能暫時先用 stub，也能先把 endpoint 邊界固定，避免前後端反覆重改

本階段不先做 embedding 與檢索實作，原因是如果資料模型、response format、CRUD 邊界尚未定穩，太早進入 AI workflow 會讓改動面變大。

### 2.2 核心流程

#### Step 1：後端資料模型與 schema

- 定義 `Note` persistence model
- 定義 request / response schema
- 定義統一 response envelope：
  - `code`
  - `success`
  - `message`
  - `data`
- 定義共用 error response schema

#### Step 2：Notes CRUD API

- 建立 `GET /notes`
- 建立 `GET /notes/{note_id}`
- 建立 `POST /notes`
- 建立 `PUT /notes/{note_id}`
- 建立 `DELETE /notes/{note_id}`
- 先確保 CRUD 行為與 response format 穩定

#### Step 3：AI API Contract

- 建立 `POST /ai/tag`
- 建立 `POST /ai/search`
- 建立 `POST /ai/chat`
- 第一版可先回傳 mock / placeholder data
- 確保 API contract 與 response schema 已固定，後續再接真實 AI 與 vector search

### 2.3 資料模型

本階段至少先定義以下資料模型：

#### `notes`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | 筆記唯一識別碼 |
| `title` | string | Yes | 筆記標題 |
| `content` | text | Yes | Markdown 筆記內容 |
| `tags` | string[] / JSON | No | 筆記標籤 |
| `created_at` | datetime | Yes | 建立時間 |
| `updated_at` | datetime | Yes | 更新時間 |

#### 預留模型：`note_chunks`

本階段可先定義 schema 或 model placeholder，不要求完成搜尋邏輯。

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | chunk 唯一識別碼 |
| `note_id` | UUID | Yes | 關聯 notes.id |
| `chunk_text` | text | Yes | chunk 內容 |
| `embedding` | vector / placeholder | Yes | embedding 向量 |
| `created_at` | datetime | Yes | 建立時間 |

### 2.4 API 設計

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| GET | `/api/v1/notes` | - | `code/success/message/data[]` |
| GET | `/api/v1/notes/{note_id}` | path: `note_id` | `code/success/message/data` |
| POST | `/api/v1/notes` | `title`, `content`, `tags?` | `code/success/message/data` |
| PUT | `/api/v1/notes/{note_id}` | `title`, `content`, `tags?` | `code/success/message/data` |
| DELETE | `/api/v1/notes/{note_id}` | path: `note_id` | `code/success/message/data` |
| POST | `/api/v1/ai/tag` | `title`, `content` | `code/success/message/data` |
| POST | `/api/v1/ai/search` | `query`, `top_k?` | `code/success/message/data` |
| POST | `/api/v1/ai/chat` | `question`, `top_k?` | `code/success/message/data` |

### 2.5 與現有系統整合

- 與目前前端 `client/` 的整合點是：
  - notes 列表
  - note detail / editor
  - AI search
  - AI chat
- 前端目前仍使用 local mock state，本階段完成後即可進入下一階段做 API 串接
- 與資料庫的整合先以 PostgreSQL 為主
- `pgvector` 與 OpenAI 會在後續階段接上，不要求本階段完成真實推論流程

## 三、任務拆解與時間估算

只列你指定的前三步。

| 子任務 | 預估工時 | 實際工時 | 偏差 | 說明 |
|--------|----------|----------|------|------|
| Step 1.1 定義 Notes / AI 共用 response envelope schema | 1.5h | | | 定義 `code/success/message/data` |
| Step 1.2 定義 Note model 與 Pydantic schema | 2h | | | 含 create / update / read schema |
| Step 1.3 預留 note_chunks model 或 schema placeholder | 1h | | | 供後續 embedding/search 階段使用 |
| Step 2.1 實作 `GET /notes` 與 `GET /notes/{note_id}` | 2h | | | 先完成讀取能力 |
| Step 2.2 實作 `POST /notes` 與 `PUT /notes/{note_id}` | 2.5h | | | 含欄位驗證 |
| Step 2.3 實作 `DELETE /notes/{note_id}` | 1h | | | 統一 success envelope |
| Step 2.4 撰寫 Notes CRUD API 測試 | 2h | | | endpoint 與 schema 驗證 |
| Step 3.1 實作 `POST /ai/tag` contract 與 stub service | 1.5h | | | 先保證回應格式正確 |
| Step 3.2 實作 `POST /ai/search` contract 與 stub service | 1.5h | | | 先回傳 placeholder results |
| Step 3.3 實作 `POST /ai/chat` contract 與 stub service | 1.5h | | | 先回傳 answer + sources |
| Step 3.4 撰寫 AI API 測試 | 2h | | | 驗證 success/error envelope |
| **總計** | **18.5h** | | | |

## 四、生產環境目標

此階段仍偏 API 基礎建設，先以 contract 穩定性與可整合性為主。

| 指標 | 目前 Baseline | 本次交付目標 |
|------|--------------|-------------|
| API contract 一致性 | 尚未建立 | 全部 8 隻 endpoint 統一使用同一 envelope |
| Notes CRUD 可用性 | 尚未建立 | 5 隻 CRUD endpoint 可於本機正常呼叫 |
| AI API 可整合性 | 尚未建立 | 3 隻 AI endpoint 有固定 request / response schema |
| 測試覆蓋率 | N/A | backend API 測試覆蓋率 ≥ 70% |

## 五、風險與相依

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| response format 在實作中再次改動 | 中 | 前後端與文件一起重改 | 先以 Swagger 定版再開始 router 實作 |
| tags 欄位 DB 型別選擇不穩 | 中 | migration 與 schema 需重改 | MVP 先用 PostgreSQL array 或 JSONB，先求簡單 |
| AI API 太早接真實 LLM | 中 | 開發節奏被外部依賴拖慢 | 本階段先用 stub，先固定 contract |
| `note_chunks` 是否現在就建表仍有不確定性 | 中 | 後續 migration 可能多一次調整 | 可先保留 placeholder schema，實作與 migration 拆到下一階段 |

**外部相依：**

- PostgreSQL / pgvector 的最終啟動方式
- FastAPI 專案結構
- 後續 OpenAI API key 與模型選型

## 六、驗收清單

### 功能驗收

- [ ] `Note` 資料模型與 schema 已建立
- [ ] `GET /notes`、`GET /notes/{note_id}` 可正常回傳
- [ ] `POST /notes`、`PUT /notes/{note_id}` 可正常建立與更新筆記
- [ ] `DELETE /notes/{note_id}` 可正常刪除筆記
- [ ] `POST /ai/tag` 可回傳 tags response envelope
- [ ] `POST /ai/search` 可回傳 search results response envelope
- [ ] `POST /ai/chat` 可回傳 answer + sources response envelope
- [ ] 全部 endpoint 使用統一 `code/success/message/data` 格式

### 生產環境驗收

- [ ] API contract 與 [doc/api/openapi.yaml](../api/openapi.yaml) 一致
- [ ] Notes CRUD 可於本機環境穩定呼叫
- [ ] AI API 即使尚未接真實模型，也能穩定回傳正確 schema

### 品質驗收

- [ ] Code Review 通過
- [ ] 測試覆蓋率 ≥ 70%
- [ ] 靜態分析零 critical issue
