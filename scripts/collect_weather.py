"""
scripts/collect_weather.py
역할: 날씨 정보를 수집하고 코디를 자동 생성하여 data/weather.json 으로 저장합니다.

사용 API: Open-Meteo (무료, API 키 불필요)
  - https://open-meteo.com/
  - 서울 위도/경도를 사용합니다.

공기질 API: Open-Meteo Air Quality (무료, API 키 불필요)
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# 한국 표준시 (UTC+9)
KST = timezone(timedelta(hours=9))


# ──────────────────────────────────────
# 날씨 코드 → 한글 설명 변환표
# WMO Weather Interpretation Codes 기준
# ──────────────────────────────────────
WEATHER_CODES = {
    0: "맑음",
    1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림",
    45: "안개", 48: "결빙 안개",
    51: "가벼운 이슬비", 53: "이슬비", 55: "진한 이슬비",
    61: "약한 비", 63: "비", 65: "강한 비",
    71: "약한 눈", 73: "눈", 75: "강한 눈",
    80: "소나기", 81: "강한 소나기", 82: "폭우",
    95: "뇌우", 99: "뇌우 + 우박",
}


def fetch_json(url):
    """URL에서 JSON 데이터를 가져옵니다."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read())


def get_outfit(summary, temp_max, temp_min, rain):
    """날씨 조건에 따라 코디 문장과 참고 이미지 URL을 반환합니다."""

    # 비/소나기 여부
    is_rainy = rain != "없음"
    # 일교차
    temp_diff = temp_max - temp_min

    if is_rainy:
        text = (
            "비 오는 날엔 방수 재킷이나 레인코트를 챙기세요. "
            "어두운 색 하의와 방수 신발로 마무리하면 실용적입니다. "
            "접이식 우산도 잊지 마세요."
        )
        img = "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=600&q=80"
    elif temp_max >= 27:
        text = (
            f"최고 {temp_max}°C의 더운 날씨입니다. "
            "반팔 티셔츠, 린넨 셔츠, 가벼운 면 팬츠를 추천합니다. "
            "자외선 차단을 위해 선크림과 가벼운 모자를 챙기세요."
        )
        img = "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&q=80"
    elif temp_max >= 18:
        if temp_diff >= 10:
            text = (
                f"일교차가 {temp_diff}°C로 큽니다. "
                "아침저녁엔 얇은 겉옷이나 가디건을 챙기고, "
                "낮에는 가볍게 반팔 또는 얇은 긴팔 티셔츠를 입으세요."
            )
            img = "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&q=80"
        else:
            text = (
                "활동하기 좋은 선선한 날씨입니다. "
                "얇은 긴팔 티셔츠나 맨투맨에 청바지 조합이 잘 어울립니다. "
                "얇은 가디건을 하나 챙기면 완벽합니다."
            )
            img = "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&q=80"
    else:
        text = (
            f"최고 기온이 {temp_max}°C의 쌀쌀한 날씨입니다. "
            "니트, 코트, 머플러를 추천합니다. "
            "두꺼운 한 겹보다 얇은 레이어드 스타일이 체온 조절에 효과적입니다."
        )
        img = "https://images.unsplash.com/photo-1511401139252-f158d3209c17?w=600&q=80"

    return text, img


def main():
    now_kst = datetime.now(KST)
    today = now_kst.strftime("%Y-%m-%d")

    # ── Open-Meteo API 호출 (서울: 위도 37.5665, 경도 126.9780) ──
    params = urllib.parse.urlencode({
        "latitude": 37.5665,
        "longitude": 126.9780,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Asia/Seoul",
        "forecast_days": 1,
    })
    weather_url = f"https://api.open-meteo.com/v1/forecast?{params}"

    try:
        weather_data = fetch_json(weather_url)
        daily = weather_data["daily"]

        code     = daily["weathercode"][0]
        temp_max = round(daily["temperature_2m_max"][0])
        temp_min = round(daily["temperature_2m_min"][0])
        precip   = daily["precipitation_sum"][0]

        summary = WEATHER_CODES.get(code, "날씨 정보 없음")
        rain    = f"{precip}mm 예상" if precip and precip > 0 else "없음"

    except Exception as e:
        print(f"[경고] 날씨 API 오류: {e}. 샘플 데이터를 사용합니다.")
        temp_max, temp_min = 24, 16
        summary = "맑음"
        rain    = "없음"

    # ── 공기질 (미세먼지) ──
    try:
        aq_params = urllib.parse.urlencode({
            "latitude": 37.5665,
            "longitude": 126.9780,
            "hourly": "pm10",
            "timezone": "Asia/Seoul",
            "forecast_days": 1,
        })
        aq_data = fetch_json(f"https://air-quality-api.open-meteo.com/v1/air-quality?{aq_params}")
        pm10 = aq_data["hourly"]["pm10"][12]  # 정오 기준

        if pm10 is None:
            dust = "데이터 없음"
        elif pm10 < 30:
            dust = f"좋음 ({pm10:.0f}㎍/㎥)"
        elif pm10 < 80:
            dust = f"보통 ({pm10:.0f}㎍/㎥)"
        elif pm10 < 150:
            dust = f"나쁨 ({pm10:.0f}㎍/㎥)"
        else:
            dust = f"매우 나쁨 ({pm10:.0f}㎍/㎥)"

    except Exception as e:
        print(f"[경고] 공기질 API 오류: {e}")
        dust = "정보 없음"

    # ── 코디 생성 ──
    outfit_text, outfit_image_url = get_outfit(summary, temp_max, temp_min, rain)

    # ── JSON 저장 ──
    result = {
        "date": today,
        "region": "서울",
        "summary": summary,
        "temp_min": str(temp_min),
        "temp_max": str(temp_max),
        "rain": rain,
        "dust": dust,
        "outfit_text": outfit_text,
        "outfit_image_url": outfit_image_url,
        "updated_at": now_kst.strftime("%Y-%m-%d %H:%M"),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/weather.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[완료] data/weather.json 저장 완료: {summary}, {temp_min}~{temp_max}°C")


if __name__ == "__main__":
    main()
