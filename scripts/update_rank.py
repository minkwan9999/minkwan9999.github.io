# [Version 2.0] - raw.html 정규식 치환 방식 폐기, posts.json 직접 조작 방식으로 전환.
# 특정 플랫폼 데이터 가져오기에 실패하면(API 키 누락, 네트워크 오류 등) 해당 플랫폼은
# 기존 posts.json에 있던 값을 그대로 유지한다 (원래 스크립트의 안전장치를 그대로 계승).
import os
import re
import json
import time
import datetime
from datetime import timezone, timedelta
import urllib.request

PLATFORM_ORDER = ["YOUTUBE", "TIKTOK", "THREADS", "INSTA", "X"]
BADGE_MAP = {
    "YOUTUBE": ("YouTube", "bg-red-500/10 text-red-400 border-red-500/30"),
    "TIKTOK": ("TikTok", "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"),
    "THREADS": ("Threads", "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"),
    "INSTA": ("Instagram", "bg-pink-500/10 text-pink-400 border-pink-500/30"),
    "X": ("X", "bg-slate-500/10 text-slate-300 border-slate-500/30"),
}

# --- 1. YouTube Data API v3 (공식 API) ---
def fetch_youtube_top():
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    items = []
    if not api_key:
        print("[WARN] YOUTUBE_API_KEY not found. Keeping existing YouTube data.")
        return items

    try:
        url = (
            "https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,statistics&chart=mostPopular&regionCode=KR&maxResults=5&key={api_key}"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            badge, color = BADGE_MAP["YOUTUBE"]
            for idx, v in enumerate(data.get("items", []), start=1):
                snip = v["snippet"]
                stat = v.get("statistics", {})
                views = int(stat.get("viewCount", 0))
                channel = snip.get("channelTitle", "크리에이터")
                title = snip.get("title", "")

                items.append({
                    "id": f"yt{idx}",
                    "platformRank": idx,
                    "platform": "YOUTUBE",
                    "platformBadge": badge,
                    "platformColor": color,
                    "creatorName": {"ko": channel, "en": channel},
                    "handle": f"@{channel.replace(' ', '_')[:20]}",
                    "categoryTag": {"ko": "주간 급상승", "en": "Trending"},
                    "rankChange": f"▲{idx}",
                    "followers": {"ko": f"{views // 10000}만 뷰", "en": f"{views // 1000}K views"},
                    "weeklyGrowth": {"ko": f"+{max(1, views // 50000)}만", "en": f"+{max(1, views // 50000)}0K"},
                    "headline": {"ko": title, "en": title},
                    "viralTopic": f"#{channel.replace(' ', '')[:15]} #인기급상승",
                    "growthFactor": {
                        "ko": "실시간 급상승 알고리즘 및 높은 완청률 기반 트래픽 폭발.",
                        "en": "Surged via recommendation algorithms.",
                    },
                    "upvotes": 500 + (idx * 50),
                    "disagrees": 10 + (idx * 5),
                })
        print(f"[SUCCESS] Fetched {len(items)} YouTube items.")
    except Exception as e:
        print(f"[ERROR] YouTube API failed: {e}. Keeping existing YouTube data.")
        return []

    return items


# --- 2. Gemini 2.5 Flash Search Grounding (TikTok/Threads/Insta/X) ---
def fetch_social_trends_via_gemini():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not found. Keeping existing TikTok/Threads/Insta/X data.")
        return {}

    prompt = """
당신은 대한민국 실시간 소셜 트렌드 분석 시스템입니다.
반드시 Google Search 기능을 사용하여 오늘 한국 기준으로 가장 화제가 된 4개 플랫폼의 실제 인기 크리에이터 또는 계정 5개씩을 분석해 순수 JSON만 반환하세요.
마크다운 코드블록(```json) 없이 오직 JSON 텍스트만 출력해야 합니다.

대상 플랫폼 키: "TIKTOK", "THREADS", "INSTA", "X"
각 플랫폼마다 정확히 5개 항목을 아래 필드 규격에 맞춰 배열로 만드세요:
[
  {
    "creatorName": "실제 활동명 또는 채널명",
    "handle": "@실제핸들아이디",
    "categoryTag": "숏폼챌린지 / 일상도파민 / 뷰티라이프 / 실시간이슈 중 택1",
    "rankChange": "▲1 / ▲2 / NEW 중 택1",
    "followers": "추정 팔로워 수 (예: 45만, 120만)",
    "weeklyGrowth": "주간 증가치 (예: +8만, +15만)",
    "headline": "이번 주 가장 크게 터진 핵심 영상/게시글 제목 1줄 요약",
    "viralTopic": "#태그1 #태그2",
    "growthFactor": "이 계정이 알고리즘을 타고 떡상한 이유 1줄 명확 분석",
    "upvotes": 350,
    "disagrees": 12
  }
]

최종 반환 JSON 포맷:
{
  "TIKTOK": [... 5개 ...],
  "THREADS": [... 5개 ...],
  "INSTA": [... 5개 ...],
  "X": [... 5개 ...]
}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)
            return json.loads(raw_text)
    except Exception as e:
        print(f"[ERROR] Gemini API failed: {e}. Keeping existing data for affected platforms.")
        return {}


def format_gemini_items(platform_key, raw_list):
    badge, color = BADGE_MAP[platform_key]
    items = []
    for idx, item in enumerate(raw_list[:5], start=1):
        items.append({
            "id": f"{platform_key.lower()[:2]}{idx}",
            "platformRank": idx,
            "platform": platform_key,
            "platformBadge": badge,
            "platformColor": color,
            "creatorName": {"ko": str(item.get("creatorName", "화제의 크리에이터")), "en": str(item.get("creatorName", "Trending Creator"))},
            "handle": str(item.get("handle", "@trend_creator")),
            "categoryTag": {"ko": str(item.get("categoryTag", "실시간 화제")), "en": str(item.get("categoryTag", "Trending"))},
            "rankChange": str(item.get("rankChange", "▲1")),
            "followers": {"ko": str(item.get("followers", "50만")), "en": str(item.get("followers", "500K"))},
            "weeklyGrowth": {"ko": str(item.get("weeklyGrowth", "+5만")), "en": str(item.get("weeklyGrowth", "+50K"))},
            "headline": {"ko": str(item.get("headline", "알고리즘 급상승 화제")), "en": str(item.get("headline", "Trending topic"))},
            "viralTopic": str(item.get("viralTopic", f"#{platform_key} #트렌드")),
            "growthFactor": {
                "ko": str(item.get("growthFactor", "알고리즘 적중 및 높은 인게이지먼트로 확산.")),
                "en": str(item.get("growthFactor", "Spread via strong algorithmic engagement.")),
            },
            "upvotes": int(item.get("upvotes", 400 - (idx * 20))),
            "disagrees": int(item.get("disagrees", 10 + (idx * 2))),
        })
    return items


def recompute_overall_ranks(all_items):
    """플랫폼 순서(YOUTUBE,TIKTOK,THREADS,INSTA,X)로 인터리빙된 종합 순위를 재계산."""
    by_platform = {p: sorted([i for i in all_items if i["platform"] == p], key=lambda x: x["platformRank"]) for p in PLATFORM_ORDER}
    for plat_idx, plat in enumerate(PLATFORM_ORDER):
        for item in by_platform[plat]:
            item["overallRank"] = (item["platformRank"] - 1) * 5 + (plat_idx + 1)
    return all_items


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_path = os.path.join(base_dir, "rank", "posts.json")

    if not os.path.exists(posts_path):
        print(f"[ERROR] File not found: {posts_path}")
        return

    with open(posts_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_by_platform = {p: [r for r in existing["ranks"] if r["platform"] == p] for p in PLATFORM_ORDER}

    # 1. YouTube 갱신 시도
    yt_items = fetch_youtube_top()
    final_by_platform = dict(existing_by_platform)
    if yt_items:
        final_by_platform["YOUTUBE"] = yt_items

    # 2. Gemini로 4개 플랫폼 갱신 시도
    social_data = fetch_social_trends_via_gemini()
    for plat_key in ["TIKTOK", "THREADS", "INSTA", "X"]:
        if plat_key in social_data and isinstance(social_data[plat_key], list) and social_data[plat_key]:
            plat_items = format_gemini_items(plat_key, social_data[plat_key])
            final_by_platform[plat_key] = plat_items
            print(f"[SUCCESS] Refreshed {plat_key} via Gemini.")
        else:
            print(f"[WARN] {plat_key} not refreshed. Keeping existing data.")

    # 3. 25개로 합치고 overallRank 재계산
    all_items = []
    for p in PLATFORM_ORDER:
        all_items.extend(final_by_platform.get(p, []))
    all_items = recompute_overall_ranks(all_items)

    kst = timezone(timedelta(hours=9))
    result = {
        "lastUpdated": datetime.datetime.now(kst).strftime("%Y.%m.%d %H:%M"),
        "ranks": all_items,
    }

    with open(posts_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] rank/posts.json updated. Total items: {len(all_items)}")


if __name__ == "__main__":
    main()
