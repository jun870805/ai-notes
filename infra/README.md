# Infra

`infra/` 放置本機開發、資料庫初始化、Docker 與部署相關檔案。

## 目標

- 管理 PostgreSQL / pgvector 初始化。
- 放置 Docker Compose 相關輔助設定。
- 放置本機開發環境 scripts。
- 未來可擴充部署設定，例如 cloud build、reverse proxy 或 migration job。

## 建議結構

```text
infra/
  postgres/       # PostgreSQL 與 pgvector init SQL
  scripts/        # 本機環境輔助腳本
```

## Docker Compose

根目錄預期會有：

```text
docker-compose.yml
```

服務範圍：

- `frontend`
- `backend`
- `db`

預期啟動指令：

```bash
docker compose up --build
```

## PostgreSQL / pgvector

`infra/postgres/` 可放：

- `init.sql`
- extension setup
- local seed data

MVP 至少需要啟用：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

正式 schema 建議由 Alembic migration 管理。
