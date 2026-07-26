# 每日市场复盘

个人 / 团队盘后复盘归档。脚本在仓库根目录，产物写到本目录。

## 用法

```bash
# 1. 抓取当日指数 / 涨跌家数 / 量能 / 热门板块 → market_data_today.json
python get_market_recap.py

# 2. 生成 Markdown 骨架（第 2、3 节）
python generate_recap_stub.py
# 或指定日期、对比上一篇：
python generate_recap_stub.py --date 2026-07-26 --compare docs/market-recaps/2026-07-20_今日复盘.md
```

默认输出：`docs/market-recaps/YYYY-MM-DD_今日复盘.stub.md`  
人工补全「一句话结论 / 主线拆解 / 持仓 / 次日计划」后，去掉 `.stub` 归档。

## 约定

| 文件 | 是否入库 |
|---|---|
| `docs/market-recaps/*.md` | ✅ 归档 |
| `market_data_today.json` / `_*.json` | ❌ 运行时产物（已 gitignore） |
