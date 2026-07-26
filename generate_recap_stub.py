#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 market_data_today.json 生成 UZI 每日复盘骨架（第 2、3 节）。

用法:
  python get_market_recap.py
  python generate_recap_stub.py
  python generate_recap_stub.py --date 2026-06-20 --compare docs/market-recaps/2026-06-19_今日复盘.md
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_JSON = ROOT / "market_data_today.json"
DEFAULT_OUT_DIR = ROOT / "docs" / "market-recaps"


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"找不到数据文件: {path}，请先运行 python get_market_recap.py")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def parse_previous_sentiment(recap_path: Path) -> dict[str, str]:
    """从上一篇复盘提取情绪温度表格，用于「对比昨日」列。"""
    if not recap_path.is_file():
        return {}
    text = recap_path.read_text(encoding="utf-8")
    section = re.search(r"## 3\. 情绪温度\n\n\| 指标 \| 数值.*?\n\n", text, re.S)
    if not section:
        return {}
    rows = re.findall(r"\| ([^|]+) \| \*\*([^*]+)\*\*", section.group(0))
    return {label.strip(): value.strip() for label, value in rows}


def fmt_pct(value: float | int | None) -> str:
    if value is None:
        return "—"
    return f"{value:+.2f}%"


def fmt_num(value: int | float | None) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def compare_cell(today: str, previous: str | None) -> str:
    if not previous:
        return "—"
    if today == previous:
        return "持平"
    return previous


def build_section_indices(indices: dict) -> list[str]:
    lines = [
        "## 2. 指数与量能",
        "",
        "| 指数 | 收盘 | 涨跌幅 |",
        "|------|------|--------|",
    ]
    for name, item in indices.items():
        close = fmt_num(item.get("close"))
        change_pct = fmt_pct(item.get("change_pct"))
        lines.append(f"| {name} | **{close}** | **{change_pct}** |")
    lines.extend(
        [
            "",
            "**量能特征**：",
            "- 两市成交额：____（较昨日 ____）",
            "",
            "**关键信号**：",
            "1. ____",
            "2. ____",
            "",
        ]
    )
    return lines


def build_section_sentiment(data: dict, previous: dict[str, str]) -> list[str]:
    stat = data.get("market_stat") or {}
    limit_up = data.get("limit_up") or {}
    limit_down = data.get("limit_down") or {}
    broken = data.get("broken_limit") or {}
    seal_rate = data.get("seal_rate")

    rows = [
        ("上涨家数", fmt_num(stat.get("up_count"))),
        ("下跌家数", fmt_num(stat.get("down_count"))),
        ("平盘家数", fmt_num(stat.get("flat_count"))),
        ("涨停家数", fmt_num(limit_up.get("count"))),
        ("跌停家数", fmt_num(limit_down.get("count"))),
        ("炸板家数", fmt_num(broken.get("count"))),
        ("封板率", f"{seal_rate}%" if seal_rate is not None else "—"),
    ]

    lines = [
        "## 3. 情绪温度",
        "",
        "| 指标 | 数值 | 对比昨日 |",
        "|------|------|----------|",
    ]
    for label, today in rows:
        prev = compare_cell(today, previous.get(label))
        lines.append(f"| {label} | **{today}** | {prev} |")

    up = stat.get("up_count")
    down = stat.get("down_count")
    ratio = "—"
    if isinstance(up, int) and isinstance(down, int) and down > 0:
        ratio = f"1:{down / up:.1f}" if up > 0 else "—"

    lines.extend(
        [
            "",
            f"**宽度摘要**：上涨 {fmt_num(up)} / 下跌 {fmt_num(down)} / 平盘 {fmt_num(stat.get('flat_count'))} · 涨跌比约 **{ratio}**",
            "",
            "**我的定性**：",
            "",
            "1. **宽度 vs 指数**：____（指数涨但个股跌？还是共振？）",
            "2. **涨停生态**：____（封板率、炸板是否支持短线情绪）",
            "3. **情绪定调**：____（用一句话命名今天）",
            "",
        ]
    )
    return lines


def build_stub(data: dict, date: datetime, previous_recap: Path | None) -> str:
    previous = parse_previous_sentiment(previous_recap) if previous_recap else {}
    title = f"# {date.strftime('%Y-%m-%d')} 今日复盘"
    header = [
        title,
        "",
        f"时间：{date.strftime('%Y-%m-%d %A')} 收盘",
        "模式：一句话结论 → 指数与量能 → 情绪温度 → 主线拆解 → 持仓复盘 → 明日计划",
        "",
        "## 1. 一句话结论",
        "",
        "____",
        "",
        "---",
        "",
    ]
    body = build_section_indices(data.get("indices") or {})
    body.extend(build_section_sentiment(data, previous))
    body.extend(
        [
            "## 4. 主线拆解",
            "",
            "### 盘面节奏",
            "- **09:25 竞价**：____",
            "- **上午**：____",
            "- **午后**：____",
            "",
            "## 5. 持仓复盘",
            "",
            "> 填写持仓组表现与纪律执行情况",
            "",
            "## 6. 明日计划",
            "",
            "1. ____",
            "2. ____",
            "",
            "---",
            "",
            "**免责声明**：本复盘仅作市场观察记录，不构成投资建议。市场有风险，投资需谨慎。",
            "",
        ]
    )
    return "\n".join(header + body)


def default_previous_recap(date: datetime) -> Path | None:
    if not DEFAULT_OUT_DIR.is_dir():
        return None
    candidates = sorted(DEFAULT_OUT_DIR.glob("*_今日复盘.md"), reverse=True)
    today_prefix = date.strftime("%Y-%m-%d")
    for path in candidates:
        if today_prefix not in path.name:
            return path
    return candidates[0] if candidates else None


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 UZI 每日复盘 Markdown 骨架")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON, help="market_data_today.json 路径")
    parser.add_argument("--date", type=str, default=None, help="复盘日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--compare", type=Path, default=None, help="上一篇复盘，用于对比昨日列")
    parser.add_argument("--out", type=Path, default=None, help="输出文件，默认 docs/market-recaps/YYYY-MM-DD_今日复盘.stub.md")
    parser.add_argument("--print", action="store_true", help="只打印到 stdout，不写文件")
    args = parser.parse_args()

    data = load_json(args.json)
    date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    previous = args.compare or default_previous_recap(date)
    markdown = build_stub(data, date, previous)

    if args.print:
        print(markdown)
        return

    out = args.out or DEFAULT_OUT_DIR / f"{date.strftime('%Y-%m-%d')}_今日复盘.stub.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    print(f"已生成: {out}")
    if previous:
        print(f"对比基准: {previous}")


if __name__ == "__main__":
    main()
