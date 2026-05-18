# Alembic

`server/alembic/` 放資料庫 migration。

MVP 需要 migration 建立：

- `notes`
- `note_chunks`
- pgvector index

pgvector extension 可由 `infra/postgres/001_enable_vector.sql` 在本機 container 初始化時啟用。
