# 每日市场复盘

个人 / 团队盘后复盘归档。正式 skill：`skills/market-recap/`。

## 用法

```bash
# 推荐（skill 路径）
python skills/market-recap/scripts/get_market_recap.py
python skills/market-recap/scripts/generate_recap_stub.py

# 兼容根目录入口（转发到 skill）
python get_market_recap.py
python generate_recap_stub.py --date 2026-07-26 \
  --compare docs/market-recaps/2026-07-20_今日复盘.md
```

Agent 触发词：复盘 / 今日复盘 / 盘后 / 午盘 / 周末复盘 · 命令：`/market-recap`

默认输出：`docs/market-recaps/YYYY-MM-DD_今日复盘.stub.md`  
人工或 agent 补全后去掉 `.stub` 归档。

## 约定

| 文件 | 是否入库 |
|---|---|
| `docs/market-recaps/*.md` | ✅ 归档 |
| `market_data_today.json` / `_*.json` | ❌ 运行时产物（已 gitignore） |
