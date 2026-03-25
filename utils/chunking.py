from __future__ import annotations


def chunk_text(text: str, size: int = 450) -> list[str]:
    words = text.split()
    if not words:
        return []
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
