# Client

`client/` 是 AI Engineer Notes 的 React 前端。MVP 會使用 React、TypeScript、Vite、React Router、TanStack Query、Tailwind CSS 與 Markdown renderer。

## 目標

- 提供筆記列表、建立、編輯、刪除與閱讀介面。
- 提供 Markdown editor 與 preview。
- 提供 AI 語意搜尋頁面。
- 提供 AI Chat 頁面，顯示回答與引用來源。
- 將 API 呼叫集中在 `src/api/`，避免 UI 元件直接處理 HTTP 細節。

## 建議結構

```text
client/
  public/
  src/
    api/          # API client，例如 notes.ts、ai.ts
    components/   # 可重用 UI 元件
    pages/        # Route 對應頁面
    routes/       # React Router 設定
    hooks/        # 自訂 React hooks
    types/        # 前端共用 TypeScript 型別
    utils/        # 純函式工具
```

## 頁面範圍

- Notes List Page
- Note Detail / Editor Page
- AI Search Page
- AI Chat Page

## API Boundary

前端只透過後端 API 操作資料，不直接存取資料庫或 OpenAI API。

預期 API client：

- `src/api/notes.ts`
- `src/api/ai.ts`

## 開發注意事項

- Server state 使用 TanStack Query 管理。
- Editor 內部輸入狀態使用 React local state。
- Markdown preview 應避免直接渲染未清理 HTML。
- UI 要能清楚呈現 AI 回答來源，讓使用者可追溯到原筆記。
