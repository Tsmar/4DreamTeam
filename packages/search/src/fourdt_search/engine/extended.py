from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from .bitap import BitapSearch
from .helpers import merge_indices, strip_diacritics

ESCAPED_PIPE = "\x00"
OR_TOKEN = "|"
MULTI_MATCH_TYPES = {"fuzzy", "include"}


@dataclass
class Matcher:
    type: str
    search: Callable[[str], dict]


def is_inverse(matcher_type: str) -> bool:
    return matcher_type.startswith("inverse")


def _find_all(text: str, pattern: str) -> list[list[int]]:
    indices: list[list[int]] = []
    location = 0
    pattern_len = len(pattern)
    while True:
        index = text.find(pattern, location)
        if index == -1:
            return indices
        location = index + pattern_len
        indices.append([index, location - 1])


def _matcher_defs(options: dict[str, Any]) -> list[tuple[str, re.Pattern, re.Pattern, Callable[[str], Matcher]]]:
    def exact(pattern: str) -> Matcher:
        return Matcher(
            "exact",
            lambda text: {
                "isMatch": text == pattern,
                "score": 0 if text == pattern else 1,
                "indices": [0, len(pattern) - 1],
            },
        )

    def include(pattern: str) -> Matcher:
        def search(text: str) -> dict:
            indices = _find_all(text, pattern)
            return {"isMatch": bool(indices), "score": 0 if indices else 1, "indices": indices}

        return Matcher("include", search)

    def prefix(pattern: str) -> Matcher:
        return Matcher(
            "prefix-exact",
            lambda text: {
                "isMatch": text.startswith(pattern),
                "score": 0 if text.startswith(pattern) else 1,
                "indices": [0, len(pattern) - 1],
            },
        )

    def inverse_prefix(pattern: str) -> Matcher:
        return Matcher(
            "inverse-prefix-exact",
            lambda text: {
                "isMatch": not text.startswith(pattern),
                "score": 0 if not text.startswith(pattern) else 1,
                "indices": [0, len(text) - 1],
            },
        )

    def inverse_suffix(pattern: str) -> Matcher:
        return Matcher(
            "inverse-suffix-exact",
            lambda text: {
                "isMatch": not text.endswith(pattern),
                "score": 0 if not text.endswith(pattern) else 1,
                "indices": [0, len(text) - 1],
            },
        )

    def suffix(pattern: str) -> Matcher:
        return Matcher(
            "suffix-exact",
            lambda text: {
                "isMatch": text.endswith(pattern),
                "score": 0 if text.endswith(pattern) else 1,
                "indices": [len(text) - len(pattern), len(text) - 1],
            },
        )

    def inverse_exact(pattern: str) -> Matcher:
        return Matcher(
            "inverse-exact",
            lambda text: {
                "isMatch": text.find(pattern) == -1,
                "score": 0 if text.find(pattern) == -1 else 1,
                "indices": [0, len(text) - 1],
            },
        )

    def fuzzy(pattern: str) -> Matcher:
        bitap = BitapSearch(
            pattern,
            location=options["location"],
            threshold=options["threshold"],
            distance=options["distance"],
            include_matches=options["includeMatches"],
            find_all_matches=options["findAllMatches"],
            min_match_char_length=options["minMatchCharLength"],
            is_case_sensitive=options["isCaseSensitive"],
            ignore_diacritics=options["ignoreDiacritics"],
            ignore_location=options["ignoreLocation"],
        )
        return Matcher("fuzzy", bitap.search_in)

    return [
        ("exact", re.compile(r'^="(.*)"$'), re.compile(r"^=(.*)$"), exact),
        ("include", re.compile(r'^\'"(.*)"$'), re.compile(r"^'(.*)$"), include),
        ("prefix-exact", re.compile(r'^\^"(.*)"$'), re.compile(r"^\^(.*)$"), prefix),
        ("inverse-prefix-exact", re.compile(r'^!\^"(.*)"$'), re.compile(r"^!\^(.*)$"), inverse_prefix),
        ("inverse-suffix-exact", re.compile(r'^!"(.*)"\$$'), re.compile(r"^!(.*)\$$"), inverse_suffix),
        ("suffix-exact", re.compile(r'^"(.*)"\$$'), re.compile(r"^(.*)\$$"), suffix),
        ("inverse-exact", re.compile(r'^!"(.*)"$'), re.compile(r"^!(.*)$"), inverse_exact),
        ("fuzzy", re.compile(r'^"(.*)"$'), re.compile(r"^(.*)$"), fuzzy),
    ]


