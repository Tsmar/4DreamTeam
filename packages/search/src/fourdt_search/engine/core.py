from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from .bitap import BitapSearch
from .extended import ExtendedSearch
from .helpers import FieldNorm, Key, create_key, create_key_id, default_get, is_blank, to_string
from .token import (
    MAX_MASK_TERMS,
    InvertedIndex,
    TokenSearch,
    add_to_inverted_index,
    build_inverted_index,
    create_analyzer,
    remove_and_shift_inverted_index,
)


DEFAULT_OPTIONS = {
    "isCaseSensitive": False,
    "ignoreDiacritics": False,
    "includeScore": False,
    "includeMatches": False,
    "findAllMatches": False,
    "minMatchCharLength": 1,
    "keys": [],
    "shouldSort": True,
    "location": 0,
    "threshold": 0.6,
    "distance": 100,
    "ignoreLocation": False,
    "ignoreFieldNorm": False,
    "fieldNormWeight": 1,
    "getFn": default_get,
    "useExtendedSearch": False,
    "useTokenSearch": False,
    "tokenize": None,
    "tokenMatch": "any",
}


def default_sort(a: dict, b: dict) -> int:
    if a["score"] == b["score"]:
        return -1 if a["idx"] < b["idx"] else 1
    return -1 if a["score"] < b["score"] else 1


class KeyStore:
    def __init__(self, keys: list[Any]) -> None:
        self._keys = [create_key(key) for key in keys]
        total_weight = sum(key.weight for key in self._keys)
        if total_weight:
            for key in self._keys:
                key.weight /= total_weight

    def get(self, key_id: str) -> Key:
        for key in self._keys:
            if key.id == key_id:
                return key
        raise KeyError(key_id)

    def keys(self) -> list[Key]:
        return self._keys


class SearchIndex:
    def __init__(self, *, get_fn: Callable = default_get, field_norm_weight: float = 1) -> None:
        self.norm = FieldNorm(field_norm_weight, 3)
        self.get_fn = get_fn
        self.docs: list[Any] = []
        self.records: list[dict] = []
        self.keys: list[Key] = []
        self._keys_map: dict[str, int] = {}
        self.is_created = False

    def set_sources(self, docs: list[Any] | None = None) -> None:
        self.docs = docs or []

    def set_keys(self, keys: list[Key] | None = None) -> None:
        self.keys = keys or []
        self._keys_map = {key.id: index for index, key in enumerate(self.keys)}

    def set_index_records(self, records: list[dict] | None = None) -> None:
        self.records = records or []

    def create(self) -> None:
        if self.is_created or not self.docs:
            return
        self.is_created = True
        if isinstance(self.docs[0], str):
            self.records = [
                record for i, doc in enumerate(self.docs) if (record := self._create_string_record(doc, i))
            ]
        else:
            self.records = [self._create_object_record(doc, i) for i, doc in enumerate(self.docs)]
        self.norm.clear()

    def add(self, doc: Any, doc_index: int) -> dict | None:
        if doc_index < 0:
            raise ValueError("Invalid document index")
        record = self._create_string_record(doc, doc_index) if isinstance(doc, str) else self._create_object_record(doc, doc_index)
        if record:
            self.records.append(record)
        return record

    def remove_at(self, idx: int) -> None:
        if idx < 0:
            raise ValueError("Invalid document index")
        self.records = [record for record in self.records if record["i"] != idx]
        for record in self.records:
            if record["i"] > idx:
                record["i"] -= 1

    def remove_all(self, indices: list[int]) -> None:
        to_remove = {idx for idx in indices if isinstance(idx, int) and idx >= 0}
        if not to_remove:
            return
        self.records = [record for record in self.records if record["i"] not in to_remove]
        ordered = sorted(to_remove)
        for record in self.records:
            shift = sum(1 for idx in ordered if idx < record["i"])
            record["i"] -= shift

    def get_value_for_item_at_key_id(self, item: dict, key_id: str) -> Any:
        return item[self._keys_map[key_id]]

    def size(self) -> int:
        return len(self.records)

    def _create_string_record(self, doc: str, doc_index: int) -> dict | None:
        if doc is None or is_blank(doc):
            return None
        return {"v": doc, "i": doc_index, "n": self.norm.get(doc)}

    def _create_object_record(self, doc: Any, doc_index: int) -> dict:
        record = {"i": doc_index, "$": {}}
        for key_index, key in enumerate(self.keys):
            value = key.get_fn(doc) if key.get_fn else self.get_fn(doc, key.path)
            if value is None:
                continue
            if isinstance(value, list):
                sub_records = []
                for item_index, item in enumerate(value):
                    if item is None:
                        continue
                    if isinstance(item, str):
                        text = item
                        ref_index = item_index
                    elif isinstance(item, dict) and "v" in item:
                        text = item["v"] if isinstance(item["v"], str) else to_string(item["v"])
                        ref_index = item.get("i", item_index)
                    else:
                        continue
                    if not is_blank(text):
                        sub_records.append({"v": text, "i": ref_index, "n": self.norm.get(text)})
                record["$"][key_index] = sub_records
            elif isinstance(value, str) and not is_blank(value):
                record["$"][key_index] = {"v": value, "n": self.norm.get(value)}
            elif isinstance(value, (int, float, bool)):
                text = to_string(value)
                if not is_blank(text):
                    record["$"][key_index] = {"v": text, "n": self.norm.get(text)}
        return record

    def to_json(self) -> dict:
        return {
            "keys": [
                {"path": key.path, "id": key.id, "src": key.src, "weight": key.weight}
                for key in self.keys
            ],
            "records": self.records,
        }


