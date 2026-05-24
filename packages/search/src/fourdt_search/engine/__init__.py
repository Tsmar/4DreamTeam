"""Native 4DT search engine."""

from .core import SearchEngine as SearchEngine
from .core import SearchIndex as SearchIndex
from .core import create_index, parse_index

match = SearchEngine.match
parse_query = SearchEngine.parse_query

__all__ = ["SearchEngine", "SearchIndex", "create_index", "parse_index", "match", "parse_query"]