def _tokenize(pattern: str) -> list[str]:
    tokens: list[str] = []
    length = len(pattern)
    i = 0
    while i < length:
        while i < length and pattern[i] == " ":
            i += 1
        if i >= length:
            break
        j = i
        while j < length and pattern[j] != " " and pattern[j] != '"':
            j += 1
        if j < length and pattern[j] == '"':
            j += 1
            while j < length:
                if pattern[j] == '"':
                    nxt = j + 1
                    if nxt >= length or pattern[nxt] == " ":
                        j += 1
                        break
                    if pattern[nxt] == "$" and (nxt + 1 >= length or pattern[nxt + 1] == " "):
                        j += 2
                        break
                j += 1
            tokens.append(pattern[i:j])
            i = j
        else:
            while j < length and pattern[j] != " ":
                j += 1
            tokens.append(pattern[i:j])
            i = j
    return tokens


def parse_extended_query(pattern: str, options: dict[str, Any]) -> list[list[Matcher]]:
    escaped = pattern.replace(r"\|", ESCAPED_PIPE)
    groups = []
    for item in escaped.split(OR_TOKEN):
        restored = item.replace(ESCAPED_PIPE, "|")
        query = [token for token in _tokenize(restored.strip()) if token.strip()]
        results: list[Matcher] = []
        for query_item in query:
            found = False
            for _typ, multi_regex, _single_regex, create in _matcher_defs(options):
                match = multi_regex.match(query_item)
                if match and match.group(1):
                    results.append(create(match.group(1)))
                    found = True
                    break
            if found:
                continue
            for _typ, _multi_regex, single_regex, create in _matcher_defs(options):
                match = single_regex.match(query_item)
                if match and match.group(1):
                    results.append(create(match.group(1)))
                    break
        groups.append(results)
    return groups


class ExtendedSearch:
    def __init__(self, pattern: str, options: dict[str, Any]) -> None:
        self.options = options
        pattern = pattern if options["isCaseSensitive"] else pattern.lower()
        self.pattern = strip_diacritics(pattern) if options["ignoreDiacritics"] else pattern
        self.query = parse_extended_query(self.pattern, options)

    def search_in(self, text: str) -> dict:
        if not self.query:
            return {"isMatch": False, "score": 1}
        text = text if self.options["isCaseSensitive"] else text.lower()
        text = strip_diacritics(text) if self.options["ignoreDiacritics"] else text

        total_score = 0.0
        for searchers in self.query:
            all_indices: list[list[int]] = []
            num_matches = 0
            has_inverse = False
            for matcher in searchers:
                result = matcher.search(text)
                if result["isMatch"]:
                    num_matches += 1
                    total_score += result["score"]
                    if is_inverse(matcher.type):
                        has_inverse = True
                    if self.options["includeMatches"]:
                        indices = result.get("indices")
                        if indices and matcher.type in MULTI_MATCH_TYPES:
                            all_indices.extend(indices)
                        elif indices:
                            all_indices.append(indices)
                else:
                    total_score = 0
                    num_matches = 0
                    all_indices = []
                    has_inverse = False
                    break
            if num_matches:
                output = {"isMatch": True, "score": total_score / num_matches}
                if has_inverse:
                    output["hasInverse"] = True
                if self.options["includeMatches"]:
                    output["indices"] = merge_indices(all_indices)
                return output
        return {"isMatch": False, "score": 1}
