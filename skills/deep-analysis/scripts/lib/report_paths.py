from __future__ import annotations

from datetime import datetime
from pathlib import Path

from lib.cache import read_task_output

INVALID_FS_CHARS = '<>:"/\\|?*'


def _sanitize_report_name(name: str | None) -> str:
    if not name:
        return ""
    cleaned = "".join("_" if ch in INVALID_FS_CHARS else ch for ch in str(name).strip())
    cleaned = cleaned.replace("\n", " ").replace("\r", " ").strip(" ._")
    return cleaned


def get_report_display_name(ticker: str) -> str:
    syn = read_task_output(ticker, "synthesis") or {}
    raw = read_task_output(ticker, "raw_data") or {}
    basic = raw.get("basic") or {}
    return _sanitize_report_name(syn.get("name") or basic.get("name"))


def build_report_dir_name(ticker: str, date: str | None = None, name: str | None = None) -> str:
    report_date = date or datetime.now().strftime("%Y%m%d")
    display_name = _sanitize_report_name(name) if name is not None else get_report_display_name(ticker)
    if display_name:
        return f"{ticker}_{display_name}_{report_date}"
    return f"{ticker}_{report_date}"


def build_report_dir(root: str | Path, ticker: str, date: str | None = None, name: str | None = None) -> Path:
    return Path(root) / build_report_dir_name(ticker, date=date, name=name)
