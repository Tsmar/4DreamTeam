from __future__ import annotations

import math
import re
from typing import Any, Callable

from .bitap import BitapSearch
from .helpers import merge_indices, strip_diacritics

MAX_MASK_TERMS = 31
DEFAULT_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


class Analyzer:
    def __init__(
        self,
        *,
        is_case_sensitive: bool = False,
        ignore_diacritics: bool = False,
        tokenize: re.Pattern | Callable[[str], list[str]] | None = None,
    ) -> None:
        self.is_case_sensitive = is_case_sensitive
        self.ignore_diacritics = ignore_diacritics
        self.tokenize_fn = tokenize

    def tokenize(self, text: str) -> list[str]:
        if not self.is_case_sensitive:
            text = text.lower()
        if self.ignore_diacritics:
            text = strip_diacritics(text)
        if callable(self.tokenize_fn) and not isinstance(self.tokenize_fn, re.Pattern):
            return self.tokenize_fn(text)
        if isinstance(self.tokenize_fn, re.Pattern):
            return self.tokenize_fn.findall(text)
        return DEFAULT_TOKEN_RE.findall(text)


def create_analyzer(options: dict[str, Any]) -> Analyzer:
    return Analyzer(
        is_case_sensitive=options.get("isCaseSensitive", False),
        ignore_diacritics=options.get("ignoreDiacritics", False),
        tokenize=options.get("tokenize"),
    )


class InvertedIndex:
    def __init__(self) -> None:
        self.field_count = 0
        self.df: dict[str, int] = {}
        self.doc_field_count: dict[int, int] = {}
        self.doc_term_field_hits: dict[int, dict[str, int]] = {}


def _add_field(index: InvertedIndex, text: str, doc_idx: int, analyzer: Analyzer) -> None:
    tokens = analyzer.tokenize(text)
    if not tokens:
        return
    index.field_count += 1
    index.doc_field_count[doc_idx] = index.doc_field_count.get(doc_idx, 0) + 1
    per_doc_terms = index.doc_term_field_hits.setdefault(doc_idx, {})
    for term in set(tokens):
        per_doc_terms[term] = per_doc_terms.get(term, 0) + 1
        index.df[term] = index.df.get(term, 0) + 1


def _ingest_record(index: InvertedIndex, record: dict, key_count: int, analyzer: Analyzer) -> None:
    doc_idx = record["i"]
    if "v" in record:
        _add_field(index, record["v"], doc_idx, analyzer)
        return
    fields = record.get("$") or {}
    for key_idx in range(key_count):
        value = fields.get(key_idx)
        if not value:
            continue
        if isinstance(value, list):
            for sub in value:
                _add_field(index, sub["v"], doc_idx, analyzer)
        else:
            _add_field(index, value["v"], doc_idx, analyzer)


def build_inverted_index(records: list[dict], key_count: int, analyzer: Analyzer) -> InvertedIndex:
    index = InvertedIndex()
    for record in records:
        _ingest_record(index, record, key_count, analyzer)
    return index


def add_to_inverted_index(index: InvertedIndex, record: dict, key_count: int, analyzer: Analyzer) -> None:
    _ingest_record(index, record, key_count, analyzer)


def remove_from_inverted_index(index: InvertedIndex, doc_idx: int) -> None:
    field_count = index.doc_field_count.pop(doc_idx, None)
    if field_count is None:
        return
    index.field_count -= field_count
    per_doc_terms = index.doc_term_field_hits.pop(doc_idx, None)
    if not per_doc_terms:
        return
    for term, hits in per_doc_terms.items():
        next_value = index.df.get(term, 0) - hits
        if next_value <= 0:
            index.df.pop(term, None)
        else:
            index.df[term] = next_value


def remove_and_shift_inverted_index(index: InvertedIndex, removed_indices: list[int]) -> None:
    if not removed_indices:
        return
    sorted_indices = sorted(set(removed_indices))
    for idx in sorted_indices:
        remove_from_inverted_index(index, idx)

    def shift(old_idx: int) -> int:
        return old_idx - sum(1 for idx in sorted_indices if idx < old_idx)

    first_removed = sorted_indices[0]
    index.doc_field_count = {
        (shift(old_key) if old_key > first_removed else old_key): count
        for old_key, count in index.doc_field_count.items()
    }
    index.doc_term_field_hits = {
        (shift(old_key) if old_key > first_removed else old_key): terms
        for old_key, terms in index.doc_term_field_hits.items()
    }


class TokenSearch:
    def __init__(self, pattern: str, options: dict[str, Any], inverted_index: InvertedIndex) -> None:
        self.options = options
        self.analyzer = create_analyzer(options)
        query_terms = self.analyzer.tokenize(pattern)
        self.term_searchers = [
            BitapSearch(
                term,
                location=options["location"],
                threshold=options["threshold"],
                distance=options["distance"],
                include_matches=options["includeMatches"],
                find_all_matches=options["findAllMatches"],
                min_match_char_length=options["minMatchCharLength"],
                is_case_sensitive=options["isCaseSensitive"],
                ignore_diacritics=options["ignoreDiacritics"],
                ignore_location=True,
            )
            for term in query_terms
        ]
        self.idf_weights = []
        for term in query_terms:
            doc_freq = inverted_index.df.get(term, 0)
            idf = math.log(1 + (inverted_index.field_count - doc_freq + 0.5) / (doc_freq + 0.5))
            self.idf_weights.append(idf)
        self.combine_all = options.get("tokenMatch") == "all"
        self.num_terms = len(self.term_searchers)
        self.use_mask = self.num_terms <= MAX_MASK_TERMS

    def search_in(self, text: str) -> dict:
        if not self.term_searchers:
            return {"isMatch": False, "score": 1}

        all_indices: list[list[int]] = []
        weighted_score = 0.0
        max_possible_score = 0.0
        matched_count = 0
        matched_mask = 0
        matched_terms: set[int] = set()

        for index, searcher in enumerate(self.term_searchers):
            result = searcher.search_in(text)
            idf = self.idf_weights[index]
            max_possible_score += idf
            if result["isMatch"]:
                matched_count += 1
                weighted_score += idf * (1 - result["score"])
                if result.get("indices"):
                    all_indices.extend(result["indices"])
                if self.combine_all:
                    if self.use_mask:
                        matched_mask |= 1 << index
                    else:
                        matched_terms.add(index)

        if matched_count == 0:
            return {"isMatch": False, "score": 1}

        normalized = 1 - weighted_score / max_possible_score if max_possible_score > 0 else 0
        output = {"isMatch": True, "score": max(0.001, normalized)}
        if self.options["includeMatches"] and all_indices:
            output["indices"] = merge_indices(all_indices)
        if self.combine_all:
            if self.use_mask:
                output["matchedMask"] = matched_mask
            else:
                output["matchedTerms"] = matched_terms
            output["termCount"] = self.num_terms
        return output
