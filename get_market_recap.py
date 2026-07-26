#!/usr/bin/env python3
"""兼容入口 · 转发到 skills/market-recap/scripts/get_market_recap.py"""
from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent / "skills/market-recap/scripts/get_market_recap.py"),
    run_name="__main__",
)