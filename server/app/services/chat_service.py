from __future__ import annotations

from app.schemas.ai import SearchResult


class ChatService:
    def answer(self, question: str, sources: list[SearchResult]) -> str:
        if not sources:
            return "沒有足夠的筆記資料可以回答這個問題。"
        combined = " ".join(source.chunk_text for source in sources)
        return f"根據目前檢索到的筆記內容，{combined} 以上回答對應問題「{question}」。"

