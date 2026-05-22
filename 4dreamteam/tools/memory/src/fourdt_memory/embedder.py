from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Protocol


TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
HASH_DIMENSIONS = 16


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def lexical_score(query: str, text: str) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0
    text_tokens = set(tokenize(text))
    if not text_tokens:
        return 0.0
    return len(query_tokens & text_tokens) / len(query_tokens)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class EmbeddingProvider(Protocol):
    name: str
    model: str
    supports_vectors: bool

    def embed(self, text: str) -> list[float]:
        ...


@dataclass(frozen=True)
class NoneEmbeddingProvider:
    name: str = "none"
    model: str = "lexical"
    supports_vectors: bool = False

    def embed(self, text: str) -> list[float]:
        return []


@dataclass(frozen=True)
class HashEmbeddingProvider:
    name: str = "hash"
    model: str = "sha256-16"
    supports_vectors: bool = True

    def embed(self, text: str) -> list[float]:
        buckets = [0.0] * HASH_DIMENSIONS
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = digest[0] % HASH_DIMENSIONS
            sign = 1.0 if digest[1] % 2 == 0 else -1.0
            buckets[index] += sign
        norm = math.sqrt(sum(value * value for value in buckets))
        if norm == 0:
            return buckets
        return [value / norm for value in buckets]


def provider_key(provider: EmbeddingProvider) -> str:
    return f"{provider.name}:{provider.model}"


def provider_from_args(name: str | None, model: str | None = None) -> EmbeddingProvider:
    provider_name = name or "none"
    if provider_name == "none":
        return NoneEmbeddingProvider(model=model or "lexical")
    if provider_name == "hash":
        return HashEmbeddingProvider(model=model or "sha256-16")
    raise ValueError(f"unsupported provider: {provider_name}")
