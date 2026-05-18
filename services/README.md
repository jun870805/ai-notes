# Services

`services/` 目前保留給未來獨立 service 或 worker。

MVP 階段建議先不要把邏輯拆到這裡，而是放在：

```text
server/app/services/
```

這樣可以降低部署與開發複雜度。

## 何時使用這個目錄

當以下需求出現時，再考慮把邏輯拆成根目錄 `services/`：

- embedding pipeline 需要獨立 worker。
- AI 任務需要 queue，例如 Redis / Celery / RQ。
- chat response 需要 streaming gateway。
- 有多個後端服務需要共享同一組 domain logic。

## 可能結構

```text
services/
  embedding-worker/
  ai-gateway/
  shared/
```

在拆分前，請先確認服務邊界、部署方式、資料存取責任與 observability 設計。
