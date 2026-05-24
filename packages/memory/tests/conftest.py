from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
SEARCH_SRC_DIR = Path(__file__).resolve().parents[2] / "search" / "src"
sys.path.insert(0, str(SEARCH_SRC_DIR))
sys.path.insert(0, str(SRC_DIR))
