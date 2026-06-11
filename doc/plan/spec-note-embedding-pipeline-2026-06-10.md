# Spec / Plan：筆記 Chunk 與 Embedding Pipeline

> 技術規格與開發計畫

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 功能名稱 | 筆記 Chunk 與 Embedding Pipeline |
| Brief 連結 | [20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) |
| Owner (RD) | TBD |
| 歸屬模組 | AI Notes / Backend AI Pipeline |
| Spec 日期 | 2026-06-10 |
| Sprint | TBD |
| Review 狀態 | 草稿 |

## 一、需求理解確認

目前專案已完成 `notes` CRUD、AI API contract、前端串接與 PostgreSQL 基礎架構，但 AI 搜尋與 AI 對話仍是 placeholder。要讓後續的 semantic search 與 RAG 真正可用，必須先建立一條穩定的資料處理流程：當筆記被建立或更新時，系統會自動把 Markdown 內容切成可檢索的文字片段，為每個片段產生 embedding，並將結果寫入 `note_chunks`。

這份計畫的完成標準是：

- 建立與更新筆記後，`note_chunks` 會被正確重建
- 每個 chunk 都有可查詢的文字內容、順序資訊與 embedding
- pipeline 失敗時不會把 `notes` 主資料寫壞，且有明確錯誤處理
- 後續 `AI 搜尋` 與 `AI 對話` 可以直接使用 `note_chunks` 作為檢索資料來源

本階段不包含：

- `/ai/search` 的 similarity query 實作細節
- `/ai/chat` 的 prompt 與 answer generation
- 前端新增操作入口

## 二、技術方案

### 2.1 架構選型

這段流程採用「同步寫入主筆記資料 + 背景化重建 chunk / embedding」的設計，具體如下：

- `notes` 仍由現有 CRUD API 同步寫入 PostgreSQL
- `note_chunks` 作為獨立表存放切段後內容與向量
- embedding 由 Gemini embedding model 產生
- `pgvector` 用於儲存向量欄位，供後續 similarity search 使用
- 文件 embedding 建議使用 Gemini retrieval 格式，例如：
  - `title: {title} | text: {content}`
- 查詢 embedding 建議使用 Gemini retrieval query 格式，例如：
  - `task: search result | query: {query}`

選這個方向的理由：

- `notes` 與 `note_chunks` 分開，資料責任清楚，後續 search/chat 不需要反覆解析原始 Markdown
- 先完成 pipeline，再接搜尋與對話，開發風險較低
- 建立 / 更新時即時重建，可保證檢索資料與筆記內容一致，不會長時間使用舊向量

替代方案與取捨：

- 只在搜尋時即時計算 embedding：實作簡單，但延遲高且成本不可控
- 以 queue / worker 非同步處理：較適合正式環境，但目前 MVP 可先在 API 內完成重建，後續再抽成背景任務

建議 MVP 採兩階段方式：

1. 先在 `POST /notes`、`PUT /notes/{note_id}` 後同步執行 chunk + embedding 重建，先讓功能可用
2. 後續若延遲與穩定性成為問題，再抽成 background job 或 queue worker

### 2.2 核心流程

#### 建立筆記

1. 驗證 `title`、`content`、`tags`
2. 寫入 `notes`
3. 將 `content` 轉成 chunk 列表
4. 逐批呼叫 embedding API
5. 刪除該筆記舊的 `note_chunks`（建立時通常為空）
6. 寫入新的 `note_chunks`
7. 回傳建立成功的 `note`

#### 更新筆記

1. 讀取既有 `note`
2. 更新 `title`、`content`、`tags`
3. 重新將新版 `content` 切 chunk
4. 逐批呼叫 embedding API
5. 刪除舊的 `note_chunks`
6. 寫入新的 `note_chunks`
7. 回傳更新成功的 `note`

#### 失敗處理

- 若 `notes` 還沒寫入成功：整筆 request 直接失敗
- 若 `notes` 已寫入但 embedding 失敗：
  - MVP 建議整個 request 回滾，避免主資料與檢索資料不一致
  - 若之後要改為非同步模式，再引入 `embedding_status` 或補償機制

### 2.3 資料模型

本階段重點是補強 `note_chunks`，並確認是否需要在 `notes` 增加少量狀態欄位。

#### `note_chunks`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | chunk 唯一識別碼 |
| `note_id` | UUID | Yes | 關聯 `notes.id` |
| `chunk_index` | integer | Yes | chunk 在筆記中的順序 |
| `chunk_text` | text | Yes | 用於檢索的文字內容 |
| `token_count` | integer | No | 該 chunk 估算 token 數，供後續調校 |
| `embedding` | vector(n) | Yes | embedding 向量 |
| `created_at` | timestamptz | Yes | 建立時間 |

#### `notes` 建議補充欄位

若希望後續可觀察 pipeline 狀態，可考慮新增以下欄位；若想先保持 schema 精簡，可先不做。

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `embedding_updated_at` | timestamptz | No | 最近一次完成 embedding 重建時間 |

### 2.4 API 設計

