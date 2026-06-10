# Client

`client/` 是 AI 工程筆記的 React 前端，目前使用 React、TypeScript、Vite、React Router 與 Vitest。這一版已經有可執行的 MVP 畫面與測試，但資料仍以本地 mock state 為主，尚未串接後端 API。

## 目前功能

- 筆記列表頁
- 新增 / 編輯筆記頁
- Markdown 預覽
- AI 搜尋頁
- AI 對話頁
- 繁中介面文案
- 基本前端測試與 coverage

## 啟動方式

```bash
cd client
npm install
npm run dev
```

開發伺服器啟動後，建議使用 `http://127.0.0.1:5173` 開啟。

若要串接本機 backend，預設會打：

```text
http://127.0.0.1:8000/api/v1
```

若要改 API base URL，可在啟動前設定：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev
```

## 常用指令

```bash
npm run dev
npm run build
npm run preview
npm test
npm run test:watch
```

## 測試

目前測試使用 Vitest、Testing Library 與 jsdom。

涵蓋範圍：

- 主要導覽與繁中文案
- `AI 搜尋` / `AI 對話` 頁面骨架一致性
- 新增筆記與儲存流程
- tab 切換
- `mockData` 的搜尋與回答邏輯

coverage 目前目標已達 80% 以上。

## 目錄結構

```text
client/
  public/
  src/
    components/   # 共用 UI 元件
    pages/        # 各 route 對應頁面
    test/         # 測試初始化與 helper
    types/        # 共用 TypeScript 型別
    utils/        # 純函式與 mock data
    App.tsx       # 路由與本地資料狀態
    main.tsx      # 入口點
    styles.css    # 全站樣式
```

## 主要檔案

- `src/App.tsx`：路由、notes store、本地 CRUD / search / chat 行為
- `src/components/AppLayout.tsx`：全站版型與主導覽
- `src/pages/NotesListPage.tsx`：筆記列表
- `src/pages/NoteEditorPage.tsx`：新增 / 編輯 / 刪除 / 預覽
- `src/pages/SearchPage.tsx`：AI 搜尋
- `src/pages/ChatPage.tsx`：AI 對話
- `src/utils/mockData.ts`：目前畫面用的 sample notes 與搜尋 / 回答邏輯
- `src/App.test.tsx`、`src/utils/mockData.test.ts`：目前測試案例

## 現況限制

- 已串接 backend API，但 AI 流程目前仍是 server placeholder implementation
- `AI 搜尋` 與 `AI 對話` 的 server response schema 已固定，但還不是實際 embedding / retrieval / LLM 流程
- Markdown preview 是輕量自製 renderer，僅支援目前 MVP 需要的基本語法

## 下一步建議

- 將 notes CRUD 改為呼叫後端 API
- 將 `AI 搜尋` / `AI 對話` 接到實際的 server endpoint
- 視需要再引入 TanStack Query 管理 server state
- 補上更多元件級測試與錯誤情境測試
