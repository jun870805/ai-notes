# Spec / Plan：AI Tag Gemini 實作

> 技術規格與開發計畫

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 功能名稱 | AI Tag Gemini 實作 |
| Brief 連結 | [20260520_AI_Notes_MVP_Product_Spec.md](../spec/20260520_AI_Notes_MVP_Product_Spec.md) |
| Owner (RD) | TBD |
| 歸屬模組 | AI Notes / Backend AI Tag |
| Spec 日期 | 2026-06-16 |
| Sprint | TBD |
| Review 狀態 | 已實作 |

## 一、需求理解確認

目前專案已提供：

- `POST /api/v1/ai/tag`
- `POST /api/v1/notes`
- `PUT /api/v1/notes/{note_id}`

目前專案已完成 `AI tag` 的真正 Gemini 生成流程。[server/app/services/tagging_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/tagging_service.py) 現在會呼叫 Gemini 生成 tags，並在單獨 `/ai/tag` 呼叫時走 strict mode；而在 `NoteService.create_note()` / `update_note()` 中，若使用者未手動提供 `tags`，則會自動產生 tags，失敗時退回 fallback 規則式標籤。

這份計畫現在用來記錄本階段的實際落地結果、保留的設計決策，以及後續還沒做的優化項目。

完成標準是：

- `/ai/tag` 已由 Gemini 生成 tags
- `POST /notes`、`PUT /notes/{note_id}` 在 `tags` 未提供時，會自動產生 tags
- tags 格式已符合規則：3 到 6 個、小寫英文或 kebab-case
- 失敗時已補明確 `tag_*` error envelope 或 fallback 策略

本階段仍不包含：

- 前端新增獨立「重新產生標籤」按鈕
- tags 分類層級或權重
- 多語標籤輸出
- tags 人工審核工作流

## 二、技術方案

### 2.1 架構選型

本功能沿用 Gemini provider，不新增額外模型服務，並延續目前 Notes API 的同步流程。

核心技術選擇如下：

- Tag generation provider：Gemini chat / generateContent
- Integration point：`TaggingService.generate_tags()`
- 自動標籤寫回：`NoteService.create_note()` / `update_note()`
- 對外 API：沿用 `POST /api/v1/ai/tag`

選擇這條路的理由：

- 現有 `NoteService` 已有自動標籤接點，不需再重構主要資料流
- tags 和 embeddings / chat 共用同一個 Gemini provider，環境變數與維運較單純
- 使用者在不手動輸入 tags 時，仍能維持產品上的自動整理體驗

替代方案與取捨：

- 繼續用規則式 tag：實作簡單，但品質有限，對新領域詞彙的泛化差
- 另外接分類模型：可行，但目前 MVP 沒必要增加 provider 複雜度
- 非同步背景生成：可降低寫入延遲，但會使 `notes.tags` 在短時間內不一致

目前實作採：

1. 同步呼叫 Gemini 生成 tags
2. 若使用者有手動傳入 `tags`，優先使用手動值
3. 若 Gemini 失敗，可先退回既有規則式 fallback，避免建立筆記失敗

### 2.2 核心流程

#### `POST /ai/tag`

1. 收到 `title`、`content`
2. 組出 Gemini prompt
3. 要求模型回傳 3 到 6 個 tags
4. 解析模型回應
5. 做格式清理與驗證：
   - 小寫
   - kebab-case
   - 去重
   - 限制在 3 到 6 個
6. 回傳 `tags`

#### `POST /notes` / `PUT /notes/{note_id}`

1. 若 request 帶有 `tags`
   - 先做 sanitize / dedupe 後使用使用者提供的 tags
2. 若 `tags` 未提供
   - 呼叫 `TaggingService.generate_tags(title, content)`
3. 將最終 tags 寫入 `notes.tags`
4. 繼續走既有 chunk / embedding pipeline

#### 失敗處理

- Gemini tag API 失敗：
  - MVP 建議先 fallback 到規則式 tag，避免整個 notes request 失敗
- Gemini 回應格式錯誤：
  - 先做 sanitize；若仍不合法，再 fallback
- `/ai/tag` 單獨呼叫失敗：
  - 已直接回 `tag_*` error envelope，而非靜默 fallback

### 2.3 資料模型

本階段不新增資料表，沿用 `notes.tags`。

#### `notes`

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | Yes | 筆記 ID |
| `title` | text | Yes | tag 生成輸入 |
| `content` | text | Yes | tag 生成輸入 |
| `tags` | json/jsonb | No | 最終標籤列表 |

#### Tag 格式規則

- 數量：`3` 到 `6`
- 字元：小寫英文、數字、連字號
- 樣式：`kebab-case`
- 去重：相同 tag 只保留一個

### 2.4 API 設計

