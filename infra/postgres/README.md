# PostgreSQL

`infra/postgres/` 放 PostgreSQL container 初始化檔案。

## 用途

- 啟用 pgvector extension。
- 放本機開發用 seed SQL。
- 放只需在 container 第一次建立時執行的 init SQL。

正式資料表 schema 建議使用 `server/alembic/` migration 管理。

## Example

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
