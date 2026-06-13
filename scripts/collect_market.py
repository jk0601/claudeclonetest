"""
scripts/collect_market.py
역할: 주요 시장 지수(코스피, 나스닥 등)를 수집하여 data/market.json 으로 저장합니다.

사용 라이브러리: yfinance (무료, API 키 불필요)
  - Yahoo Finance 데이터를 파이썬으로 쉽게 가져올 수 있습니다.
  - pip install yfinance

티커(Ticker) 기호 설명:
  ^KS11   → 코스피
  ^IXIC   → 나스닥
  ^GSPC   → S&P 500
  SOXX    → 반도체 ETF
  GC=F    → 금 선물
  KRW=X   → 원/달러 환율
"""

import json
import os
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

# ──────────────────────────────────────
# 수집할 종목 설정
# ──────────────────────────────────────
TICKERS = [
    {"symbol": "^KS11",  "name": "코스피",          "format": "comma"},
    {"symbol": "^IXIC",  "name": "나스닥",           "format": "comma"},
    {"symbol": "^GSPC",  "name": "S&P 500",          "format": "comma"},
    {"symbol": "SOXX",   "name": "반도체 ETF (SOXX)", "format": "decimal"},
    {"symbol": "GC=F",   "name": "금 ($/oz)",         "format": "decimal"},
    {"symbol": "KRW=X",  "name": "원/달러 환율",      "format": "won"},
]


def format_value(value, fmt):
    """숫자를 표시 형식에 맞게 변환합니다."""
    if fmt == "comma":
        return f"{value:,.2f}"
    elif fmt == "decimal":
        return f"{value:.2f}"
    elif fmt == "won":
        return f"{value:,.0f}원"
    return str(value)


def get_direction(change):
    """변화량으로 방향을 결정합니다."""
    if change > 0:
        return "up"
    elif change < 0:
        return "down"
    return "flat"


def main():
    now_kst = datetime.now(KST)
    items = []

    try:
        import yfinance as yf

        for t in TICKERS:
            try:
                ticker = yf.Ticker(t["symbol"])
                hist = ticker.history(period="2d")  # 최근 2일치

                if hist.empty or len(hist) < 1:
                    raise ValueError("데이터 없음")

                close = hist["Close"].iloc[-1]
                prev  = hist["Close"].iloc[-2] if len(hist) >= 2 else close
                change     = close - prev
                change_pct = (change / prev * 100) if prev != 0 else 0
                direction  = get_direction(change)

                items.append({
                    "name":       t["name"],
                    "value":      format_value(close, t["format"]),
                    "change":     f"{'+' if change >= 0 else ''}{format_value(change, t['format'])}",
                    "change_pct": f"{'+' if change_pct >= 0 else ''}{change_pct:.2f}%",
                    "direction":  direction,
                })
                print(f"  ✓ {t['name']}: {format_value(close, t['format'])}")

            except Exception as e:
                print(f"  [경고] {t['name']} 수집 실패: {e}")
                items.append({
                    "name":       t["name"],
                    "value":      "수집 중",
                    "change":     "-",
                    "change_pct": "-",
                    "direction":  "flat",
                })

    except ImportError:
        # yfinance 미설치 시 샘플 데이터 사용
        print("[경고] yfinance 미설치. 샘플 데이터를 사용합니다.")
        print("       설치: pip install yfinance")
        items = [
            {"name": "코스피",           "value": "2,712.34", "change": "+15.21", "change_pct": "+0.56%", "direction": "up"},
            {"name": "나스닥",            "value": "19,864.98","change": "+102.45","change_pct": "+0.52%", "direction": "up"},
            {"name": "S&P 500",          "value": "5,431.22", "change": "-8.10",  "change_pct": "-0.15%", "direction": "down"},
            {"name": "반도체 ETF (SOXX)","value": "238.50",   "change": "+3.20",  "change_pct": "+1.36%", "direction": "up"},
            {"name": "금 ($/oz)",        "value": "2,348.70", "change": "-5.30",  "change_pct": "-0.23%", "direction": "down"},
            {"name": "원/달러 환율",     "value": "1,398원",  "change": "+3",     "change_pct": "+0.21%", "direction": "up"},
        ]

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
