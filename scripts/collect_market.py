"""
scripts/collect_market.py
역할: 주요 시장 지수를 수집하여 data/market.json 으로 저장합니다.

yfinance 로 수집하되, rate limit 시 exchangerate API(환율)로 부분 보완합니다.
period="5d" 로 요청해 주말/공휴일에도 데이터가 충분히 확보되도록 합니다.

필요 라이브러리: yfinance, requests
"""

import json
import os
import time
import requests
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

# 수집할 종목 (period="5d" 로 주말/공휴일 대응)
TICKERS = [
    {"symbol": "^KS11", "name": "KOSPI",       "fmt": "comma"},
    {"symbol": "^GSPC", "name": "S&P 500",      "fmt": "comma"},
    {"symbol": "^SOX",  "name": "반도체(SOX)",  "fmt": "comma"},
    {"symbol": "GC=F",  "name": "금(Gold)",     "fmt": "decimal"},
]


def fmt_value(value, fmt):
    if fmt == "comma":
        return f"{value:,.2f}"
    return f"{value:.2f}"


def fetch_yfinance():
    """yfinance 로 주요 지수를 가져옵니다. 실패 시 빈 리스트 반환."""
    import yfinance as yf

    items = []
    for t in TICKERS:
        try:
            time.sleep(1)  # rate limit 방지용 딜레이
            hist = yf.Ticker(t["symbol"]).history(period="5d")
            if len(hist) < 2:
                raise ValueError("데이터 부족")

            prev  = float(hist["Close"].iloc[-2])
            close = float(hist["Close"].iloc[-1])
            change     = close - prev
            change_pct = (change / prev * 100) if prev != 0 else 0
            direction  = "up" if change > 0 else ("down" if change < 0 else "flat")
            sign       = "+" if change >= 0 else ""

            items.append({
                "name":       t["name"],
                "value":      fmt_value(close, t["fmt"]),
                "change":     f"{sign}{fmt_value(change, t['fmt'])}",
                "change_pct": f"{sign}{change_pct:.2f}%",
                "direction":  direction,
            })
            print(f"  ✓ {t['name']}: {fmt_value(close, t['fmt'])}")

        except Exception as e:
            print(f"  [경고] {t['name']} 수집 실패: {e}")

    return items


def fetch_usd_krw():
    """exchangerate-api (무료, 키 불필요) 로 원/달러 환율을 가져옵니다."""
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
        {"name": "KOSPI",       "value": "2,712.34", "change": "+15.21",  "change_pct": "+0.56%", "direction": "up"},
        {"name": "S&P 500",     "value": "5,431.22", "change": "-8.10",   "change_pct": "-0.15%", "direction": "down"},
        {"name": "반도체(SOX)", "value": "4,123.50", "change": "+32.10",  "change_pct": "+0.79%", "direction": "up"},
        {"name": "금(Gold)",    "value": "2,348.70", "change": "-5.30",   "change_pct": "-0.23%", "direction": "down"},
        {"name": "원/달러 환율","value": "1,398원",  "change": "-",       "change_pct": "-",       "direction": "flat"},
    ]


def main():
    now_kst = datetime.now(KST)
    items = []

    try:
        import yfinance  # noqa: 설치 확인
        items = fetch_yfinance()
    except ImportError:
        print("[경고] yfinance 미설치")

    # 환율은 별도 API 로 항상 시도
    krw = fetch_usd_krw()
    if krw:
        items.append(krw)

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
