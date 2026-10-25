"""
Taiwan & US Stock Data Auto-Updater & Injector (台美股歷史與即時報價自動更新/注入器)
--------------------------------------------------------------------------
Zero external pip dependencies (Standard library only).
Fetches from official TWSE Open Data and Yahoo Finance API.
- Supports Taiwan Big 5 & TAIEX + US Stocks/ETFs (VT, VTI, BND, TSM, NVDA, GOOGL)
- Generates 'latest_market_data.json'
- Can inject directly into 'index.html' via `python update_prices.py --inject`
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

def main():
    inject_mode = "--inject" in sys.argv
    print("=" * 65)
    print("  TW & US Stock Auto-Updater (台美股歷史行情自動更新器)")
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

    print("\nTip: Run `python update_prices.py` anytime to update data.")
    print("=" * 65)

if __name__ == "__main__":
    main()
