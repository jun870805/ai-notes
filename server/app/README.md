# Server App

`server/app/` 放 FastAPI 應用程式主要程式碼。

## 子目錄

- `models/`：SQLAlchemy models。
- `schemas/`：Pydantic schemas。
- `routers/`：FastAPI route handlers。
- `services/`：business logic、AI workflow、RAG、tagging、embedding。
- `repositories/`：資料庫查詢與 persistence logic。

## 原則

- `routers/` 不直接寫複雜 business logic。
- `services/` 負責 use case 與流程 orchestration。
- `repositories/` 負責資料存取。
- `schemas/` 定義 API request/response contract。
- `models/` 對應資料庫 schema。
