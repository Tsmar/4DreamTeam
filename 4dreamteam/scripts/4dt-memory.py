#!/usr/bin/env python3
from __future__ import annotations

from run_tool import main


if __name__ == "__main__":
    raise SystemExit(main(["memory", *__import__("sys").argv[1:]]))
