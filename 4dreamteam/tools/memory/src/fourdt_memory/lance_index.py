from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


INDEX_FILE = "index.json"
TABLE_NAME = "memory"


class LanceIndex:
    def __init__(self, index_dir: str | Path):
        self.index_dir = Path(index_dir)
        self.index_path = self.index_dir / INDEX_FILE
        self.available = importlib.util.find_spec("lancedb") is not None

    def exists(self) -> bool:
        return self.index_path.exists()

    def read(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {"items": [], "providerModel": None}
        try:
            value = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"items": [], "providerModel": None, "corrupt": True}
        if not isinstance(value, dict):
            return {"items": [], "providerModel": None, "corrupt": True}
        if not isinstance(value.get("items"), list):
            value["items"] = []
        return value

    def rebuild(self, *, provider_model: str, items: list[dict[str, Any]]) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "providerModel": provider_model,
            "items": items,
        }
        self.index_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        if self.available:
            try:
                import lancedb  # type: ignore[import-not-found]

                db = lancedb.connect(str(self.index_dir))
                table_rows = [
                    {"id": item["id"], "vector": item["vector"], "providerModel": provider_model}
                    for item in items
                    if isinstance(item.get("id"), str) and isinstance(item.get("vector"), list)
                ]
                db.create_table(TABLE_NAME, data=table_rows, mode="overwrite")
            except Exception:
                return

    def vector_search(self, vector: list[float], *, provider_model: str, limit: int) -> list[dict[str, Any]]:
        if self.available:
            try:
                import lancedb  # type: ignore[import-not-found]

                db = lancedb.connect(str(self.index_dir))
                table = db.open_table(TABLE_NAME)
                rows = table.search(vector).limit(limit).to_list()
                results: list[dict[str, Any]] = []
                for row in rows:
                    if row.get("providerModel") == provider_model:
                        results.append(
                            {
                                "id": row.get("id"),
                                "score": -float(row.get("_distance", 0.0)),
                                "providerModel": row.get("providerModel"),
                            }
                        )
                return results
            except Exception:
                return []

        results: list[dict[str, Any]] = []
        for item in self.read().get("items", []):
            if not isinstance(item, dict) or item.get("providerModel") != provider_model:
                continue
            if not isinstance(item.get("id"), str) or not isinstance(item.get("vector"), list):
                continue
            results.append(
                {
                    "id": item["id"],
                    "vector": item["vector"],
                    "providerModel": provider_model,
                }
            )
        return results[:limit]

    def ids(self) -> list[str]:
        ids: list[str] = []
        for item in self.read().get("items", []):
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ids.append(item["id"])
        return ids
