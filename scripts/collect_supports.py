"""
scripts/collect_supports.py
역할: 기업마당(bizinfo.go.kr) 공개 API에서 서울·경기 지원사업을 수집하여
      data/supports.json 으로 저장합니다.

사용 API: 기업마당 지원사업정보 서비스 (공공데이터포털)
  - https://www.data.go.kr/data/15105143/openapi.do
  - 일반 인증키(Decoding) 필요: GitHub Actions Secrets 에 BIZINFO_API_KEY 로 등록하세요.

API 키 등록 방법:
  1. https://www.data.go.kr 에서 해당 API 신청
  2. GitHub 저장소 → Settings → Secrets and variables → Actions
  3. New repository secret → Name: BIZINFO_API_KEY, Value: (발급받은 키)

API 키가 없으면 샘플 데이터를 사용합니다.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

# ──────────────────────────────────────
# API 설정
# GitHub Actions Secrets 에서 환경변수로 주입됩니다.
# 로컬 실행 시에는 export BIZINFO_API_KEY=발급키 로 설정하세요.
# ──────────────────────────────────────
API_KEY = os.environ.get("BIZINFO_API_KEY", "")
API_BASE = "https://www.bizinfo.go.kr/uss/rss/bizInfoServiceJSON.do"

# 수집 대상 지역
TARGET_REGIONS = ["서울", "경기"]
MAX_ITEMS = 10


def fetch_supports_api():
    """기업마당 API에서 지원사업 목록을 가져옵니다."""
    items = []

    for region in TARGET_REGIONS:
        params = urllib.parse.urlencode({
            "crtfcKey": API_KEY,
            "dataType": "json",
            "pageIndex": 1,
            "pageUnit": 5,
            "searchCnd": region,
        })
        url = f"{API_BASE}?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read())

            for entry in data.get("jsonArray", []):
                items.append({
                    "title":        entry.get("PBANC_TASK_NM", "제목 없음"),
                    "region":       region,
                    "period":       f"{entry.get('RCPT_BGNG_YMD', '')} ~ {entry.get('RCPT_END_YMD', '')}",
                    "organization": entry.get("EXCL_INST_NM", "기관명 없음"),
                    "summary":      entry.get("BSNS_PURP_CONT", "요약 정보 없음")[:150],
                    "link":         entry.get("DETL_PG_URL", "https://www.bizinfo.go.kr"),
                })

        except Exception as e:
            print(f"[경고] 기업마당 API 오류 ({region}): {e}")

    return items


def get_sample_data(now_kst):
    """API 키가 없거나 오류 시 반환할 샘플 데이터입니다."""
    today = now_kst.strftime("%Y-%m-%d")
    return [
        {
            "title": "서울형 강소기업 청년채용 지원사업",
            "region": "서울",
            "period": f"2026-06-01 ~ 2026-06-30",
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

    if API_KEY:
        print(f"[정보] API 키 확인됨. 기업마당 API 를 호출합니다.")
        items = fetch_supports_api()
    else:
        # API 키가 없으면 샘플 데이터 사용
        print("[경고] BIZINFO_API_KEY 환경변수가 설정되지 않았습니다.")
        print("       GitHub Secrets 에 등록하면 실제 데이터가 수집됩니다.")
        print("       현재는 샘플 데이터를 사용합니다.")
        items = get_sample_data(now_kst)

    # 수집 실패 시 샘플 사용
    if not items:
        print("[경고] 수집된 데이터 없음. 샘플 데이터를 사용합니다.")
        items = get_sample_data(now_kst)

    result = {
        "updated_at": now_kst.strftime("%Y-%m-%d %H:%M"),
        "items": items[:MAX_ITEMS],
    }

    os.makedirs("data", exist_ok=True)
    with open("data/supports.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[완료] data/supports.json 저장 완료: {len(result['items'])}건")


if __name__ == "__main__":
    main()
