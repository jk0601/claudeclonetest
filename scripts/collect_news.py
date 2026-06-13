"""
scripts/collect_news.py
역할: 네이버 뉴스 경제 섹션을 스크래핑하여 data/news.json 으로 저장합니다.
      RSS 피드 방식은 GitHub Actions 에서 차단되므로 직접 스크래핑합니다.

필요 라이브러리: requests, beautifulsoup4 (requirements.txt 에 포함)
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

SECTIONS = [
    {"url": "https://news.naver.com/section/101", "source": "네이버 경제"},
    {"url": "https://news.naver.com/section/105", "source": "네이버 IT/과학"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

MAX_ITEMS = 8


def scrape_section(url, source):
    items = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        for tag in soup.select(".sa_text_title")[:5]:
            title = tag.get_text(strip=True)
            link = tag.get("href", "")
            if title and link:
                items.append({
                    "title": title,
                    "summary": "요약 정보 없음",
                    "source": source,
                    "date": datetime.now(KST).strftime("%Y-%m-%d"),
                    "link": link,
                })
    except Exception as e:
        print(f"[경고] 스크래핑 실패 ({source}): {e}")
    return items


def main():
    now_kst = datetime.now(KST)
    all_items = []

    for sec in SECTIONS:
        fetched = scrape_section(sec["url"], sec["source"])
        print(f"  {sec['source']}: {len(fetched)}건 수집")
        all_items.extend(fetched)
        if len(all_items) >= MAX_ITEMS:
            break

    if not all_items:
        print("[경고] 수집 실패. 샘플 데이터를 사용합니다.")
        all_items = [{
            "title": "뉴스 데이터 수집 중입니다",
            "summary": "잠시 후 다시 시도하면 실제 뉴스가 표시됩니다.",
            "source": "샘플",
            "date": now_kst.strftime("%Y-%m-%d"),
            "link": "https://news.naver.com/section/101",
        }]

    result = {
        "updated_at": now_kst.strftime("%Y-%m-%d %H:%M"),
        "items": all_items[:MAX_ITEMS],
    }

    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[완료] data/news.json 저장 완료: {len(result['items'])}건")


if __name__ == "__main__":
    main()
