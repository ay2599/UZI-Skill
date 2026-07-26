---
name: market-recap
description: A股每日/盘中市场复盘。抓取指数量能与情绪宽度，生成复盘骨架，并由 agent 补全主线、持仓与次日计划。Use when 用户提到"复盘/今日复盘/盘后复盘/午盘复盘/周末复盘/写复盘/市场怎么看/明天怎么干"。
version: 3.9.2
author: FloatFu-true
license: MIT
metadata:
  hermes:
    tags: [finance, a-share, market-recap, daily-review]
    related_skills: [deep-analysis, lhb-analyzer]
---

# 每日市场复盘

## 调用上下文

输入：可选日期 / 持仓列表 / 盘中|收盘|周末模式  
输出：`docs/market-recaps/YYYY-MM-DD_今日复盘.md`

## 工作流（脚本骨架 + 你写结论）

### Step 1 · 抓数

```bash
cd <plugin_root>
python skills/market-recap/scripts/get_market_recap.py
```

产物：`market_data_today.json`（gitignore，不入库）。

### Step 2 · 生成骨架

```bash
python skills/market-recap/scripts/generate_recap_stub.py
# 指定日期 / 对比上一篇：
python skills/market-recap/scripts/generate_recap_stub.py --date YYYY-MM-DD \
  --compare docs/market-recaps/<上一篇>.md
```

产物：`docs/market-recaps/YYYY-MM-DD_今日复盘.stub.md`

### Step 3 · 你来写（HARD-GATE）

脚本只填第 2–3 节数字。**不要把 stub 当终稿**。你必须：

1. 读 stub + `market_data_today.json` + 上一篇归档复盘
2. 若用户给了持仓，补行情（腾讯/东财/akshare均可）并写第 5 节
3. 按 [references/output-template.md](references/output-template.md) 写完整 1–7 节
4. 落盘为 `docs/market-recaps/YYYY-MM-DD_今日复盘.md`（去掉 `.stub`）
5. 向用户汇报：一句话结论 + 情绪定调 + 持仓要点 + 次日关键位

### 模式切换

| 用户说法 | 标题 / 覆盖 |
|---|---|
| 今日复盘 / 盘后 | `今日复盘` · 当日收盘 |
| 午盘 / 早盘 | `午盘复盘` / `早盘复盘` · 注明截止时间 |
| 周末复盘 | `周末复盘` · 覆盖最近交易日 |

## 质量红线

- 数字必须能追溯到 JSON 或公开行情；不确定写「约 / 报道口径」
- 持仓未提供 → 第 5 节写「未提供持仓」，不要编造仓位
- 结尾保留免责声明；不做荐股口号

## 参考

- 输出模板：[references/output-template.md](references/output-template.md)
- 归档目录：`docs/market-recaps/`
- 用法速查：`docs/market-recaps/README.md`
