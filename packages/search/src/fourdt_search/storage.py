from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .records import SearchChunk

RUNTIME_ROOT = Path(".4dt") / "search"
CHUNKS_FILE = "chunks.jsonl"
MANIFEST_FILE = "manifest.json"


def search_dir(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT


def chunks_path(workspace: Path) -> Path:
    return search_dir(workspace) / CHUNKS_FILE


def manifest_path(workspace: Path) -> Path:
    return search_dir(workspace) / MANIFEST_FILE


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_chunks(workspace: Path, chunks: list[SearchChunk]) -> None:
    path = chunks_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(chunk.to_dict(), ensure_ascii=False, sort_keys=True) for chunk in chunks]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def read_chunks(workspace: Path) -> list[SearchChunk]:
    path = chunks_path(workspace)
    if not path.exists():
        return []
    chunks: list[SearchChunk] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            chunks.append(SearchChunk.from_dict(value))
    return chunks


def find_chunk(workspace: Path, result_id: str) -> SearchChunk | None:
    for chunk in read_chunks(workspace):
        if chunk.id == result_id:
            return chunk
    return None
