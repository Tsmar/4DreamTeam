from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_search import SearchEngine, create_index, match, parse_index, parse_query
from fourdt_search.records import snippet


class SearchEngineTests(unittest.TestCase):
    def test_fuzzy_scores_matches_and_collection_updates(self) -> None:
        engine = SearchEngine(["Old Man's War", "The Lock Artist"], {"includeScore": True, "includeMatches": True})

        results = engine.search("old")
        self.assertEqual(results[0]["item"], "Old Man's War")
        self.assertLess(results[0]["score"], 0.1)
        self.assertEqual(results[0]["matches"][0]["indices"], [[0, 2]])

        engine.add("Learning Python")
        self.assertEqual(engine.search("pythn")[0]["item"], "Learning Python")
        removed = engine.remove(lambda doc, _idx: doc == "Learning Python")
        self.assertEqual(removed, ["Learning Python"])

    def test_object_keys_extended_logical_token_and_index_roundtrip(self) -> None:
        docs = [
            {"title": "JavaScript Patterns", "author": {"last": "Osmani"}, "body": "JavaScript programming patterns"},
            {"title": "Learning Python", "author": {"last": "Lutz"}, "body": "Python programming language"},
            {"title": "Old Man's War", "author": {"last": "Scalzi"}, "body": "Military science fiction"},
        ]
        options = {
            "keys": ["title", "author.last", "body"],
            "includeScore": True,
            "useExtendedSearch": True,
        }
        engine = SearchEngine(docs, options)
        self.assertEqual(engine.search("^Learning")[0]["item"]["title"], "Learning Python")
        self.assertEqual(engine.search({"$and": [{"title": "old"}, {"author.last": "scazi"}]})[0]["item"]["title"], "Old Man's War")

        token_engine = SearchEngine(docs, {"keys": ["title", "body"], "useTokenSearch": True, "tokenMatch": "all", "threshold": 0.35})
        self.assertEqual(token_engine.search("javascrpt paterns")[0]["item"]["title"], "JavaScript Patterns")

        index = create_index(["title", "body"], docs)
        restored = SearchEngine(docs, {"keys": ["title", "body"]}, parse_index(index.to_json()))
        self.assertEqual(restored.search("python")[0]["item"]["title"], "Learning Python")

        self.assertTrue(match("scazi", "Scalzi")["isMatch"])
        parsed = parse_query({"title": "python"}, {"keys": ["title"]}, auto=False)
        self.assertEqual(parsed["children"][0]["keyId"], "title")

    def test_snippet_prefers_query_context(self) -> None:
        text = "frontmatter value " * 30 + "The wiki role must not read or write wiki storage directly. " + "tail value " * 30
        excerpt = snippet(text, query="wiki storage directly", limit=120)
        self.assertIn("wiki storage directly", excerpt)
        self.assertTrue(excerpt.startswith("..."))
        self.assertTrue(excerpt.endswith("..."))


if __name__ == "__main__":
    unittest.main()
