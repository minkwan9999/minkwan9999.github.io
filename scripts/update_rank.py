import os
import re
import json
import urllib.request
import urllib.parse

# 1. YouTube Data API v3 (공식 API 연동 유지)
def fetch_youtube_top():
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    items = []
    if not api_key:
        print("Warning: YOUTUBE_API_KEY not found.")
        return items

    try:
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode=KR&maxResults=5&key={api_key}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            for idx, v in enumerate(data.get("items", []), start=1):
                snip = v["snippet"]
                stat = v.get("statistics", {})
                views = int(stat.get("viewCount", 0))
                channel = snip.get("channelTitle", "크리에이터").replace('"', '\\"')
                title = snip.get("title", "").replace('"', '\\"')
                
                items.append({
                    "id": f"yt{idx}",
                    "overallRank": (idx * 5) - 4,
                    "platformRank": idx,
                    "platform": "YOUTUBE",
                    "platformBadge": "YouTube",
                    "platformColor": "bg-red-500/10 text-red-400 border-red-500/30",
                    "creatorName": {"ko": channel, "en": channel},
                    "handle": f"@{channel.replace(' ', '_')[:20]}",
                    "categoryTag": {"ko": "주간 급상승", "en": "Trending"},
                    "rankChange": f"▲{idx}",
                    "followers": {"ko": f"{views//10000}만 뷰", "en": f"{views//1000}K views"},
                    "weeklyGrowth": {"ko": f"+{max(1, views//50000)}만", "en": f"+{max(1, views//50000)}0K"},
                    "headline": {"ko": title, "en": title},
                    "viralTopic": f"#{channel.replace(' ', '')[:15]} #인기급상승",
                    "growthFactor": {"ko": "실시간 급상승 알고리즘 및 높은 완청률 기반 트래픽 폭발.", "en": "Surged via recommendation algorithms."},
                    "upvotes": 500 + (idx * 50),
                    "disagrees": 10 + (idx * 5)
                })
        print(f"Successfully fetched {len(items)} YouTube items.")
    except Exception as e:
        print(f"YouTube API Error: {e}")

    return items

