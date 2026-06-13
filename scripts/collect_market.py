"""
scripts/collect_market.py
역할: 주요 시장 지수를 수집하여 data/market.json 으로 저장합니다.

yfinance 는 GitHub Actions IP 에서 Yahoo Finance rate limit 에 걸리므로
investing.com 스크래핑 + 환율은 exchangerate API 로 대체합니다.

필요 라이브러리: requests, beautifulsoup4
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# investing.com 각 지수 URL
INDICES = [
    {"name": "코스피",    "url": "https://api.investing.com/api/financialdata/get_quotes?pair_ids=929&time_utc_offset=32400&lang_ID=18&market_hours_type=1", "key": "929"},
    {"name": "나스닥",    "url": "https://api.investing.com/api/financialdata/get_quotes?pair_ids=13&time_utc_offset=32400&lang_ID=18&market_hours_type=1",  "key": "13"},
    {"name": "S&P 500",  "url": "https://api.investing.com/api/financialdata/get_quotes?pair_ids=166&time_utc_offset=32400&lang_ID=18&market_hours_type=1", "key": "166"},
    {"name": "필라델피아 반도체", "url": "https://api.investing.com/api/financialdata/get_quotes?pair_ids=49470&time_utc_offset=32400&lang_ID=18&market_hours_type=1", "key": "49470"},
    {"name": "금 ($/oz)", "url": "https://api.investing.com/api/financialdata/get_quotes?pair_ids=8830&time_utc_offset=32400&lang_ID=18&market_hours_type=1",  "key": "8830"},
]


def fetch_investing(name, url):
    """investing.com 비공개 API 로 지수 데이터를 가져옵니다."""
    try:
        h = {**HEADERS, "Domain-Id": "www", "Referer": "https://www.investing.com/"}
        res = requests.get(url, headers=h, timeout=10)
        res.raise_for_status()
        data = res.json()
        quote = data["quotes"][0]
        price      = float(quote.get("last", 0))
        change     = float(quote.get("change", 0))
        change_pct = float(quote.get("change_percent", 0))
        direction  = "up" if change > 0 else ("down" if change < 0 else "flat")
        sign       = "+" if change >= 0 else ""
        return {
            "name":       name,
            "value":      f"{price:,.2f}",
            "change":     f"{sign}{change:,.2f}",
            "change_pct": f"{sign}{change_pct:.2f}%",
            "direction":  direction,
        }
    except Exception as e:
        print(f"  [경고] {name} 수집 실패: {e}")
        return None


def fetch_usd_krw():
    """exchangerate-api (무료, 키 불필요) 로 원/달러 환율을 가져옵니다."""
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        res.raise_for_status()
        data = res.json()
        rate = data["rates"]["KRW"]
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
        {"name": "코스피",          "value": "2,712.34", "change": "+15.21", "change_pct": "+0.56%", "direction": "up"},
        {"name": "나스닥",           "value": "19,864.98","change": "+102.45","change_pct": "+0.52%", "direction": "up"},
        {"name": "S&P 500",         "value": "5,431.22", "change": "-8.10",  "change_pct": "-0.15%", "direction": "down"},
        {"name": "필라델피아 반도체", "value": "4,123.50", "change": "+32.10", "change_pct": "+0.79%", "direction": "up"},
        {"name": "금 ($/oz)",       "value": "2,348.70", "change": "-5.30",  "change_pct": "-0.23%", "direction": "down"},
        {"name": "원/달러 환율",     "value": "1,398원",  "change": "-",      "change_pct": "-",      "direction": "flat"},
    ]


def main():
    now_kst = datetime.now(KST)
    items = []

    for idx in INDICES:
        result = fetch_investing(idx["name"], idx["url"])
        if result:
            items.append(result)
            print(f"  ✓ {result['name']}: {result['value']}")

    krw = fetch_usd_krw()
    if krw:
        items.append(krw)
        print(f"  ✓ {krw['name']}: {krw['value']}")

    if not items:
        print("[경고] 모든 수집 실패. 샘플 데이터를 사용합니다.")
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