本階段不新增前端直接呼叫的新 endpoint，主要是改造既有 Notes API 的內部行為。

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/notes` | `title`, `content`, `tags?` | 建立 `notes`，並同步建立 `note_chunks` |
| PUT | `/api/v1/notes/{note_id}` | `title`, `content`, `tags?` | 更新 `notes`，並同步重建 `note_chunks` |

可選的內部 service 邊界：

- `chunk_markdown(content) -> list[ChunkDraft]`
- `embed_chunks(chunks) -> list[EmbeddingVector]`
- `replace_note_chunks(note_id, chunk_records) -> None`

這樣後續做 `/ai/search` 時可直接重用 `replace_note_chunks` 之後的資料表結構。

### 2.5 與現有系統整合

- 與 `server/app/routers/notes.py` 整合：
  - `createNote`
  - `updateNote`
- 與 SQLAlchemy model / migration 整合：
  - `note_chunks` 欄位需從 placeholder 改成可儲存 pgvector 的正式 schema
- 與 Docker Compose 整合：
  - 確認 PostgreSQL 啟用 `vector` extension
- 與環境變數整合：
  - 需要 `GEMINI_API_KEY`
  - 需要可設定 embedding model 名稱

## 三、任務拆解與時間估算

| 子任務 | 預估工時 | 實際工時 | 偏差 | 說明 |
|--------|----------|----------|------|------|
| 定義 chunk 切分規則與資料結構 | 2h | | | 決定以段落 / 標題 / 長度為主的切分策略 |
| 調整 `note_chunks` model 與 migration | 2h | | | 加入 `chunk_index`、正式 vector 欄位、必要 index |
| 實作 Markdown chunk service | 3h | | | 將內容切成穩定 chunk，避免過短或過長 |
| 實作 embedding client 封裝 | 2h | | | 串 Gemini embedding API，支援批次呼叫 |
| 實作 `replace_note_chunks` repository/service | 2h | | | 同一筆記的 chunk 全量替換 |
| 將 pipeline 接入 `POST /notes` | 2h | | | 建立筆記後同步產生 chunks |
| 將 pipeline 接入 `PUT /notes/{note_id}` | 2h | | | 更新筆記後同步重建 chunks |
| 補錯誤處理與 transaction 邊界 | 2h | | | embedding 失敗時回滾策略 |
| 撰寫 unit tests：chunk service | 2h | | | 驗證切段結果穩定 |
| 撰寫 integration tests：建立 / 更新後的 chunk 重建 | 3h | | | 驗證 `notes` 與 `note_chunks` 一致 |
| 撰寫手動驗證文件 | 1h | | | 說明如何確認 chunk 與 embedding 已建立 |
| **總計** | **23h** | | | |

## 四、生產環境目標

| 指標 | 目前 Baseline | 本次交付目標 |
|------|--------------|-------------|
| 筆記寫入後的檢索資料完整性 | `note_chunks` 尚未真實建立 | 建立 / 更新筆記後，`note_chunks` 成功寫入率 ≥ 95% |
| 單篇筆記重建延遲 | N/A | 一般長度筆記在 5 秒內完成 chunk + embedding |
| chunk 一致性 | 無 | 相同內容重建時，chunk 數量與順序穩定 |
| 失敗可觀察性 | 無 | API log 可明確辨識 chunk 或 embedding 失敗點 |

## 五、風險與相依

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| Markdown chunk 規則切得太碎或太長 | 中 | 搜尋品質變差、embedding 成本變高 | 先定單一規則並用真實筆記樣本驗證 |
| embedding API 延遲過高 | 中 | 建立 / 更新筆記體感變差 | 先做 batch embedding，必要時再拆背景任務 |
| 向量欄位型別與 SQLAlchemy / Alembic 整合不順 | 中 | migration 卡住、DB schema 無法落地 | 先用小範圍 spike 驗證 pgvector model 寫法 |
| 同步回滾策略導致建立筆記容易失敗 | 中 | 使用者無法保存筆記 | MVP 先求資料一致；若失敗率偏高，再評估非同步化 |
| Gemini embedding model 變更或限制 | 低 | API 行為與成本波動 | 將 model 名稱與 batch size 參數化 |

**外部相依：**

- Gemini API key 與可用 embedding model
- `pgvector` 在本機與 Docker 環境的實際型別支援
- 一批真實工程筆記樣本，供 chunk 規則驗證

## 六、驗收清單

### 功能驗收

- [ ] 建立筆記後，資料庫中可看到對應的 `note_chunks`
- [ ] 更新筆記後，舊的 `note_chunks` 會被替換為新內容
- [ ] 每個 chunk 都包含 `chunk_index`、`chunk_text`、`embedding`
- [ ] 同一篇筆記的 chunk 順序穩定且可重建
- [ ] embedding 失敗時，API 有明確錯誤訊息且不留下半套資料

### 生產環境驗收

- [ ] 建立 / 更新筆記的平均延遲符合第四節目標
- [ ] `note_chunks` 寫入結果可供後續 `/ai/search` 直接使用
- [ ] 日誌中可追蹤單筆筆記的 chunk / embedding 重建結果

### 品質驗收

- [ ] Code Review 通過
- [ ] 測試覆蓋率 ≥ 70%
- [ ] 靜態分析零 critical issue
