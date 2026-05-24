from __future__ import annotations


def line_chunks(text: str, *, size: int = 60, step: int = 40) -> list[tuple[int, int, str]]:
    lines = text.splitlines()
    chunks: list[tuple[int, int, str]] = []
    if not lines:
        return chunks
    index = 0
    while index < len(lines):
        selected = lines[index : index + size]
        body = "\n".join(selected).strip()
        if body:
            chunks.append((index + 1, index + len(selected), body))
        index += step
    return chunks
