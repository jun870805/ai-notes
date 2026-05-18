---
name: powerflow-code-review
description: Use when completing any feature or bugfix in the powerflow/InsightVex project, before marking work done or pushing.
---

# Powerflow Code Review 檢查清單

## 概覽

在宣告任何功能完成或 push 之前，必須對所有修改過的檔案跑完此清單。以下是此專案的基本規範，違反任何一條都要修。

---

## 1. i18n — 禁止寫死使用者可見字串

所有顯示給使用者的文字必須透過 `t.*` translation key，禁止在 TSX / TS 裡寫死中文或任何語言的字串。

- UI 文字：`t.workflows.xxx`、`t.common.xxx` 等
- 新增 key 時：`client/src/lib/i18n/types.ts` + 全部 13 個 locale 檔都要加
- Server 回傳錯誤訊息給前端時：使用機器可讀的 `errorCode`（如 `'EMBED_IN_PROGRESS'`），前端再自行翻譯；**禁止前端用 `includes('中文字串')` 來偵測 server 狀態**

---

## 2. Catch 塊 — 禁止無聲吞錯

每個 `catch` 必須明確區分「預期的正常狀況」與「真正的錯誤」。

- 只有確定是「資源不存在」（如 Qdrant collection not found）才可以回傳預設值
- 網路逾時、auth 失敗、服務崩潰等非預期錯誤必須 rethrow 或上報
- 空 `catch {}` 或直接 `return 0 / [] / false` 而不判斷原因 → 禁止

---

## 3. 前端重試流程 — 必須有 circuit breaker

任何「收到特定訊號後自動重試」的流程（如 SSE ready 後重送查詢），必須有最大重試次數限制，防止 race condition 造成無限迴圈。

---

## 4. 使用者回饋 — 不能無聲失敗

任何 cleanup / 結束流程必須告知使用者原因。禁止 banner 無聲消失、錯誤無聲吞掉而不顯示任何訊息。

---

## 5. 狀態競爭 — 修改共享資源前先確認鎖

對共享資源（Qdrant collection、Redis 快取）做破壞性操作（reset、清除）前，必須先確認沒有其他 job 正在使用該資源（檢查 embed lock）。

---

## 6. API 授權 — JWT 驗證 ≠ 資源授權

每個 workflow 相關 endpoint 除了驗 JWT（`authenticateToken`），還必須確認該使用者對該 workflow 有對應權限（`canExecute`、`canView` 等），禁止只驗身份不驗權限。

---

## 7. 外部呼叫錯誤處理

Prisma、Redis、Qdrant 等外部呼叫，特別是在 SSE handler、background job、`finally` 塊中，必須有 try-catch。`finally` 塊內的外部呼叫若拋錯，必須用 `.catch()` 處理，不能蓋掉原始錯誤。

---

## 8. 錯誤日誌 — 保留完整 stack trace

fire-and-forget 的 `.catch()` 或任何 logger 呼叫，必須傳入完整 error 物件，禁止只記錄 `err.message`。

```typescript
// ✗ 失去 stack trace
logger.error(`失敗: ${err.message}`)

// ✓ 保留完整資訊
logger.error('失敗:', err)
```

---

## 快速掃描紅旗

| 看到這個 | 問題 |
|---------|------|
| TSX/TS 裡有中文字串字面量（非 translation 檔）| 違反 i18n |
| `includes('中文')` 用於判斷 API response | 脆弱的跨層耦合 |
| `catch { return 0 }` / `catch { return [] }` | 可能吞掉真實錯誤 |
| SSE / 重試流程沒有計數器 | 潛在無限迴圈 |
| `sse.onerror = () => { cleanup(); }` | 無聲失敗 |
| endpoint 只有 `authenticateToken` 沒有 permission check | 缺少資源授權 |
| `finally` 裡有 `await` 且沒有 `.catch` | 可能蓋掉原始錯誤 |
| `.catch(err => logger.error(err.message))` | stack trace 遺失 |
