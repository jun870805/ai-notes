# Spec / Plan：note_chunks pgvector 欄位升級

> 技術規格與開發計畫

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 功能名稱 | note_chunks pgvector 欄位升級 |
| Brief 連結 | [20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) |
| Owner (RD) | TBD |
| 歸屬模組 | AI Notes / Backend Vector Search |
| Spec 日期 | 2026-06-12 |
| Sprint | TBD |
| Review 狀態 | 草稿 |

## 一、需求理解確認

本階段已完成將 `note_chunks.embedding` 從 JSON array 升級為真正的 `pgvector` 欄位，且建立 / 更新筆記後可正確寫入向量資料。現在需要把文件更新為實際狀態，並說明目前已具備的查詢能力與尚未完成的索引優化。

這份計畫的實際落地結果是：`note_chunks.embedding` 已使用真正的 `pgvector` 型別，後續的 `/ai/search` 與 `/ai/chat` 可以直接基於資料庫向量查詢實作 similarity search。

完成標準是：

- `note_chunks.embedding` 使用真正的 vector 欄位，而不是 JSON
- 建立 / 更新筆記後，新的 embedding 可正確寫入 vector 欄位
- 資料庫可執行向量距離查詢
- `/ai/search` 可直接使用這個 schema，不需要再改 DB 結構

本階段不包含：

- `/ai/search` 完整 API 行為與 ranking 調校
- `/ai/chat` prompt 組裝與答案生成
- chunk 切分規則重設計
- ANN vector index

## 二、技術方案

### 2.1 架構選型

本階段採用 PostgreSQL `pgvector` extension 作為正式向量儲存方案，取代目前 `note_chunks.embedding` 的 JSON 存法。

核心技術選擇如下：

- PostgreSQL extension：`vector`
- ORM 對應：SQLAlchemy 搭配 `pgvector` Python 套件
- 距離函式：優先使用 cosine distance
- index 策略：目前先不上 ANN index，後續依資料量與維度限制再做 halfvec、降維或其他索引策略

選擇這條路的原因：

- `pgvector` 是 PostgreSQL 原生向量搜尋常見方案，與目前 Docker 環境相容
- 後續可直接在 SQL 層做 similarity search，不需要先把所有向量拉回應用層比對
- 能為 `/ai/search` 與 `/ai/chat` 提供可延展的資料查詢基礎

替代方案與取捨：

- 繼續使用 JSON：實作最簡單，但幾乎無法做有效率的 similarity search
- 外接專門向量資料庫：功能更強，但對目前 MVP 來說會引入額外營運與整合成本

### 2.2 核心流程

#### Schema 升級流程

1. 確認資料庫已啟用 `vector` extension
2. 安裝 / 加入 `pgvector` Python 套件
3. 調整 SQLAlchemy model，將 `embedding` 型別改為 vector
4. 撰寫 Alembic migration：
   - 新增正式 vector 欄位
   - 規劃資料搬移策略
5. 驗證 migration 可在本機與 Docker PostgreSQL 環境跑通

#### 寫入流程

1. 建立 / 更新筆記
2. 產生 chunk 與 Gemini embeddings
3. 將 embeddings 轉成 `pgvector` 可接受的型別
4. 寫入 `note_chunks.embedding`

#### 查詢預備流程

1. 將 query 轉成 embedding
2. 使用 SQL distance operator 查詢最相近 chunks
3. 回傳 top-k chunks 作為 search / chat 上游資料

這一步先只確保 schema 和 repository 能支援，不在本 plan 內完成整個 `/ai/search`。

### 2.3 資料模型

#### `note_chunks`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | chunk 唯一識別碼 |
| `note_id` | UUID | Yes | 關聯 `notes.id` |
| `chunk_index` | integer | Yes | chunk 順序 |
| `chunk_text` | text | Yes | chunk 內容 |
| `token_count` | integer | No | token 粗估數 |
| `embedding` | vector(n) | Yes | 正式向量欄位 |
| `created_at` | timestamptz | Yes | 建立時間 |

#### 向量維度

Gemini embedding 模型維度已確認並固定為 `3072`，避免：

- schema 先用錯維度
- 未來 migration 再改欄位型別
- 新舊 embeddings 混用時維度不一致

目前 `gemini-embedding-2` 以 `3072` 維寫入 schema，若後續要建立 ANN index，需再評估：

- halfvec index
- 降維
- 其他索引策略

### 2.4 API 設計

