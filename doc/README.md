# Documentation

`doc/` 放置產品規格、API 文件、架構設計與開發計畫。

## 結構

```text
doc/
  spec/           # 產品規格與功能需求
  plan/           # 開發計畫、milestone、任務拆分
  api/            # API contract、request/response 範例
  architecture/   # 系統架構、資料流、技術決策
```

## 目前文件

- `spec/20260520_AI_Notes_MVP_Product_Spec.md`：MVP 產品規格。

## 文件維護原則

- 需求變更先更新 `spec/`。
- 開發切分與時程放在 `plan/`。
- API request/response contract 放在 `api/`。
- 跨模組設計、資料流與技術選型放在 `architecture/`。
- README 保持入口說明，細節放到對應子目錄。
