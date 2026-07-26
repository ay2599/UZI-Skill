#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取今日A股市场数据用于复盘
"""
import akshare as ak
import json
import re
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

_TENCENT_INDEX_CODES = {
    "上证指数": "s_sh000001",
    "深证成指": "s_sz399001",
    "创业板指": "s_sz399006",
    "科创50": "s_sh000688",
}


def _fetch_indices_tencent() -> dict:
    """东财指数 spot 失败时，用腾讯 s_ 前缀接口兜底。"""
    if requests is None:
        return {}
    url = f"https://qt.gtimg.cn/q={','.join(_TENCENT_INDEX_CODES.values())}"
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = "gbk"
    except Exception as e:
        print(f"  腾讯指数兜底失败: {e}")
        return {}

    indices: dict = {}
    for name, code in _TENCENT_INDEX_CODES.items():
        m = re.search(rf'v_{re.escape(code)}="([^"]+)"', resp.text)
        if not m:
            continue
        parts = m.group(1).split("~")
        if len(parts) < 6:
            continue
        try:
            indices[name] = {
                "code": code.replace("s_", ""),
                "close": float(parts[3]),
                "change": float(parts[4]),
                "change_pct": float(parts[5]),
            }
            print(f"  {name}(腾讯): {indices[name]['close']} ({indices[name]['change_pct']:+.2f}%)")
        except ValueError:
            continue
    return indices


def get_market_data():
    """获取市场概况数据"""
    data = {}
    
    try:
        # 1. 获取主要指数
        print("正在获取指数数据...")
        indices = {
            "上证指数": "sh000001",
            "深证成指": "sz399001",
            "创业板指": "sz399006",
            "科创50": "sh000688",
            "沪深300": "sh000300",
            "中证500": "sh000905",
            "中证1000": "sh000852",
        }
        
        data["indices"] = {}
        index_spot = None
        try:
            index_spot = ak.stock_zh_index_spot_em()
        except Exception as e:
            print(f"  指数列表获取失败: {e}")
        
        for name, code in indices.items():
            try:
                if index_spot is None or index_spot.empty:
                    raise ValueError("指数列表为空")
                idx_data = index_spot[index_spot['代码'] == code]
                if not idx_data.empty:
                    data["indices"][name] = {
                        "code": code,
                        "close": float(idx_data['最新价'].values[0]),
                        "change_pct": float(idx_data['涨跌幅'].values[0]),
                        "change": float(idx_data['涨跌额'].values[0])
                    }
                    print(f"  {name}: {data['indices'][name]['close']} ({data['indices'][name]['change_pct']:+.2f}%)")
            except Exception as e:
                print(f"  {name} 获取失败: {e}")

        if not data["indices"]:
            print("  尝试腾讯指数兜底...")
            data["indices"] = _fetch_indices_tencent()
        
        # 2. 获取市场统计
        print("\n正在获取市场统计...")
        market_stat = None
        try:
            market_stat = ak.stock_zh_a_spot_em()
            data["market_stat"] = {
                "total_stocks": len(market_stat),
                "up_count": len(market_stat[market_stat['涨跌幅'] > 0]),
                "down_count": len(market_stat[market_stat['涨跌幅'] < 0]),
                "flat_count": len(market_stat[market_stat['涨跌幅'] == 0])
            }
            print(f"  上涨: {data['market_stat']['up_count']}")
            print(f"  下跌: {data['market_stat']['down_count']}")
            print(f"  平盘: {data['market_stat']['flat_count']}")
        except Exception as e:
            print(f"  市场统计获取失败: {e}")
        
        # 3. 获取涨停板数据
        print("\n正在获取涨停板数据...")
        try:
            zt_pool = ak.stock_zt_pool_em(date=datetime.now().strftime("%Y%m%d"))
            data["limit_up"] = {
                "count": len(zt_pool),
                "top_stocks": []
            }
            if len(zt_pool) > 0:
                for idx, row in zt_pool.head(10).iterrows():
                    data["limit_up"]["top_stocks"].append({
                        "name": row['名称'],
                        "code": row['代码'],
                        "reason": row.get('涨停原因类别', ''),
                        "first_time": str(row.get('首次封板时间', ''))
                    })
            print(f"  涨停家数: {data['limit_up']['count']}")
        except Exception as e:
            print(f"  涨停板数据获取失败: {e}")
            data["limit_up"] = {"count": 0, "top_stocks": []}
        
        # 4. 获取跌停板数据
        print("\n正在获取跌停板数据...")
        try:
            dt_pool = ak.stock_zt_pool_dtgc_em(date=datetime.now().strftime("%Y%m%d"))
            data["limit_down"] = {
                "count": len(dt_pool)
            }
            print(f"  跌停家数: {data['limit_down']['count']}")
        except Exception as e:
            print(f"  跌停板数据获取失败: {e}")
            data["limit_down"] = {"count": 0}
        
        # 5. 获取炸板数据
        print("\n正在获取炸板数据...")
        try:
            zb_pool = ak.stock_zt_pool_zbgc_em(date=datetime.now().strftime("%Y%m%d"))
            data["broken_limit"] = {
                "count": len(zb_pool)
            }
            print(f"  炸板家数: {data['broken_limit']['count']}")
        except Exception as e:
            print(f"  炸板数据获取失败: {e}")
            data["broken_limit"] = {"count": 0}
        
        # 6. 计算封板率
        if data.get("limit_up", {}).get("count", 0) > 0 and data.get("broken_limit", {}).get("count", 0) >= 0:
            total_attempts = data["limit_up"]["count"] + data["broken_limit"]["count"]
            if total_attempts > 0:
                data["seal_rate"] = round(data["limit_up"]["count"] / total_attempts * 100, 2)
                print(f"  封板率: {data['seal_rate']}%")
        
        # 7. 获取资金流向
        print("\n正在获取资金流向...")
        try:
            capital_flow = ak.stock_market_fund_flow()
            if not capital_flow.empty:
                latest = capital_flow.iloc[0]
                data["capital_flow"] = {
                    "main_net": float(latest.get('主力净流入-净额', 0)),
                    "main_net_pct": float(latest.get('主力净流入-净占比', 0))
                }
                print(f"  主力净流入: {data['capital_flow']['main_net']:.2f}亿元")
        except Exception as e:
            print(f"  资金流向获取失败: {e}")
        
        # 8. 获取成交额（从指数数据推算）
        print("\n正在获取成交额...")
        try:
            if market_stat is None:
                raise ValueError("市场统计为空")
            # 尝试从市场统计获取总成交额
            total_amount = market_stat['成交额'].sum() / 100000000  # 转换为亿元
            data["turnover"] = round(total_amount / 10000, 2)  # 转换为万亿
            print(f"  两市成交额: {data['turnover']}万亿元")
        except Exception as e:
            print(f"  成交额获取失败: {e}")
        
        # 9. 获取热门板块
        print("\n正在获取热门板块...")
        try:
            sector_flow = ak.stock_board_industry_name_em()
            data["hot_sectors"] = []
            for idx, row in sector_flow.head(10).iterrows():
                data["hot_sectors"].append({
                    "name": row['板块名称'],
                    "change_pct": float(row['涨跌幅'])
                })
            print(f"  获取到 {len(data['hot_sectors'])} 个板块数据")
        except Exception as e:
            print(f"  热门板块获取失败: {e}")
        
    except Exception as e:
        print(f"获取数据时发生错误: {e}")
    
    return data

if __name__ == "__main__":
    print("=" * 60)
    print(f"开始获取 {datetime.now().strftime('%Y-%m-%d')} 市场数据")
    print("=" * 60)
    
    data = get_market_data()
    
    # 保存到JSON
    output_file = "market_data_today.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"数据已保存到: {output_file}")
    print("下一步: python generate_recap_stub.py")
    print("=" * 60)
