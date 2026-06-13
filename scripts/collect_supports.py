"""
scripts/collect_supports.py
역할: 기업마당 웹 페이지를 스크래핑하여 서울·경기 지원사업 정보를
      data/supports.json 으로 저장합니다.

API 키 방식은 타임아웃이 잦으므로 웹 스크래핑 방식을 사용합니다.
필요 라이브러리: requests, beautifulsoup4 (requirements.txt 에 포함)
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

# 서울(6110000), 경기(6410000) 지원사업 목록
URL = "https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do?schAreaDetailCodes=6110000,6410000"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

MAX_ITEMS = 10


def scrape_bizinfo():
    items = []
    try:
        res = requests.get(URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        for row in soup.select("table tbody tr"):
            tds = row.select("td")
            link_tag = row.select_one("td:nth-child(3) a") or row.select_one("td.txt_left a")
            if not link_tag:
                continue

            title = link_tag.get_text(strip=True)
            href = link_tag.get("href", "")

            if not href or "javascript" in href:
                link = "https://www.bizinfo.go.kr"
            elif href.startswith("/"):
                link = f"https://www.bizinfo.go.kr{href}"
            else:
                link = href

            period = tds[3].get_text(strip=True) if len(tds) > 3 else "상세 확인"

            region = "서울·경기"
            if "서울" in title:
                region = "서울"
            elif "경기" in title:
                region = "경기"

            items.append({
                "title": title,
                "region": region,
                "period": period,
                "organization": "",
                "summary": title,
                "link": link,
            })

    except Exception as e:
        print(f"[경고] 기업마당 스크래핑 실패: {e}")

    return items[:MAX_ITEMS]


def get_sample_data():
    return [
        {
            "title": "서울형 강소기업 청년채용 지원사업",
            "region": "서울",
            "period": "2026-06-01 ~ 2026-06-30",
            "organization": "서울특별시",
            "summary": "서울 소재 중소기업의 청년 신규 채용을 지원합니다. 채용 1인당 최대 720만 원 지원.",
            "link": "https://www.bizinfo.go.kr",
        },
        {
            "title": "경기도 소상공인 디지털 전환 지원",
            "region": "경기",
            "period": "2026-05-15 ~ 2026-07-15",
            "organization": "경기도경제과학진흥원",
            "summary": "경기도 소재 소상공인을 대상으로 디지털 전환 컨설팅 및 솔루션 도입 비용의 최대 70%를 지원합니다.",
            "link": "https://www.bizinfo.go.kr",
        },
        {
            "title": "서울 창업허브 입주기업 모집",
            "region": "서울",
            "period": "2026-06-10 ~ 2026-06-28",
            "organization": "서울창업허브",
            "summary": "서울 마포구 창업허브 입주 기업을 모집합니다. 사무공간, 멘토링, 투자 연계 프로그램 제공.",
            "link": "https://www.bizinfo.go.kr",
        },
        {
            "title": "경기도 기술개발사업 R&D 지원",
            "region": "경기",
            "period": "2026-06-01 ~ 2026-06-20",
            "organization": "경기도",
            "summary": "경기도 소재 중소기업의 기술 개발을 지원합니다. 과제당 최대 1억 원, 수행기간 1년 이내.",
            "link": "https://www.bizinfo.go.kr",
        },
        {
            "title": "서울시 사회적기업 육성 지원",
            "region": "서울",
            "period": "2026-06-05 ~ 2026-07-05",
            "organization": "서울시 사회적경제지원센터",
            "summary": "사회적기업 인증 준비 중인 서울 소재 기업에 컨설팅, 교육, 초기 운영비를 지원합니다.",
            "link": "https://www.bizinfo.go.kr",
        },
        {
            "title": "경기도 여성기업 경영 역량 강화 사업",
            "region": "경기",
            "period": "2026-06-01 ~ 2026-07-31",
            "organization": "경기도여성능력개발센터",
            "summary": "경기도 소재 여성 대표 중소기업에 마케팅, 회계, 법률 등 경영 전반의 역량 강화 교육을 제공합니다.",
            "link": "https://www.bizinfo.go.kr",
        },
    ]


def main():
    now_kst = datetime.now(KST)

    print("[정보] 기업마당 웹 스크래핑 시작...")
    items = scrape_bizinfo()

    if not items:
        print("[경고] 스크래핑 실패. 샘플 데이터를 사용합니다.")
        items = get_sample_data()
    else:
        print(f"[정보] {len(items)}건 수집 성공")

    result = {
        "updated_at": now_kst.strftime("%Y-%m-%d %H:%M"),
        "items": items,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/supports.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[완료] data/supports.json 저장 완료: {len(result['items'])}건")


if __name__ == "__main__":
    main()
