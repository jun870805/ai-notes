from __future__ import annotations

import re


class TaggingService:
    _candidates = [
        "fastapi",
        "websocket",
        "streaming",
        "backend",
        "frontend",
        "react",
        "pgvector",
        "retrieval",
        "docker",
        "auth",
        "jwt",
        "markdown",
    ]

    def generate_tags(self, title: str, content: str) -> list[str]:
        haystack = f"{title}\n{content}".lower()
        tags = [tag for tag in self._candidates if tag in haystack][:6]
        if len(tags) >= 3:
            return tags

        words = [
            word
            for word in re.split(r"[^a-z0-9]+", haystack)
            if len(word) > 3 and word.isascii() and word not in tags
        ]
        for word in words:
            tags.append(word)
            if len(tags) == 3:
                break
        return tags[:6] or ["engineering-note", "notes", "knowledge"]

