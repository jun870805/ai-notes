# Client Source

`client/src/` 放 React 前端主要程式碼。

## 子目錄

- `api/`：封裝後端 API 呼叫。
- `components/`：可重用 UI 元件。
- `pages/`：頁面級元件，通常對應 route。
- `routes/`：React Router 設定。
- `hooks/`：自訂 React hooks。
- `types/`：共用 TypeScript 型別。
- `utils/`：純函式工具。

## 原則

- API 呼叫集中在 `api/`。
- 頁面負責組合資料與元件。
- 可重用顯示元件放 `components/`。
- 型別定義避免散落在頁面檔案中。
