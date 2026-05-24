from __future__ import annotations

from pathlib import Path
from typing import Any

from fourdt_memory.search_backend import chunk_from_memory
from fourdt_memory.sqlite_store import MemoryStore

from ..records import SearchChunk


def collect(workspace: Path) -> list[SearchChunk]:
    store = MemoryStore(workspace)
    if not store.paths.sqlite_path.exists():
        return []
    try:
        store.connect()
        rows = store.list_live_memory_items()
        return [chunk_from_memory(row) for row in rows]
    finally:
        store.close()


def read(workspace: Path, chunk: SearchChunk) -> dict[str, Any]:
    return read_by_id(workspace, chunk.item_id or chunk.id)


def read_by_id(workspace: Path, memory_id: str) -> dict[str, Any]:
    store = MemoryStore(workspace)
    if not store.paths.sqlite_path.exists():
        raise RuntimeError("not_found")
    try:
        store.connect()
        item = store.get_memory_item(memory_id)
        if item is None:
            raise RuntimeError("not_found")
        return {"item": item}
    finally:
        store.close()