本階段不新增對外 API，但會影響既有 Notes API 的內部寫入行為，並為未來 search/chat 查詢補齊 repository 能力。

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/notes` | `title`, `content`, `tags?` | 建立 note 並寫入 pgvector embedding |
| PUT | `/api/v1/notes/{note_id}` | `title`, `content`, `tags?` | 更新 note 並重建 pgvector embedding |

內部 repository / query 邊界建議補上：

- `replace_note_chunks(note, chunks, embeddings)`
- `search_similar_chunks(query_embedding, top_k)`

第二個方法可以先實作但不一定要立刻接到 router。

### 2.5 與現有系統整合

- 與 `server/app/models/note_chunk.py` 整合：
  - `embedding` 從 JSON 改成 vector
- 與 `server/app/services/embedding_service.py` 整合：
  - 確認 Gemini embeddings 輸出格式可直接映射到 vector 欄位
- 與 Alembic 整合：
  - migration 要能在 PostgreSQL 環境建立 / 轉換欄位
- 與 Docker Compose 整合：
  - 使用現有 `pgvector/pgvector:pg16`
  - 確認 init script 已啟用 `vector` extension

## 三、任務拆解與時間估算

| 子任務 | 預估工時 | 實際工時 | 偏差 | 說明 |
|--------|----------|----------|------|------|
| 確認 Gemini embedding 維度與 model 限制 | 1.5h | 已完成 | 0 | 最終確認為 `3072` 維 |
| 安裝 / 納入 `pgvector` Python 套件 | 1h | 已完成 | 0 | `pyproject.toml` 已更新 |
| 調整 `NoteChunk` model 為 vector 欄位 | 2h | 已完成 | 0 | PostgreSQL 用 vector，SQLite 用 JSON fallback |
| 撰寫 migration：JSON → vector 欄位 | 3h | 已完成 | 0 | PostgreSQL migration 已驗證可跑 |
| 驗證 PostgreSQL migration 與 rollback | 2h | 已完成 | 0 | 以 Docker 臨時資料庫驗證 upgrade |
| 調整 repository 寫入邏輯 | 2h | 已完成 | 0 | embeddings 已寫入 vector 欄位 |
| 補 similarity query repository prototype | 2h | 已完成 | 0 | 已有 cosine distance query prototype |
| 建立 vector index | 1.5h | 未完成 | - | `3072` 維直接建 HNSW 會撞 PostgreSQL 限制 |
| 撰寫 unit/integration tests | 3h | 已完成 | 0 | schema、寫入、查詢 prototype 測試已補上 |
| 撰寫手動驗證步驟與 SQL 範例 | 1h | 部分完成 | - | 已有基本驗證流程，仍可再整理 |
| **總計** | **19h** | | | |

## 四、生產環境目標

| 指標 | 目前 Baseline | 本次交付目標 |
|------|--------------|-------------|
| 向量欄位可查詢性 | JSON array，無法直接做 similarity search | 已達成：`note_chunks.embedding` 可直接做向量距離查詢 |
| 寫入成功率 | embedding 可存，但非正式向量型別 | 已達成：建立 / 更新筆記後可寫入 vector 欄位 |
| 查詢延展性 | `/ai/search` 無法直接接 DB 向量查詢 | 已達成：repository 已可支援 top-k similarity prototype |
| schema 穩定性 | 暫時性結構 | 已達成：migration 後成為後續 search/chat 的正式資料結構 |

## 五、風險與相依

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| Gemini embeddings 維度與預期不符 | 低 | vector 欄位型別設計錯誤 | 已確認目前為 `3072` 維 |
| JSON → vector 資料搬移不順 | 低 | migration 失敗或舊資料遺失 | 已驗證 migration 可在 PostgreSQL 跑通 |
| `pgvector` Python 套件與 SQLAlchemy 整合出現相容性問題 | 低 | model / migration 卡住 | 已完成最小可行整合 |
| 3072 維向量無法直接建立 HNSW index | 高 | ANN index 先無法落地 | 後續改做 halfvec、降維或其他索引策略 |
| SQLite 測試環境與 PostgreSQL 行為差異 | 中 | 測試綠燈但實際 DB 不通 | 已在 Docker PostgreSQL 額外驗證 migration |

**外部相依：**

- `pgvector` extension 與 Python 套件可用性
- Docker PostgreSQL 環境可正常執行 migration
- 後續 vector index 策略決策

## 六、驗收清單

### 功能驗收

- [x] `note_chunks.embedding` 已改為真正的 vector 欄位
- [x] 建立筆記後，資料可寫入 vector 欄位
- [x] 更新筆記後，重建的 chunks 仍可寫入 vector 欄位
- [x] repository 可執行基本 similarity search prototype
- [ ] vector index 已建立且可於 PostgreSQL 驗證

### 生產環境驗收

- [x] Docker PostgreSQL 環境可成功執行 migration
- [x] 建立 / 更新筆記流程在 vector 欄位下仍能正常完成
- [x] 資料庫可直接執行向量距離查詢並返回合理結果

### 品質驗收

- [ ] Code Review 通過
- [ ] 測試覆蓋率 ≥ 70%
- [ ] 靜態分析零 critical issue