本階段不新增 endpoint，沿用既有 `/ai/tag` 與 Notes API。

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/ai/tag` | `{ "title": string, "content": string }` | `{ "tags": string[] }` |
| POST | `/api/v1/notes` | `{ "title": string, "content": string, "tags"?: string[] }` | 建立 note，必要時自動生成 tags |
| PUT | `/api/v1/notes/{note_id}` | `{ "title": string, "content": string, "tags"?: string[] }` | 更新 note，必要時自動生成 tags |

#### `/ai/tag` 錯誤碼建議

- `tag_rate_limited`
- `tag_auth_failed`
- `tag_request_failed`
- `tag_unavailable`
- `tag_response_invalid`

### 2.5 與現有系統整合

- 與 [server/app/services/tagging_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/tagging_service.py) 整合：
  - 由規則式改為 Gemini generation + sanitize + fallback
- 與 [server/app/services/note_service.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/services/note_service.py) 整合：
  - 保留「未提供 `tags` 時自動產生」的邏輯
- 與 [server/app/routers/ai.py](/Users/peter/Documents/work/product/jun870805/ai-notes/server/app/routers/ai.py) 整合：
  - `/ai/tag` 改為真正模型化流程
- 與 [doc/api/ai-tag.md](/Users/peter/Documents/work/product/jun870805/ai-notes/doc/api/ai-tag.md) / OpenAPI 整合：
  - 補錯誤碼與 fallback 行為

## 三、任務拆解與時間估算

| 子任務 | 預估工時 | 實際工時 | 偏差 | 說明 |
|--------|----------|----------|------|------|
| 盤點現有 tag 規則式邏輯與 notes 接點 | 1h | 已完成 | - | 確認 create/update note 的自動標籤行為 |
| 設計 Gemini tag prompt | 2h | 已完成 | - | 要求 3-6 tags、小寫、kebab-case |
| 補 TaggingService 的 Gemini client | 3h | 已完成 | - | 呼叫模型、解析回應、錯誤處理 |
| 實作 sanitize / dedupe / fallback | 2h | 已完成 | - | 保證 tags 可寫入 DB |
| 接回 `POST /ai/tag` | 1h | 已完成 | - | 對外 API 變成模型化流程 |
| 驗證 `POST /notes` 自動標籤 | 2h | 已完成 | - | `tags=None` 時自動產生 |
| 驗證 `PUT /notes` 自動標籤 | 2h | 已完成 | - | 更新內容後自動重產 |
| 撰寫 API tests：`/ai/tag` | 2h | 已完成 | - | success / error |
| 撰寫 integration tests：notes 自動標籤 | 2h | 已完成 | - | create/update 行為與 fallback |
| 更新 API 文件 / README | 1h | 已完成 | - | 已同步現況 |
| **總計** | **18h** | | | |

## 四、生產環境目標

| 指標 | 目前 Baseline | 本次交付目標 |
|------|--------------|-------------|
| tag 品質 | 規則式，對新內容泛化有限 | 大部分工程筆記可生成合理 tags |
| 格式一致性 | 部分依賴規則式候選詞 | 所有輸出都符合 3-6 個、小寫、kebab-case |
| 建立 / 更新成功率 | tags 邏輯幾乎不失敗 | 即使 Gemini 失敗，也不影響 notes 寫入 |
| 延遲 P50 | N/A | ≤ 3s |

## 五、風險與相依

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| Gemini 回傳不符合格式 | 中 | tags 無法直接寫入或品質不穩 | 加 sanitize、去重、長度限制與 fallback |
| tag generation 拉長 notes 建立延遲 | 中 | 儲存體感變差 | 先同步做 MVP；若延遲高，再考慮非同步 |
| 使用者手動 tags 與 AI tags 行為混淆 | 中 | 規格不清 | 明確規定：手動 tags 優先，未提供才自動產生 |
| Gemini quota / rate limit | 中 | `/ai/tag` 與 notes 自動標籤不穩 | 補 `tag_*` 錯誤碼；notes 流程保留 fallback |

**外部相依：**

- Gemini API key 與可用 chat model
- 既有 Notes API 流程
- 一批真實技術筆記作為 tags 品質驗收樣本

## 六、驗收清單

### 功能驗收

- [x] `POST /api/v1/ai/tag` 已不再使用純規則式 placeholder
- [x] tags 數量為 `3` 到 `6`
- [x] tags 皆為小寫英文或 kebab-case
- [x] `POST /notes` 在未提供 `tags` 時會自動產生 tags
- [x] `PUT /notes/{note_id}` 在未提供 `tags` 時會自動重產 tags
- [x] 若 Gemini 失敗，notes 寫入仍可透過 fallback tags 完成
- [x] 手動提供給 notes 的 tags 也會做 sanitize / dedupe

### 生產環境驗收

- [ ] 真實 Gemini 環境下可生成合理 tags
- [ ] 建立 / 更新筆記延遲符合第四節目標
- [ ] 前端可看到自動產生的 tags 寫回筆記資料

### 品質驗收

- [ ] Code Review 通過
- [ ] 測試覆蓋率 ≥ 70%
- [ ] 靜態分析零 critical issue
