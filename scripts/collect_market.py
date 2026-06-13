"""
scripts/collect_market.py
역할: 주요 시장 지수를 수집하여 data/market.json 으로 저장합니다.

사용 API:
  - Yahoo Finance 직접 URL (yfinance 라이브러리 없이 단순 HTTP 요청)
  - open.er-api.com : 원/달러 환율 (무료, API 키 불필요)

필요 라이브러리: requests
"""

import json
import os
import time
import requests
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

TICKERS = [
    {"symbol": "^KS11", "name": "KOSPI",       "fmt": "comma"},
    {"symbol": "^GSPC", "name": "S&P 500",      "fmt": "comma"},
    {"symbol": "^IXIC", "name": "나스닥",       "fmt": "comma"},
    {"symbol": "^SOX",  "name": "반도체(SOX)",  "fmt": "comma"},
    {"symbol": "GC=F",  "name": "금 ($/oz)",    "fmt": "decimal"},
]


def fmt_value(value, fmt):
    if fmt == "comma":
        return f"{value:,.2f}"
    return f"{value:.2f}"


def fetch_yahoo(symbol, name, fmt):
    """Yahoo Finance v8 API 에 직접 HTTP 요청합니다."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()

        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]

        if len(closes) < 2:
            raise ValueError("데이터 부족")

        close = closes[-1]
        prev  = closes[-2]
        change     = close - prev
        change_pct = (change / prev * 100) if prev != 0 else 0
        direction  = "up" if change > 0 else ("down" if change < 0 else "flat")
        sign       = "+" if change >= 0 else ""

        print(f"  ✓ {name}: {fmt_value(close, fmt)}")
        return {
            "name":       name,
            "value":      fmt_value(close, fmt),
            "change":     f"{sign}{fmt_value(change, fmt)}",
            "change_pct": f"{sign}{change_pct:.2f}%",
            "direction":  direction,
        }

    except Exception as e:
        print(f"  [경고] {name} 수집 실패: {e}")
        return None


def fetch_usd_krw():
    """원/달러 환율을 가져옵니다."""
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        res.raise_for_status()
        rate = res.json()["rates"]["KRW"]
        print(f"  ✓ 원/달러 환율: {rate:,.0f}원")
        return {
            "name":       "원/달러 환율",
            "value":      f"{rate:,.0f}원",
            "change":     "-",
            "change_pct": "-",
            "direction":  "flat",
        }
    except Exception as e:
        print(f"  [경고] 환율 수집 실패: {e}")
        return None


def get_sample():
    return [
        {"name": "KOSPI",        "value": "2,712.34", "change": "+15.21",  "change_pct": "+0.56%", "direction": "up"},
        {"name": "S&P 500",      "value": "5,431.22", "change": "-8.10",   "change_pct": "-0.15%", "direction": "down"},
        {"name": "나스닥",       "value": "19,864.98","change": "+102.45", "change_pct": "+0.52%", "direction": "up"},
        {"name": "반도체(SOX)",  "value": "4,123.50", "change": "+32.10",  "change_pct": "+0.79%", "direction": "up"},
        {"name": "금 ($/oz)",    "value": "2,348.70", "change": "-5.30",   "change_pct": "-0.23%", "direction": "down"},
        {"name": "원/달러 환율", "value": "1,398원",  "change": "-",       "change_pct": "-",      "direction": "flat"},
    ]


def main():
    now_kst = datetime.now(KST)
    items = []

    for t in TICKERS:
        result = fetch_yahoo(t["symbol"], t["name"], t["fmt"])
        if result:
            items.append(result)
        time.sleep(0.5)  # 요청 간 간격

    krw = fetch_usd_krw()
    if krw:
        items.append(krw)

    if len(items) <= 1:  # 환율만 있으면 샘플로 대체
        print("[경고] 지수 수집 실패. 샘플 데이터를 사용합니다.")
        items = get_sample()

    result = {
        "updated_at": now_kst.strftime("%Y-%m-%d %H:%M"),
        "items": items,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[완료] data/market.json 저장 완료: {len(items)}개 종목")


if __name__ == "__main__":
    main()
