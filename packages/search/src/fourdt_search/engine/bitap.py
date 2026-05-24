from __future__ import annotations

from dataclasses import dataclass

from .helpers import merge_indices, strip_diacritics

MAX_BITS = 32


def create_pattern_alphabet(pattern: str) -> dict[str, int]:
    mask: dict[str, int] = {}
    length = len(pattern)
    for index, char in enumerate(pattern):
        mask[char] = mask.get(char, 0) | (1 << (length - index - 1))
    return mask


def convert_mask_to_indices(match_mask: list[int], min_match_char_length: int = 1) -> list[list[int]]:
    indices: list[list[int]] = []
    start = -1
    i = 0
    for i, match in enumerate(match_mask):
        if match and start == -1:
            start = i
        elif not match and start != -1:
            end = i - 1
            if end - start + 1 >= min_match_char_length:
                indices.append([start, end])
            start = -1
    if match_mask and match_mask[-1] and start != -1 and len(match_mask) - start >= min_match_char_length:
        indices.append([start, len(match_mask) - 1])
    return indices


def bitap_search(
    text: str,
    pattern: str,
    pattern_alphabet: dict[str, int],
    *,
    location: int = 0,
    distance: int = 100,
    threshold: float = 0.6,
    find_all_matches: bool = False,
    min_match_char_length: int = 1,
    include_matches: bool = False,
    ignore_location: bool = False,
) -> dict:
    if len(pattern) > MAX_BITS:
        raise ValueError(f"Pattern length exceeds max of {MAX_BITS}.")

    pattern_len = len(pattern)
    text_len = len(text)
    expected_location = max(0, min(location, text_len))
    current_threshold = threshold
    best_location = expected_location

    def calc_score(errors: int, current_location: int) -> float:
        accuracy = errors / pattern_len
        if ignore_location:
            return accuracy
        proximity = abs(expected_location - current_location)
        if not distance:
            return 1.0 if proximity else accuracy
        return accuracy + proximity / distance

    compute_matches = min_match_char_length > 1 or include_matches
    match_mask = [0] * text_len if compute_matches else []

    index = text.find(pattern, best_location)
    while index > -1:
        score = calc_score(0, index)
        current_threshold = min(score, current_threshold)
        best_location = index + pattern_len
        if compute_matches:
            for offset in range(pattern_len):
                if index + offset < text_len:
                    match_mask[index + offset] = 1
        index = text.find(pattern, best_location)

    best_location = -1
    last_bit_arr: list[int] = []
    final_score = 1.0
    best_errors = 0
    bin_max = pattern_len + text_len
    mask = 1 << (pattern_len - 1)

    for errors in range(pattern_len):
        bin_min = 0
        bin_mid = bin_max
        while bin_min < bin_mid:
            score = calc_score(errors, expected_location + bin_mid)
            if score <= current_threshold:
                bin_min = bin_mid
            else:
                bin_max = bin_mid
            bin_mid = (bin_max - bin_min) // 2 + bin_min

        bin_max = bin_mid
        start = max(1, expected_location - bin_mid + 1)
        finish = text_len if find_all_matches else min(expected_location + bin_mid, text_len) + pattern_len
        bit_arr = [0] * (finish + 2)
        bit_arr[finish + 1] = (1 << errors) - 1

        j = finish
        while j >= start:
            current_location = j - 1
            char_match = pattern_alphabet.get(text[current_location], 0) if current_location < text_len else 0
            bit_arr[j] = ((bit_arr[j + 1] << 1) | 1) & char_match
            if errors:
                bit_arr[j] |= ((last_bit_arr[j + 1] | last_bit_arr[j]) << 1) | 1 | last_bit_arr[j + 1]

            if bit_arr[j] & mask:
                final_score = calc_score(errors, current_location)
                if final_score <= current_threshold:
                    current_threshold = final_score
                    best_location = current_location
                    best_errors = errors
                    if best_location <= expected_location:
                        break
                    start = max(1, 2 * expected_location - best_location)
            j -= 1

        if calc_score(errors + 1, expected_location) > current_threshold:
            break
        last_bit_arr = bit_arr

    if compute_matches and best_location >= 0:
        match_end = min(text_len - 1, best_location + pattern_len - 1 + best_errors)
        for index in range(best_location, match_end + 1):
            if pattern_alphabet.get(text[index]):
                match_mask[index] = 1

    result = {"isMatch": best_location >= 0, "score": max(0.001, final_score)}
    if compute_matches:
        indices = convert_mask_to_indices(match_mask, min_match_char_length)
        if not indices:
            result["isMatch"] = False
        elif include_matches:
            result["indices"] = indices
    return result


@dataclass
class BitapSearch:
    pattern: str
    location: int = 0
    threshold: float = 0.6
    distance: int = 100
    include_matches: bool = False
    find_all_matches: bool = False
    min_match_char_length: int = 1
    is_case_sensitive: bool = False
    ignore_diacritics: bool = False
    ignore_location: bool = False

    def __post_init__(self) -> None:
        pattern = self.pattern if self.is_case_sensitive else self.pattern.lower()
        self.pattern = strip_diacritics(pattern) if self.ignore_diacritics else pattern
        self.chunks: list[dict] = []
        if not self.pattern:
            return
        length = len(self.pattern)
        if length > MAX_BITS:
            i = 0
            remainder = length % MAX_BITS
            end = length - remainder
            while i < end:
                self._add_chunk(self.pattern[i : i + MAX_BITS], i)
                i += MAX_BITS
            if remainder:
                start_index = length - MAX_BITS
                self._add_chunk(self.pattern[start_index:], start_index)
        else:
            self._add_chunk(self.pattern, 0)

    def _add_chunk(self, pattern: str, start_index: int) -> None:
        self.chunks.append(
            {"pattern": pattern, "alphabet": create_pattern_alphabet(pattern), "startIndex": start_index}
        )

    def search_in(self, text: str) -> dict:
        text = text if self.is_case_sensitive else text.lower()
        text = strip_diacritics(text) if self.ignore_diacritics else text
        if self.pattern == text:
            result = {"isMatch": True, "score": 0}
            if self.include_matches:
                result["indices"] = [[0, len(text) - 1]]
            return result

        all_indices: list[list[int]] = []
        total_score = 0.0
        has_matches = False
        for chunk in self.chunks:
            result = bitap_search(
                text,
                chunk["pattern"],
                chunk["alphabet"],
                location=self.location + chunk["startIndex"],
                distance=self.distance,
                threshold=self.threshold,
                find_all_matches=self.find_all_matches,
                min_match_char_length=self.min_match_char_length,
                include_matches=self.include_matches,
                ignore_location=self.ignore_location,
            )
            has_matches = has_matches or result["isMatch"]
            total_score += result["score"]
            if result["isMatch"] and "indices" in result:
                all_indices.extend(result["indices"])

        result = {
            "isMatch": has_matches,
            "score": total_score / len(self.chunks) if has_matches and self.chunks else 1,
        }
        if has_matches and self.include_matches:
            result["indices"] = merge_indices(all_indices)
        return result
