from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChunkDraft:
    chunk_index: int
    chunk_text: str
    token_count: int


def _estimate_token_count(text: str) -> int:
    return max(1, len(text.split()))


def chunk_markdown(content: str, *, max_chars: int = 900) -> list[ChunkDraft]:
    normalized = content.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    paragraphs = [part.strip() for part in normalized.split("\n\n") if part.strip()]
    chunks: list[ChunkDraft] = []

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
            for line in lines:
                chunks.append(
                    ChunkDraft(
                        chunk_index=len(chunks),
                        chunk_text=line,
                        token_count=_estimate_token_count(line),
                    )
                )
            continue

        chunks.append(
            ChunkDraft(
                chunk_index=len(chunks),
                chunk_text=paragraph,
                token_count=_estimate_token_count(paragraph),
            )
        )
    return chunks
