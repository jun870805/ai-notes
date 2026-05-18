---
name: mr-description
description: Use when writing a GitLab/GitHub MR (Merge Request) description for the exchange backend project. Provides the standard MR template with ClickUp, API Spec, Modification, and LocalTest sections.
---

# MR Description Template

## Overview

撰寫 MR 描述時使用此模板，確保每個 MR 都包含必要資訊，讓 reviewer 能快速了解變更範圍、目的與驗收方式。

## Template

```markdown
## ClickUp
{ClickUp task URL or ticket ID}
{Feature/task name}

## API Spec
{Notion / Confluence / 內部 spec 文件連結}
{Spec 標題}

**背景：**{說明此 MR 解決的根本問題（root cause）。描述現象、原因與影響範圍。}

## Modification

{用條列式描述此 MR 的變更內容，每一項說明一個獨立的改動。
格式：動詞開頭（新增、修正、補齊、加入、移除），說明具體改動與影響範圍。}

## LocalTest

{描述如何在本地驗證此 MR 的功能，包含：
- 測試指令或步驟
- 測試情境（正常流程、異常流程）
- 預期結果
- 若有 Postman collection 或 curl 範例也可附上}
```

## Example

```markdown
## ClickUp
https://app.clickup.com/t/xxxxxxxx
OMS_ 後台管理種子用戶 Credit

## API Spec
https://www.notion.so/xxxxxxxx
OMS_ 後台管理種子用戶 Credit

## Modification

- 新增 OMS 人工加值、人工減值與積分異動列表查詢 API，支援 user_deposit_point_log 紀錄與 admin 查詢。
- 補齊 Stripe webhook 的訂閱點數異動紀錄，涵蓋首購、續訂、升級、降級、付款失敗與取消訂閱等情境。
- 在 AskME 點數扣除流程加入 type=2 使用紀錄，並在點數更新失敗時避免寫入錯誤 log。
- 新增 SubscriptionPlanUtil、log type / plan 對照與相關單元測試，補強點數與方案語義一致性。

## LocalTest

- 執行 `mvn org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test -pl exchange-admin -Dtest=XxxServiceImplTest` 確認新增單元測試全數通過。
- 使用 Postman 呼叫人工加值 API，確認 user_deposit_point_log 正確寫入。
- 模擬 Stripe webhook 事件（invoice.paid），確認訂閱點數異動紀錄補寫正常。
```

## Output

填寫完成後，將產出的 MR 描述用 Write tool 存檔：

- 路徑：`~/Work/manual-tests/<branch-name>-mr.md`
- `<branch-name>` 為當前 git branch 名稱（執行 `git branch --show-current` 取得）
- 檔案內容只包含填好的 MR 描述 markdown，不含任何說明文字

## Filling Guidelines

| 欄位 | 說明 |
|------|------|
| **ClickUp** | 先放 ticket URL，換行放功能名稱（格式與 ClickUp ticket 標題一致） |
| **API Spec** | 先放 spec 文件 URL，換行放 spec 標題；若無 spec 文件則填「N/A」；**背景**欄位說明 root cause，描述現象、原因與影響範圍 |
| **Modification** | 每項一個獨立改動，動詞開頭，說明「做了什麼」與「影響範圍」；避免過於籠統（勿用「修改了一些東西」）|
| **LocalTest** | 說明具體測試步驟，至少涵蓋 happy path；有單元測試要附上執行指令 |

## Common Mistakes

- Modification 只寫檔案名稱，沒說明「做了什麼」→ 改為動詞開頭的完整描述
- LocalTest 只寫「run tests」→ 補上完整測試指令與預期結果
- ClickUp / API Spec 欄位留空 → 確認是否有對應資源；真的沒有才填 N/A