# 2. Gemini 2.5 Flash Search Grounding 기반 4개 플랫폼 실시간 분석
def fetch_social_trends_via_gemini():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found.")
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

    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=){api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            raw_text = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
            # 혹시 모를 마크다운 블록 제거
            raw_text = re.sub(r'^```json\s*', '', raw_text)
            raw_text = re.sub(r'\s*```$', '', raw_text)
            return json.loads(raw_text)
    except Exception as e:
        print(f"Gemini API Grounding Error: {e}")
        return {}

def format_gemini_items(platform_key, raw_list):
    badge_map = {
        "TIKTOK": ("TikTok", "bg-cyan-500/10 text-cyan-400 border-cyan-500/30", 1),
        "THREADS": ("Threads", "bg-emerald-500/10 text-emerald-400 border-emerald-500/30", 2),
        "INSTA": ("Instagram", "bg-pink-500/10 text-pink-400 border-pink-500/30", 3),
        "X": ("X (Twitter)", "bg-slate-500/10 text-slate-300 border-slate-500/30", 4)
    }
    badge, color, plat_idx = badge_map[platform_key]
    items = []

    for idx, item in enumerate(raw_list[:5], start=1):
        creator = str(item.get("creatorName", "화제의 크리에이터")).replace('"', '\\"')
        handle = str(item.get("handle", "@trend_creator")).replace('"', '\\"')
        category = str(item.get("categoryTag", "실시간 화제")).replace('"', '\\"')
        rank_change = str(item.get("rankChange", "▲1")).replace('"', '\\"')
        followers = str(item.get("followers", "50만")).replace('"', '\\"')
        weekly = str(item.get("weeklyGrowth", "+5만")).replace('"', '\\"')
        headline = str(item.get("headline", "알고리즘 급상승 화제")).replace('"', '\\"')
        viral_topic = str(item.get("viralTopic", f"#{platform_key} #트렌드")).replace('"', '\\"')
        growth = str(item.get("growthFactor", "알고리즘 적중 및 높은 인게이지먼트로 확산.")).replace('"', '\\"')

        items.append({
            "id": f"{platform_key.lower()[:2]}{idx}",
            "overallRank": (idx * 5) - (4 - plat_idx),
            "platformRank": idx,
            "platform": platform_key,
            "platformBadge": badge,
            "platformColor": color,
            "creatorName": {"ko": creator, "en": creator},
            "handle": handle,
            "categoryTag": {"ko": category, "en": category},
            "rankChange": rank_change,
            "followers": {"ko": followers, "en": followers},
            "weeklyGrowth": {"ko": weekly, "en": weekly},
            "headline": {"ko": headline, "en": headline},
            "viralTopic": viral_topic,
            "growthFactor": {"ko": growth, "en": growth},
            "upvotes": int(item.get("upvotes", 400 - (idx * 20))),
            "disagrees": int(item.get("disagrees", 10 + (idx * 2)))
        })
    return items

def build_js_block(item):
    return f"""      {{
        id: "{item['id']}", overallRank: {item['overallRank']}, platformRank: {item['platformRank']}, platform: "{item['platform']}", platformBadge: "{item['platformBadge']}",
        platformColor: "{item['platformColor']}",
        creatorName: {{ ko: "{item['creatorName']['ko']}", en: "{item['creatorName']['en']}" }}, handle: "{item['handle']}",
        categoryTag: {{ ko: "{item['categoryTag']['ko']}", en: "{item['categoryTag']['en']}" }}, rankChange: "{item['rankChange']}",
        followers: {{ ko: "{item['followers']['ko']}", en: "{item['followers']['en']}" }}, weeklyGrowth: {{ ko: "{item['weeklyGrowth']['ko']}", en: "{item['weeklyGrowth']['en']}" }},
        headline: {{ ko: "{item['headline']['ko']}", en: "{item['headline']['en']}" }},
        viralTopic: "{item['viralTopic']}",
        growthFactor: {{ ko: "{item['growthFactor']['ko']}", en: "{item['growthFactor']['en']}" }},
        upvotes: {item['upvotes']}, disagrees: {item['disagrees']}
      }}"""

def replace_platform_block(content, comment_num, platform_name, js_items_str, next_comment_num=None):
    if next_comment_num:
        pattern = rf'(/\* =+ {comment_num}\. {platform_name} TOP 5 =+ \*/\s*\n)(.*?)(,\s*\n\s*/\* =+ {next_comment_num}\.)'
        if re.search(pattern, content, flags=re.DOTALL):
            return re.sub(pattern, rf'\g<1>{js_items_str}\g<3>', content, flags=re.DOTALL)
    else:
        pattern = rf'(/\* =+ {comment_num}\. {platform_name} TOP 5 =+ \*/\s*\n)(.*?)(\n\s*\];)'
        if re.search(pattern, content, flags=re.DOTALL):
            return re.sub(pattern, rf'\g<1>{js_items_str}\g<3>', content, flags=re.DOTALL)
    return content

def main():
    html_path = "rank/raw.html"
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. YouTube Data API 갱신
    yt_items = fetch_youtube_top()
    if yt_items:
        yt_str = ",\n".join([build_js_block(i) for i in yt_items])
        content = replace_platform_block(content, 1, "YOUTUBE", yt_str, 2)

    # 2. Gemini Search Grounding (TikTok, Threads, Insta, X) 갱신
    social_data = fetch_social_trends_via_gemini()
    targets = [
        ("TIKTOK", 2, 3),
        ("THREADS", 3, 4),
        ("INSTA", 4, 5),
        ("X", 5, None)
    ]

    for plat_key, num, next_num in targets:
        if plat_key in social_data and isinstance(social_data[plat_key], list):
            plat_items = format_gemini_items(plat_key, social_data[plat_key])
            if plat_items:
                plat_str = ",\n".join([build_js_block(i) for i in plat_items])
                content = replace_platform_block(content, num, plat_key, plat_str, next_num)
                print(f"Successfully processed {plat_key} with Gemini data.")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Rank auto-update completed.")

if __name__ == "__main__":
    main()
