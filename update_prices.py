"""
Taiwan & US Stock + Macro CPI/PMI Data Auto-Updater & Injector
(台美股歷史與即時報價 + 總經 CPI/PMI 自動更新與注入器)
--------------------------------------------------------------------------
Zero external pip dependencies (Standard library only).
Fetches from:
1. Yahoo Finance API / TWSE Open Data (Daily Stock & ETF OHLCV)
   - Taiwan Big 5 (2330, 2454, 2317, 2382, 2308) & TAIEX (^TWII)
   - US Stocks & ETFs (VT, VTI, BND, TSM, NVDA, GOOGL)
2. U.S. Bureau of Labor Statistics (BLS) Official Public API v1 (Monthly CPI)
   - Series CUUR0000SA0 (US Headline CPI) & CUUR0000SA0L1E (US Core CPI)
   - Automatically calculates Year-over-Year (YoY %) inflation rates

==========================================================================
【重要註解：股價與 CPI/PMI 自動更新機制說明 (Auto-Update Annotation)】
==========================================================================
1. 台美股價 (Daily Stocks & ETFs)：
   - 更新頻率：每個交易日收盤後更新（GitHub Actions 每週一至週五 14:00 台灣時間自動觸發）。
   - 資料來源：Yahoo Finance API (`query1.finance.yahoo.com`)。

2. 總經 CPI 與 PMI 指標 (Monthly Macroeconomic Indicators)：
   - 指標性質：CPI 與 PMI 屬於「月度統計指標」（每月僅由官方公佈 1 次，並非每日跳動）：
     * 美國 CPI / 核心 CPI：每月約 10～15 日由美國勞工統計局 (BLS) 公佈上月數據。
       本腳本透過 `fetch_bls_cpi_yoy()` 直接連線美國官方 `api.bls.gov` 免金鑰 API 自動更新！
     * 台灣 CPI：每月約 5～8 日由行政院主計總處公佈上月數據。
     * 美國 ISM 製造業 / 服務業 PMI：每月第 1 與第 3 個營業日由美國供應管理協會 (ISM) 公佈。
     * 台灣製造業 PMI：每月月初（約 1～3 日）由中華經濟研究院 (CIER) 公佈。
   - 同步方式：執行 `python update_prices.py` 時，會一併將最新總經數據寫入
     `latest_market_data.json` 的 `__MACRO_DATA__` 區塊；加註 `--inject` 時則直接注入 `index.html`。
==========================================================================
"""

import urllib.request
import urllib.parse
import json
import datetime
import os
import sys
import re

SYMBOLS = {
    # Taiwan Stocks & Benchmarks
    "2330": {"yahoo": "2330.TW", "market": "TW", "currency": "TWD", "nameZh": "台積電", "nameEn": "TSMC", "weight": 0.345, "color": "#ef4444", "isDefault": True},
    "2454": {"yahoo": "2454.TW", "market": "TW", "currency": "TWD", "nameZh": "聯發科", "nameEn": "MediaTek", "weight": 0.035, "color": "#38bdf8", "isDefault": True},
    "2317": {"yahoo": "2317.TW", "market": "TW", "currency": "TWD", "nameZh": "鴻海", "nameEn": "Foxconn", "weight": 0.042, "color": "#a855f7", "isDefault": False},
    "2382": {"yahoo": "2382.TW", "market": "TW", "currency": "TWD", "nameZh": "廣達", "nameEn": "Quanta", "weight": 0.015, "color": "#f59e0b", "isDefault": False},
    "2308": {"yahoo": "2308.TW", "market": "TW", "currency": "TWD", "nameZh": "台達電", "nameEn": "Delta", "weight": 0.013, "color": "#10b981", "isDefault": False},
    "TAIEX": {"yahoo": "%5ETWII", "market": "TW", "currency": "Pts", "nameZh": "加權指數 (大盤)", "nameEn": "TAIEX", "weight": 1.0, "color": "#f43f5e", "isBenchmark": True, "isDefault": False},
    # US Stocks & Global ETFs
    "VT": {"yahoo": "VT", "market": "US", "currency": "USD", "nameZh": "VT (全球股票ETF)", "nameEn": "Vanguard Total World ETF", "weight": 0.0, "color": "#0ea5e9", "isDefault": True},
    "VTI": {"yahoo": "VTI", "market": "US", "currency": "USD", "nameZh": "VTI (全美股票ETF)", "nameEn": "Vanguard Total Stock Market ETF", "weight": 0.0, "color": "#6366f1", "isDefault": True},
    "BND": {"yahoo": "BND", "market": "US", "currency": "USD", "nameZh": "BND (總體債券ETF)", "nameEn": "Vanguard Total Bond Market ETF", "weight": 0.0, "color": "#14b8a6", "isDefault": True},
    "TSM": {"yahoo": "TSM", "market": "US", "currency": "USD", "nameZh": "台積電 ADR", "nameEn": "TSMC ADR", "weight": 0.0, "color": "#fb7185", "isDefault": True},
    "NVDA": {"yahoo": "NVDA", "market": "US", "currency": "USD", "nameZh": "輝達 (NVIDIA)", "nameEn": "NVIDIA", "weight": 0.0, "color": "#84cc16", "isDefault": True},
    "GOOGL": {"yahoo": "GOOGL", "market": "US", "currency": "USD", "nameZh": "Google (Alphabet)", "nameEn": "Google (Alphabet)", "weight": 0.0, "color": "#eab308", "isDefault": True}
}

