import os
import re
import json
import urllib.request

def fetch_youtube_top():
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    items = []
    if not api_key:
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
                items.append({
                    "id": f"yt{idx}",
                    "overallRank": (idx * 5) - 4,
                    "platformRank": idx,
                    "platform": "YOUTUBE",
                    "platformBadge": "YouTube",
                    "platformColor": "bg-red-500/10 text-red-400 border-red-500/30",
                    "creatorName": {"ko": snip.get("channelTitle", "크리에이터"), "en": snip.get("channelTitle", "Creator")},
                    "handle": f"@{snip.get('channelTitle', 'creator').replace(' ', '_')}",
                    "categoryTag": {"ko": "주간 급상승", "en": "Trending"},
                    "rankChange": f"▲{idx}",
                    "followers": {"ko": f"{views//10000}만 뷰", "en": f"{views//1000}K views"},
                    "weeklyGrowth": {"ko": f"+{views//50000}만", "en": f"+{views//50000}0K"},
                    "headline": {"ko": snip.get("title", ""), "en": snip.get("title", "")},
                    "viralTopic": f"#{snip.get('channelTitle', '').replace(' ', '')} #인기급상승",
                    "growthFactor": {"ko": "실시간 급상승 알고리즘 및 높은 완청률 기반 트래픽 폭발.", "en": "Surged via real-time recommendation feed algorithms."},
                    "upvotes": 500 + (idx * 50),
                    "disagrees": 10 + (idx * 5)
                })
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

    match = re.search(r'const RANKS = (\[.*?\]);', content, flags=re.DOTALL)
    if not match:
        print("Error: RANKS array not found.")
        return

    ranks_data = json.loads(match.group(1))
    yt_new = fetch_youtube_top()

    if yt_new:
        non_yt = [item for item in ranks_data if item.get("platform") != "YOUTUBE"]
        ranks_data = yt_new + non_yt

    new_json = json.dumps(ranks_data, ensure_ascii=False, indent=2)
    new_content = re.sub(r'const RANKS = \[.*?\];', f'const RANKS = {new_json};', content, flags=re.DOTALL)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Successfully updated rank/raw.html")

if __name__ == "__main__":
    main()
