import os
import re
import json
import time
import sys
import datetime
from datetime import timezone, timedelta

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, "named", "raw.html")
    index_path = os.path.join(base_dir, "index.html")
    
    print(f"[INFO] Target named HTML path: {html_path}")

    if not os.path.exists(html_path):
        print(f"[ERROR] File not found at {html_path}")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_item = {
        "cardType": "ONGOING",
        "eraTag": {"ko": "2026년 · 자율주행", "en": "2026 · Autonomous Driving"},
        "statusBadge": {"ko": "진행중 ⏳", "en": "Pending Verdict ⏳"},
        "statusColor": "bg-slate-500/10 text-slate-300 border-slate-500/30",
        "author": {"ko": "일론 머스크", "en": "Elon Musk"},
        "authorTitle": {"ko": "테슬라 CEO", "en": "CEO of Tesla"},
        "avatar": "🚕",
        "imageBeforeUrl": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800&auto=format&fit=crop&q=80",
        "imageCaption": {"ko": "테슬라 FSD 테스트 주행", "en": "Tesla FSD beta testing"},
        "title": {
          "ko": "2026년 안에 무인 로보택시가 미국 전역을 달린다",
          "en": "Robotaxis will span the US by 2026"
        },
        "quoteSource": {"ko": "테슬라 실적 발표", "en": "Tesla Earnings Call"},
        "quoteText": {
          "ko": "2026년 안에 운전대와 페달이 없는 로보택시가 대량 양산되어 미국 전역의 거리를 장악할 것입니다.",
          "en": "By 2026, Robotaxis without steering wheels or pedals will take over the streets."
        },
        "timelineLabel": {"ko": "⏳ 현재 진행 상황", "en": "⏳ Current Status"},
        "realityStat": {"ko": "규제 승인 및 완성도 논쟁 중", "en": "Regulatory approval debate ongoing"},
        "realityText": {
          "ko": "완전 자율주행(레벨 4 이상)의 규제 당국 승인과 돌발 변수 대처 능력을 두고 여전히 업계와 시장의 팽팽한 논쟁이 진행 중입니다.",
          "en": "Intense debate continues globally regarding Level 4+ autonomous regulatory approval."
        },
        "actionHighlight": {
          "ko": "거대한 비전은 막대한 자본을 끌어모으지만, 실제 세상의 인프라와 규제가 바뀌는 속도는 언제나 선구자의 호언장담보다 느립니다.",
          "en": "Grand visions attract capital, but physical infrastructure and regulation always lag."
        },
        "upvotes": 215,
        "disagrees": 184
    }

    new_item['id'] = f"p_auto_{int(time.time())}"
    new_item_str = json.dumps(new_item, ensure_ascii=False, indent=6)

    match = re.search(r'(const POSTS = \[.*?\})(\s*\];)', content, flags=re.DOTALL)
    if not match:
        print("[ERROR] POSTS array closing not found in HTML.")
        sys.exit(1)

    new_content = content[:match.end(1)] + ",\n" + new_item_str + match.group(2)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("[SUCCESS] Appended new record to named/raw.html.")

    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            idx_content = f.read()

        kst = timezone(timedelta(hours=9))
        now_str = datetime.datetime.now(kst).strftime("%Y.%m.%d %H:%M")
        
        new_idx_content = re.sub(
            r'(<span[^>]*id="insight-update-time"[^>]*>)(.*?)(</span>)',
            fr'\g<1>마지막 업데이트: {now_str}\g<3>',
            idx_content
        )
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_idx_content)
        print(f"[SUCCESS] index.html time updated to: {now_str}")
    else:
        print("[WARN] index.html not found at root.")

if __name__ == "__main__":
    main()
