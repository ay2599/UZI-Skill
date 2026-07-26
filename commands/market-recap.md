---
description: A股每日/盘中市场复盘（指数量能 + 情绪宽度 + 主线 + 持仓 + 次日计划）
argument-hint: "[可选：日期 YYYY-MM-DD · 持仓代码 · 午盘/周末]"
---

# 市场复盘任务

用户输入: $ARGUMENTS

读取并严格执行 `skills/market-recap/SKILL.md`。

## 最短路径

```bash
cd <plugin_root>
python skills/market-recap/scripts/get_market_recap.py
python skills/market-recap/scripts/generate_recap_stub.py
```

然后你补全 stub → 写出 `docs/market-recaps/YYYY-MM-DD_今日复盘.md`，并给用户一句话结论 + 次日关键位。
