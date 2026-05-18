---
name: exchange-rd-format
description: Use when writing a design document or RD (Requirements Document) for the exchange backend project. Provides the standard RD template with ClickUp, Spec, 說明, DB Modify, and API sections.
---

# Exchange RD Document Format

RD 文件的標準格式，用於 exchange backend 專案的功能設計文件。

## Template

```markdown
> **ClickUp**

{ClickUp task URL}

---

> **Spec**

{Notion spec URL}

---

> **說明**

- {功能說明條列，每點一個業務規則或功能描述}

---

> **DB Modify**

{若有 schema 異動，貼上完整 DDL SQL；無異動則省略此段}

---

> **API**

{每支 API 一個區塊，格式如下}
```

## API 區塊格式

每支 API（新增或修改）依以下格式撰寫：

```markdown
- **[新增 / 修改] {說明} `{HTTP Method} {path}`**

  **說明**
  {一段說明此 API 的用途與業務邏輯}

  - **Request**

    Headers

    | 參數名稱 | 參數類型 | 是否必填 | 參數說明 |
    | --- | --- | --- | --- |
    | lang | String | 否 | 預設 en |

    Path Variable：`{param}`（型別，說明）

    Query Parameter / Body

    | 參數名稱 | 參數類型 | 是否必填 | 參數說明 |
    | --- | --- | --- | --- |

    ```json
    // Request body 範例（POST/PUT 才需要）
    {
      "field": value
    }
    ```

  - **Response**

    成功

    ```json
    {
      "code": 1,
      "msg": null,
      "data": { ... }
    }
    ```

    欄位說明

    | 欄位 | 型別 | 說明 |
    | --- | --- | --- |

    錯誤情境

    | 情境 | code | 說明 |
    | --- | --- | --- |
```

## 注意事項

- `RestResponse` 格式：`{ code, msg, data }`，成功 `code=1`
- 時間欄位型別標注 `Timestamp`，說明欄補充「Unix timestamp 秒」
- 修改既有 API 只列出本次**新增或異動**的欄位，其餘欄位說明「沿用既有邏輯」
- 錯誤情境的 code 填整數（對應 `ErrorCodeEnum`）