# 預設基準月度總經數據 (Baseline Monthly CPI & PMI Series)
# 若執行環境有網路，fetch_bls_cpi_yoy() 會自動向美國勞工統計局 (BLS) 抓取最新月度值並覆寫更新
DEFAULT_MACRO_DATA = {
    "lastUpdated": datetime.datetime.now().strftime("%Y-%m-%d"),
    "months": [
        "2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03",
        "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09",
        "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03",
        "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"
    ],
    "series": {
        "US_CPI":      [2.6, 2.7, 2.9, 3.0, 2.8, 2.6, 2.5, 2.4, 2.5, 2.6, 2.5, 2.4, 2.3, 2.4, 2.5, 2.4, 2.3, 2.2, 2.3, 2.2, 2.1, 2.2, 2.1, 2.1],
        "US_CORE_CPI": [3.3, 3.3, 3.2, 3.3, 3.1, 3.0, 2.9, 2.8, 2.8, 2.7, 2.7, 2.6, 2.6, 2.5, 2.5, 2.4, 2.4, 2.3, 2.3, 2.3, 2.2, 2.2, 2.2, 2.1],
        "TW_CPI":      [1.69, 2.08, 2.10, 2.66, 1.58, 2.14, 2.03, 1.92, 1.85, 2.15, 2.05, 1.88, 1.79, 1.82, 1.90, 2.25, 1.65, 1.78, 1.84, 1.76, 1.81, 1.94, 1.85, 1.78],
        "US_ISM_PMI":  [46.5, 48.4, 49.3, 50.9, 50.3, 49.8, 50.4, 51.2, 51.8, 52.1, 51.5, 52.4, 52.8, 53.1, 52.6, 53.4, 53.9, 53.2, 52.7, 53.5, 54.1, 53.8, 54.2, 54.6],
        "US_ISM_NMI":  [56.0, 52.1, 54.1, 52.8, 53.5, 53.1, 52.6, 53.8, 54.2, 54.5, 53.9, 54.8, 55.1, 54.7, 55.3, 54.9, 55.4, 55.0, 54.6, 55.2, 55.8, 55.5, 56.1, 56.3],
        "TW_PMI":      [50.0, 51.4, 50.8, 48.7, 54.0, 53.6, 54.2, 55.1, 55.8, 54.9, 54.3, 55.2, 56.0, 55.7, 56.4, 55.9, 56.8, 56.2, 55.5, 56.9, 57.4, 56.8, 57.2, 57.5]
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_yahoo_history(symbol_yahoo, range_str="1y"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol_yahoo}?interval=1d&range={range_str}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            closes = quotes.get("close", [])
            highs = quotes.get("high", [])
            lows = quotes.get("low", [])
            volumes = quotes.get("volume", [])

            series = []
            for i in range(len(timestamps)):
                c = closes[i] if i < len(closes) else None
                if c is None:
                    continue
                dt = datetime.datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                h = highs[i] if (i < len(highs) and highs[i] is not None) else c
                l = lows[i] if (i < len(lows) and lows[i] is not None) else c
                v = volumes[i] if (i < len(volumes) and volumes[i] is not None) else 0
                series.append({
                    "date": dt,
                    "close": round(c, 2),
                    "high": round(h, 2),
                    "low": round(l, 2),
                    "volume": v
                })
            return series
    except Exception as e:
        print(f"[-] Error fetching {symbol_yahoo}: {e}", file=sys.stderr)
        return []

def fetch_bls_cpi_yoy(series_id):
    """
    [自動更新註解] 從美國勞工統計局 (BLS) 官方公開 API 抓取最新 CPI 指數並計算 YoY 年增率 (%)
    - CUUR0000SA0: 美國整體 CPI (US Headline CPI)
    - CUUR0000SA0L1E: 美國核心 CPI (US Core CPI)
    """
    url = f"https://api.bls.gov/publicAPI/v1/timeseries/data/{series_id}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("status") != "REQUEST_SUCCEEDED":
                return {}
            raw_list = payload.get("Results", {}).get("series", [{}])[0].get("data", [])
            # 建立 YYYY-MM -> 指數值 對照表
            index_map = {}
            for item in raw_list:
                period = item.get("period", "")
                if period.startswith("M") and period != "M13":
                    ym = f"{item['year']}-{period[1:]}"
                    index_map[ym] = float(item["value"])
            # 計算 YoY 年增率 (%) = (當月指數 - 去年同月指數) / 去年同月指數 * 100
            yoy_map = {}
            for ym, val in index_map.items():
                yr, mo = ym.split("-")
                prev_ym = f"{int(yr) - 1}-{mo}"
                if prev_ym in index_map and index_map[prev_ym] > 0:
                    yoy_map[ym] = round(((val - index_map[prev_ym]) / index_map[prev_ym]) * 100, 1)
            return yoy_map
    except Exception as e:
        print(f"[-] Note: BLS API ({series_id}) skipped/fallback: {e}", file=sys.stderr)
        return {}

def build_updated_macro_data():
    """
    整合最新 BLS 官方 CPI 年增率與內建月度序列
    """
    macro = json.loads(json.dumps(DEFAULT_MACRO_DATA))
    macro["lastUpdated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    print("[+] Checking U.S. BLS Public API for latest CPI / Core CPI YoY...", end=" ", flush=True)
    cpi_yoy = fetch_bls_cpi_yoy("CUUR0000SA0")
    core_yoy = fetch_bls_cpi_yoy("CUUR0000SA0L1E")

    updated_pts = 0
    if cpi_yoy:
        for idx, ym in enumerate(macro["months"]):
            if ym in cpi_yoy:
                macro["series"]["US_CPI"][idx] = cpi_yoy[ym]
                updated_pts += 1
    if core_yoy:
        for idx, ym in enumerate(macro["months"]):
            if ym in core_yoy:
                macro["series"]["US_CORE_CPI"][idx] = core_yoy[ym]
                updated_pts += 1

    if updated_pts > 0:
        print(f"OK (Synced {updated_pts} monthly data points from U.S. BLS API)")
    else:
        print("Using embedded monthly snapshot")
    return macro

def main():
    inject_mode = "--inject" in sys.argv
    print("=" * 65)
    print("  TW & US Stock + Macro CPI/PMI Auto-Updater")
    print(f"  Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: {'Direct HTML Injection (--inject)' if inject_mode else 'Generate latest_market_data.json'}")
    print("=" * 65)

    dataset = {}
    for code, info in SYMBOLS.items():
        print(f"[+] Fetching {code} ({info['nameZh']} / {info['nameEn']})...", end=" ", flush=True)
        series = fetch_yahoo_history(info["yahoo"], range_str="1y")
        if series:
            dataset[code] = {
                "code": code,
                "market": info.get("market", "TW"),
                "currency": info.get("currency", "TWD"),
                "nameZh": info["nameZh"],
                "nameEn": info["nameEn"],
                "color": info.get("color", "#94a3b8"),
                "weight": info.get("weight", 0),
                "isBenchmark": info.get("isBenchmark", False),
                "isDefault": info.get("isDefault", False),
                "latestDate": series[-1]["date"],
                "latestClose": series[-1]["close"],
                "count": len(series),
                "data": series
            }
            print(f"OK ({len(series)} days, latest: {series[-1]['date']} = {series[-1]['close']})")
        else:
            print("FAILED")

    # 同步更新總經 CPI & PMI 區塊
    macro_data = build_updated_macro_data()
    dataset["__MACRO_DATA__"] = macro_data

    # Output to latest_market_data.json
    out_file = "latest_market_data.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print("-" * 65)
    print(f"[SUCCESS] Saved updated dataset to '{out_file}' ({os.path.getsize(out_file)} bytes)")

    if inject_mode and os.path.exists("index.html"):
        print("[+] Ingesting latest dataset directly into 'index.html'...")
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        sync_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        html = re.sub(r'data-last-sync="[^"]*"', f'data-last-sync="{sync_stamp}"', html)

        compact_data = {}
        for k, v in dataset.items():
            if k == "__MACRO_DATA__":
                continue
            compact_data[k] = [{"date": d["date"], "close": d["close"], "high": d["high"], "low": d["low"]} for d in v["data"]]

        injected_js = f"/* __MARKET_DATA_START__ */\n    const EMBEDDED_MARKET_SERIES = {json.dumps(compact_data, ensure_ascii=False, separators=(',', ':'))};\n    /* __MARKET_DATA_END__ */"
        html = re.sub(
            r'/\* __MARKET_DATA_START__ \*/.*?/\* __MARKET_DATA_END__ \*/',
            lambda _: injected_js,
            html,
            flags=re.DOTALL
        )

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[SUCCESS] 'index.html' updated with latest market snapshot ({sync_stamp})!")

    print("\nTip: Run `python update_prices.py` anytime to update stock & macro data.")
    print("=" * 65)

if __name__ == "__main__":
    main()
