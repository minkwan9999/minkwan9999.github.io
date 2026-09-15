import os
import re
import json
import urllib.request

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
                channel = snip.get("channelTitle", "크리에이터")
                title = snip.get("title", "").replace('"', '\\"')
                
                items.append({
                    "id": f"yt{idx}",
                    "overallRank": (idx * 5) - 4,
                    "platformRank": idx,
                    "platform": "YOUTUBE",
                    "platformBadge": "YouTube",
                    "platformColor": "bg-red-500/10 text-red-400 border-red-500/30",
                    "creatorName": {"ko": channel, "en": channel},
                    "handle": f"@{channel.replace(' ', '_')}",
                    "categoryTag": {"ko": "주간 급상승", "en": "Trending"},
                    "rankChange": f"▲{idx}",
                    "followers": {"ko": f"{views//10000}만 뷰", "en": f"{views//1000}K views"},
                    "weeklyGrowth": {"ko": f"+{views//50000}만", "en": f"+{views//50000}0K"},
                    "headline": {"ko": title, "en": title},
                    "viralTopic": f"#{channel.replace(' ', '')} #인기급상승",
                    "growthFactor": {"ko": "실시간 급상승 알고리즘 및 높은 완청률 기반 트래픽 폭발.", "en": "Surged via real-time recommendation feed algorithms."},
                    "upvotes": 500 + (idx * 50),
                    "disagrees": 10 + (idx * 5)
                })
        print(f"Successfully fetched {len(items)} YouTube items.")
    except Exception as e:
        print(f"YouTube API Error: {e}")

    return items

def main():
    html_path = "rank/raw.html"
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    yt_new = fetch_youtube_top()
    if not yt_new:
        print("No YouTube data fetched. Skipping update.")
        return

    # 유튜브 5개 항목을 자바스크립트 객체 리스트 문자열로 변환
    yt_js_blocks = []
    for item in yt_new:
        block = f"""      {{
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
        yt_js_blocks.append(block)

    replacement_yt = ",\n".join(yt_js_blocks)

    # rank/raw.html 내 YOUTUBE TOP 5 영역만 정밀 치환
    pattern = r'(/\* =+ 1\. YOUTUBE TOP 5 =+ \*/\s*\n)(.*?)(,\s*\n\s*/\* =+ 2\. TIKTOK TOP 5)'
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(
            pattern,
            rf'\g<1>{replacement_yt}\g<3>',
            content,
            flags=re.DOTALL
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated YouTube rank in rank/raw.html")
    else:
        print("Error: Could not find YOUTUBE TOP 5 comment block in rank/raw.html")

if __name__ == "__main__":
    main()
