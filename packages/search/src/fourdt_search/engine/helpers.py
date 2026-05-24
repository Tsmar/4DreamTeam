from __future__ import annotations

import math
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


NON_DECOMPOSABLE_MAP = str.maketrans(
    {
        "ł": "l",
        "Ł": "L",
        "đ": "d",
        "Đ": "D",
        "ø": "o",
        "Ø": "O",
        "ħ": "h",
        "Ħ": "H",
        "ŧ": "t",
        "Ŧ": "T",
        "ı": "i",
        "ß": "ss",
    }
)


def strip_diacritics(value: str) -> str:
    value = value.translate(NON_DECOMPOSABLE_MAP)
    normalized = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def is_blank(value: str) -> bool:
    return not str(value).strip()


def to_string(value: Any) -> str:
    return "" if value is None else str(value)


def merge_indices(indices: list[list[int]]) -> list[list[int]]:
    if len(indices) <= 1:
        return indices
    ordered = sorted(indices, key=lambda item: (item[0], item[1]))
    merged = [ordered[0][:]]
    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1] + 1:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged


def default_get(obj: Any, path: str | list[str]) -> Any:
    parts = path.split(".") if isinstance(path, str) else path
    values: list[Any] = []
    saw_array = False

    def deep_get(current: Any, index: int, array_index: int | None = None) -> None:
        nonlocal saw_array
        if current is None:
            return
        if index >= len(parts):
            values.append({"v": current, "i": array_index} if array_index is not None else current)
            return

        key = parts[index]
        if isinstance(current, dict):
            value = current.get(key)
        else:
            value = getattr(current, key, None)
        if value is None:
            return

        if index == len(parts) - 1 and isinstance(value, (str, int, float, bool)):
            text = to_string(value)
            values.append({"v": text, "i": array_index} if array_index is not None else text)
        elif isinstance(value, list):
            saw_array = True
            for item_index, item in enumerate(value):
                deep_get(item, index + 1, item_index)
        else:
            deep_get(value, index + 1, array_index)

    deep_get(obj, 0)
    return values if saw_array else (values[0] if values else None)


class FieldNorm:
    def __init__(self, weight: float = 1, mantissa: int = 3) -> None:
        self.weight = weight
        self.mantissa = mantissa
        self._cache: dict[int, float] = {}

    def get(self, value: str) -> float:
        num_tokens = 1
        in_space = False
        for ch in value:
            if ch == " ":
                if not in_space:
                    num_tokens += 1
                    in_space = True
            else:
                in_space = False

        if num_tokens not in self._cache:
            multiplier = 10**self.mantissa
            norm = round(multiplier / math.pow(num_tokens, 0.5 * self.weight)) / multiplier
            self._cache[num_tokens] = norm
        return self._cache[num_tokens]

    def clear(self) -> None:
        self._cache.clear()


@dataclass
class Key:
    path: list[str]
    id: str
    src: str | list[str]
    weight: float = 1.0
    get_fn: Callable[[Any], Any] | None = None


def create_key(key: str | list[str] | dict[str, Any]) -> Key:
    weight = 1.0
    get_fn = None
    if isinstance(key, (str, list)):
        src = key
    else:
        if "name" not in key:
            raise ValueError("Missing required key property 'name'")
        src = key["name"]
        weight = float(key.get("weight", 1))
        if weight <= 0:
            raise ValueError(f"Property 'weight' in key '{create_key_id(src)}' must be positive")
        get_fn = key.get("getFn") or key.get("get_fn")

    path = src if isinstance(src, list) else str(src).split(".")
    return Key(path=path, id=create_key_id(src), src=src, weight=weight, get_fn=get_fn)


def create_key_id(key: str | list[str]) -> str:
    return ".".join(key) if isinstance(key, list) else key
