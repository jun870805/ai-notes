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

目前實際服務範圍：

- `db`
- `server`

預期啟動指令：

```bash
docker compose up --build db server
```

前端目前維持獨立以 Vite dev server 啟動，不在 Compose 內。

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

## 相關文件

- [../doc/2026-06-17-deployment-and-handoff.md](../doc/2026-06-17-deployment-and-handoff.md)