def create_index(keys: list[Any], docs: list[Any], options: dict | None = None) -> SearchIndex:
    options = options or {}
    index = SearchIndex(
        get_fn=options.get("getFn", options.get("get_fn", default_get)),
        field_norm_weight=options.get("fieldNormWeight", options.get("field_norm_weight", 1)),
    )
    index.set_keys([create_key(key) for key in keys])
    index.set_sources(docs)
    index.create()
    return index


def parse_index(data: dict, options: dict | None = None) -> SearchIndex:
    options = options or {}
    index = SearchIndex(
        get_fn=options.get("getFn", options.get("get_fn", default_get)),
        field_norm_weight=options.get("fieldNormWeight", options.get("field_norm_weight", 1)),
    )
    keys = []
    for item in data.get("keys", []):
        key = Key(
            path=item["path"],
            id=item["id"],
            src=item["src"],
            weight=item.get("weight", 1),
            get_fn=item.get("getFn") or item.get("get_fn"),
        )
        keys.append(key)
    index.set_keys(keys)
    index.set_index_records(data.get("records", []))
    return index


class SearchEngine:
    def __init__(self, docs: list[Any], options: dict | None = None, index: SearchIndex | None = None) -> None:
        self.options = {**DEFAULT_OPTIONS, **(options or {})}
        self._key_store = KeyStore(self.options["keys"])
        self._docs = list(docs)
        self._my_index: SearchIndex
        self._inverted_index: InvertedIndex | None = None
        self.set_collection(self._docs, index)

    def set_collection(self, docs: list[Any], index: SearchIndex | None = None) -> None:
        self._docs = list(docs)
        self._my_index = index or create_index(
            self.options["keys"],
            self._docs,
            {"getFn": self.options["getFn"], "fieldNormWeight": self.options["fieldNormWeight"]},
        )
        if self.options.get("useTokenSearch"):
            analyzer = create_analyzer(self.options)
            self._inverted_index = build_inverted_index(
                self._my_index.records,
                len(self._my_index.keys),
                analyzer,
            )
        else:
            self._inverted_index = None

    def add(self, doc: Any) -> None:
        if doc is None:
            return
        self._docs.append(doc)
        record = self._my_index.add(doc, len(self._docs) - 1)
        if self._inverted_index and record:
            add_to_inverted_index(
                self._inverted_index,
                record,
                len(self._my_index.keys),
                create_analyzer(self.options),
            )

    def remove(self, predicate: Callable[[Any, int], bool] | None = None) -> list[Any]:
        predicate = predicate or (lambda _doc, _idx: False)
        removed = []
        indices = []
        for index, doc in enumerate(self._docs):
            if predicate(doc, index):
                removed.append(doc)
                indices.append(index)
        if indices:
            if self._inverted_index:
                remove_and_shift_inverted_index(self._inverted_index, indices)
            to_remove = set(indices)
            self._docs = [doc for index, doc in enumerate(self._docs) if index not in to_remove]
            self._my_index.remove_all(indices)
        return removed

    def remove_at(self, idx: int) -> Any:
        if not isinstance(idx, int) or idx < 0 or idx >= len(self._docs):
            raise ValueError("Invalid document index")
        if self._inverted_index:
            remove_and_shift_inverted_index(self._inverted_index, [idx])
        doc = self._docs.pop(idx)
        self._my_index.remove_at(idx)
        return doc

    def get_index(self) -> SearchIndex:
        return self._my_index

    @staticmethod
    def match(pattern: str, text: str, options: dict | None = None) -> dict:
        opts = {**DEFAULT_OPTIONS, **(options or {})}
        return BitapSearch(
            pattern,
            location=opts["location"],
            threshold=opts["threshold"],
            distance=opts["distance"],
            include_matches=opts["includeMatches"],
            find_all_matches=opts["findAllMatches"],
            min_match_char_length=opts["minMatchCharLength"],
            is_case_sensitive=opts["isCaseSensitive"],
            ignore_diacritics=opts["ignoreDiacritics"],
            ignore_location=opts["ignoreLocation"],
        ).search_in(text)

    @staticmethod
    def parse_query(query: Any, options: dict | None = None, *, auto: bool = True) -> dict:
        search_engine = SearchEngine([], options or {})
        return search_engine._parse_logical_query(query, auto=auto)

    def search(self, query: str, options: dict | None = None) -> list[dict]:
        options = options or {}
        limit = options.get("limit", -1)
        if isinstance(query, str) and not query.strip():
            results = [{"item": item, "refIndex": idx} for idx, item in enumerate(self._docs)]
            return results[:limit] if isinstance(limit, int) and limit > -1 else results

        if isinstance(query, str):
            if self._docs and isinstance(self._docs[0], str):
                results = self._search_string_list(query)
            else:
                results = self._search_object_list(query)
        else:
            results = self._search_logical(query)

        self._compute_score(results)
        if self.options["shouldSort"]:
            results.sort(key=lambda result: (result["score"], result["idx"]))
        if isinstance(limit, int) and limit > -1:
            results = results[:limit]
        return self._format(results)

    def _create_searcher(self, query: str) -> BitapSearch:
        if self.options.get("useTokenSearch"):
            if not self._inverted_index:
                self._inverted_index = build_inverted_index(
                    self._my_index.records,
                    len(self._my_index.keys),
                    create_analyzer(self.options),
                )
            return TokenSearch(query, self.options, self._inverted_index)  # type: ignore[return-value]
        if self.options.get("useExtendedSearch"):
            return ExtendedSearch(query, self.options)  # type: ignore[return-value]
        return BitapSearch(
            query,
            location=self.options["location"],
            threshold=self.options["threshold"],
            distance=self.options["distance"],
            include_matches=self.options["includeMatches"],
            find_all_matches=self.options["findAllMatches"],
            min_match_char_length=self.options["minMatchCharLength"],
            is_case_sensitive=self.options["isCaseSensitive"],
            ignore_diacritics=self.options["ignoreDiacritics"],
            ignore_location=self.options["ignoreLocation"],
        )

    def _search_string_list(self, query: str) -> list[dict]:
        searcher = self._create_searcher(query)
        require_all_tokens = self.options.get("useTokenSearch") and self.options.get("tokenMatch") == "all"
        results = []
        for record in self._my_index.records:
            text = record.get("v")
            if text is None:
                continue
            result = searcher.search_in(text)
            if result["isMatch"]:
                match = {
                    "score": result["score"],
                    "value": text,
                    "norm": record["n"],
                    "indices": result.get("indices"),
                }
                if "termCount" in result:
                    match["matchedMask"] = result.get("matchedMask", 0)
                    match["matchedTerms"] = result.get("matchedTerms")
                    match["termCount"] = result["termCount"]
                if not require_all_tokens or self._covers_all_tokens([match]):
                    results.append({"item": text, "idx": record["i"], "matches": [match]})
        return results

    def _search_object_list(self, query: str) -> list[dict]:
        searcher = self._create_searcher(query)
        require_all_tokens = self.options.get("useTokenSearch") and self.options.get("tokenMatch") == "all"
        results = []
        for record in self._my_index.records:
            item = record.get("$")
            if item is None:
                continue
            matches = []
            any_key_failed = False
            has_inverse = False
            for key_index, key in enumerate(self._my_index.keys):
                key_matches = self._find_matches(key, item.get(key_index), searcher)
                if key_matches:
                    matches.extend(key_matches)
                    if key_matches[0].get("hasInverse"):
                        has_inverse = True
                else:
                    any_key_failed = True
            if has_inverse and any_key_failed:
                continue
            if matches and (not require_all_tokens or self._covers_all_tokens(matches)):
                results.append({"idx": record["i"], "item": item, "matches": matches})
        return results

    def _find_matches(self, key: Key, value: Any, searcher: BitapSearch) -> list[dict]:
        if value is None:
            return []
        matches = []
        values = value if isinstance(value, list) else [value]
        for item in values:
            text = item.get("v")
            if text is None:
                continue
            result = searcher.search_in(text)
            if result["isMatch"]:
                match = {
                    "score": result["score"],
                    "key": key,
                    "value": text,
                    "idx": item.get("i", -1),
                    "norm": item["n"],
                    "indices": result.get("indices"),
                    "hasInverse": result.get("hasInverse"),
                }
                if "termCount" in result:
                    match["matchedMask"] = result.get("matchedMask", 0)
                    match["matchedTerms"] = result.get("matchedTerms")
                    match["termCount"] = result["termCount"]
                matches.append(match)
        return matches

    def _search_logical(self, query: Any) -> list[dict]:
        expression = self._parse_logical_query(query)

        def evaluate(node: dict, item: dict, idx: int) -> list[dict]:
            if "children" not in node:
                key_id = node["keyId"]
                searcher = node["searcher"]
                if key_id is None:
                    matches = []
                    for key_index, key in enumerate(self._my_index.keys):
                        matches.extend(self._find_matches(key, item.get(key_index), searcher))
                else:
                    key = self._key_store.get(key_id)
                    matches = self._find_matches(key, self._my_index.get_value_for_item_at_key_id(item, key_id), searcher)
                return [{"idx": idx, "item": item, "matches": matches}] if matches else []

            results = []
            for child in node["children"]:
                child_results = evaluate(child, item, idx)
                if child_results:
                    results.extend(child_results)
                elif node["operator"] == "$and":
                    return []
            return results

        result_map: dict[int, dict] = {}
        results: list[dict] = []
        for record in self._my_index.records:
            item = record.get("$")
            if item is None:
                continue
            exp_results = evaluate(expression, item, record["i"])
            if exp_results:
                if record["i"] not in result_map:
                    result_map[record["i"]] = {"idx": record["i"], "item": item, "matches": []}
                    results.append(result_map[record["i"]])
                for exp_result in exp_results:
                    result_map[record["i"]]["matches"].extend(exp_result["matches"])
        return results

    def _parse_logical_query(self, query: Any, *, auto: bool = True) -> dict:
        def is_expression(value: Any) -> bool:
            return isinstance(value, dict) and ("$and" in value or "$or" in value)

        def is_path(value: Any) -> bool:
            return isinstance(value, dict) and "$path" in value

        def convert_to_explicit(value: dict) -> dict:
            return {"$and": [{key: val} for key, val in value.items()]}

        def next_node(value: Any) -> dict:
            if isinstance(value, str):
                node = {"keyId": None, "pattern": value}
                if auto:
                    node["searcher"] = self._create_searcher(value)
                return node
            if not isinstance(value, dict):
                raise ValueError("Logical query nodes must be strings or dictionaries")

            keys = list(value.keys())
            query_path = is_path(value)
            if not query_path and len(keys) > 1 and not is_expression(value):
                return next_node(convert_to_explicit(value))

            if not is_expression(value):
                key = value["$path"] if query_path else keys[0]
                pattern = value["$val"] if query_path else value[key]
                if not isinstance(pattern, str):
                    raise ValueError(f"Invalid logical query for key {key}")
                node = {
                    "keyId": create_key_id(key),
                    "pattern": pattern,
                }
                if auto:
                    node["searcher"] = self._create_searcher(pattern)
                return node

            operator = keys[0]
            children = []
            for item in value.get(operator, []):
                children.append(next_node(item))
            return {"children": children, "operator": operator}

        if not is_expression(query):
            query = convert_to_explicit(query)
        return next_node(query)

    def _covers_all_tokens(self, matches: list[dict]) -> bool:
        term_count = matches[0].get("termCount") if matches else None
        if term_count is None:
            return True
        if term_count <= MAX_MASK_TERMS:
            coverage = 0
            for match in matches:
                coverage |= match.get("matchedMask", 0)
            return coverage == 2**term_count - 1
        coverage: set[int] = set()
        for match in matches:
            coverage.update(match.get("matchedTerms") or set())
        return len(coverage) == term_count

    def _compute_score(self, results: list[dict]) -> None:
        ignore_field_norm = self.options["ignoreFieldNorm"]
        for result in results:
            total_score = 1.0
            for match in result["matches"]:
                key = match.get("key")
                weight = key.weight if key else None
                score = match["score"]
                if score == 0 and weight:
                    score = 2.220446049250313e-16
                total_score *= math.pow(score, (weight or 1) * (1 if ignore_field_norm else match["norm"]))
            result["score"] = total_score

    def _format(self, results: list[dict]) -> list[dict]:
        formatted = []
        for result in results:
            data = {"item": self._docs[result["idx"]], "refIndex": result["idx"]}
            if self.options["includeMatches"]:
                data["matches"] = []
                for match in result["matches"]:
                    indices = match.get("indices")
                    if not indices:
                        continue
                    item = {"indices": indices, "value": match["value"]}
                    key = match.get("key")
                    if key:
                        item["key"] = key.src
                    if match.get("idx", -1) > -1:
                        item["refIndex"] = match["idx"]
                    data["matches"].append(item)
            if self.options["includeScore"]:
                data["score"] = result["score"]
            formatted.append(data)
        return formatted
