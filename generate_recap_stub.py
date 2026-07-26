#!/usr/bin/env python3
"""兼容入口 · 转发到 skills/market-recap/scripts/generate_recap_stub.py"""
from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent / "skills/market-recap/scripts/generate_recap_stub.py"),
    run_name="__main__",
)