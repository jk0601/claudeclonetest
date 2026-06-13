"""
scripts/collect_news.py
역할: 공개 RSS 피드에서 뉴스를 수집하여 data/news.json 으로 저장합니다.

수집 출처 (GitHub Actions 환경에서도 동작하는 공개 RSS):
  - Google News 한국어 RSS (차단 없음, 최신 뉴스)
  - 한겨레 RSS
  - 조선일보 RSS
  - KBS World RSS
"""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import html
import re

KST = timezone(timedelta(hours=9))

RSS_FEEDS = [
    {
        "url": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        "source": "Google 뉴스",
    },
    {
        "url": "https://www.hani.co.kr/rss/",
        "source": "한겨레",
    },
    {
        "url": "https://www.chosun.com/arc/outboundfeeds/rss/",
        "source": "조선일보",
    },
    {
        "url": "https://world.kbs.co.kr/rss/rss_news.htm?lang=k",
        "source": "KBS",
    },
]

MAX_ITEMS = 8


def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def parse_rss(url, source):
    items = []
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)",
                "Accept": "application/rss+xml, application/xml, text/xml",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            content = res.read()

        root = ET.fromstring(content)
        channel = root.find("channel")
        entry_list = channel.findall("item") if channel is not None else []

        for item in entry_list[:3]:
            title    = clean_text(item.findtext("title", ""))
            link     = clean_text(item.findtext("link", ""))
            summary  = clean_text(item.findtext("description", ""))
            pub_date = item.findtext("pubDate", "")

            if not link:
                link = clean_text(item.findtext("guid", ""))

            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_date).astimezone(KST)
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                date_str = datetime.now(KST).strftime("%Y-%m-%d")

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
        print(f"  {feed['source']}: {len(fetched)}건 수집")
        all_items.extend(fetched)
        if len(all_items) >= MAX_ITEMS:
            break

    if not all_items:
        print("[경고] 모든 RSS 수집 실패. 샘플 데이터를 사용합니다.")
        all_items = [{
            "title": "뉴스 데이터 수집 중입니다",
            "summary": "잠시 후 다시 시도하면 실제 뉴스가 표시됩니다.",
            "source": "샘플",
            "date": now_kst.strftime("%Y-%m-%d"),
            "link": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
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
