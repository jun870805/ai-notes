# Architecture

此目錄放系統架構、資料流、技術決策與未來擴充設計。

## MVP Architecture

```text
React frontend
  -> FastAPI backend
  -> PostgreSQL + pgvector
  -> Gemini API
```

## Key Flows

- Note creation flow
- Embedding pipeline
- Semantic search flow
- AI chat / RAG flow

詳細流程目前先放在：

```text
doc/spec/20260520_AI_Notes_MVP_Product_Spec.md
```
