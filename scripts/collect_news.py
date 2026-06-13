"""
scripts/collect_news.py
역할: 공개 RSS 피드에서 뉴스를 수집하여 data/news.json 으로 저장합니다.

수집 출처 (공개 RSS - API 키 불필요):
  - 네이버 뉴스 RSS (주요 뉴스)
  - 연합뉴스 RSS

RSS 란?
  웹사이트가 제공하는 뉴스 목록 파일로, XML 형식으로 제공됩니다.
  별도 로그인이나 API 키 없이 누구나 가져올 수 있습니다.
"""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import html
import re

KST = timezone(timedelta(hours=9))

# ──────────────────────────────────────
# 수집할 RSS 피드 목록
# ──────────────────────────────────────
RSS_FEEDS = [
    {
        "url": "https://feeds.feedburner.com/yonhapnewsrss",
        "source": "연합뉴스",
    },
    # 네이버 주요 뉴스 RSS
    {
        "url": "https://news.naver.com/main/rss/allNew.nhn?officeId=001",
        "source": "연합뉴스(네이버)",
    },
    {
        "url": "https://news.naver.com/main/rss/allNew.nhn?officeId=022",
        "source": "세계일보(네이버)",
    },
    {
        "url": "https://news.naver.com/main/rss/allNew.nhn?officeId=081",
        "source": "서울신문(네이버)",
    },
]

# 수집할 기사 최대 개수
MAX_ITEMS = 8


def clean_text(text):
    """HTML 태그와 특수문자를 제거하고 깔끔한 텍스트로 반환합니다."""
    if not text:
        return ""
    # HTML 엔티티 디코딩 (&amp; → & 등)
    text = html.unescape(text)
    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    # 연속 공백 정리
    return text.strip()


def parse_rss(url, source):
    """RSS URL 에서 뉴스 목록을 가져옵니다."""
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            content = res.read()

        root = ET.fromstring(content)
        channel = root.find("channel")
        if channel is None:
            return items

        for item in channel.findall("item")[:3]:  # 피드당 최대 3개
            title   = clean_text(item.findtext("title", ""))
            link    = clean_text(item.findtext("link", ""))
            summary = clean_text(item.findtext("description", ""))
            pub_date = item.findtext("pubDate", "")

            # 날짜 파싱 (형식이 다양하므로 단순 처리)
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_date).astimezone(KST)
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                date_str = datetime.now(KST).strftime("%Y-%m-%d")

            # 요약이 너무 길면 잘라냅니다
            if len(summary) > 150:
                summary = summary[:150] + "..."

            if title and link:
                items.append({
                    "title": title,
                    "summary": summary if summary else "요약 정보 없음",
                    "source": source,
                    "date": date_str,
                    "link": link,
                })

    except Exception as e:
        print(f"[경고] RSS 수집 실패 ({source}): {e}")

    return items


def main():
    now_kst = datetime.now(KST)
    all_items = []

    for feed in RSS_FEEDS:
        fetched = parse_rss(feed["url"], feed["source"])
        all_items.extend(fetched)
        if len(all_items) >= MAX_ITEMS:
            break

    # 수집에 실패하면 샘플 데이터 사용
    if not all_items:
        print("[경고] 모든 RSS 수집 실패. 샘플 데이터를 사용합니다.")
        all_items = [
            {
                "title": "뉴스 데이터 수집 중입니다",
                "summary": "GitHub Actions 가 실행되면 실제 뉴스가 이 자리에 표시됩니다.",
                "source": "샘플",
                "date": now_kst.strftime("%Y-%m-%d"),
                "link": "https://news.naver.com",
            }
        ]

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
