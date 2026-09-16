# [Version 2.1]
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
        "id": f"p_auto_{int(time.time())}",
        "cardType": "TRACK",
        "eraTag": {"ko": "2026년 · 자율주행", "en": "2026 · Autonomous Driving"},
        "badgeText": {"ko": "빅마우스 성적표 ✓", "en": "Verified Track Record ✓"},
        "badgeClass": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        "author": {"ko": "일론 머스크", "en": "Elon Musk"},
        "authorTitle": {"ko": "테슬라 CEO", "en": "CEO of Tesla"},
        "avatar": "🚕",
        "imageBeforeUrl": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800&auto=format&fit=crop&q=80",
        "imageCaption": {"ko": "테슬라 FSD 테스트 주행 현장", "en": "Tesla FSD beta testing scene"},
        "title": {
          "ko": "2026년까지 완전 자율주행으로 수익을 내지 못하면 사업을 접는다",
          "en": "If Tesla doesn't achieve fully autonomous profitability by 2026, we fail"
        },
        "quoteSource": {"ko": "테슬라 실적 컨퍼런스 콜 및 X 포스팅", "en": "Tesla Earnings Call & X Post"},
        "quoteText": {
          "ko": "우리는 올해와 내년에 걸쳐 완전 자율주행(FSD) 승인과 무인 로보택시 대량 양산을 완수할 것입니다. 인간 운전자보다 압도적으로 안전해집니다.",
          "en": "We will achieve full autonomy and mass production of uncrewed robotaxis. It will be overwhelmingly safer than human drivers."
        },
        "timelineLabel": {"ko": "📊 2026년 현재 성적표", "en": "📊 2026 Current Track Record"},
        "realityStat": {"ko": "규제 승인 대기 및 감독자 탑승 유지", "en": "Regulatory pending & supervision required"},
        "realityText": {
          "ko": "여전히 완전 무인 자율주행은 주요 주정부의 엄격한 승인 심사와 안전 운전자 상시 대기 조건 속에서 제한적으로 테스트되고 있습니다.",
          "en": "True uncrewed autonomy remains under strict state regulatory review and requires safety drivers in most jurisdictions."
        },
        "actionHighlight": {
          "ko": "거대한 비전과 혁신적 기술 발표는 시장의 기대감을 모으지만, 물리적 안전 규제와 인프라의 장벽은 언제나 예상보다 높고 오래 걸립니다.",
          "en": "Grand visions capture market excitement, but physical safety regulations and infrastructure barriers always take longer than expected."
        },
        "upvotes": 312,
        "disagrees": 45
    }

    new_item_str = json.dumps(new_item, ensure_ascii=False, indent=6)

    if "const POSTS = [" in content:
        parts = content.split("const POSTS = [")
        header = parts[0] + "const POSTS = ["
        rest = parts[1]
        idx = rest.rfind("];")
        if idx != -1:
            array_content = rest[:idx].strip()
            footer = rest[idx:]
            if array_content and not array_content.endswith(","):
                array_content += ","
            new_content = header + "\n" + array_content + "\n" + new_item_str + "\n" + footer
        else:
            print("[ERROR] Could not find closing ]; for POSTS")
            sys.exit(1)
    else:
        print("[ERROR] const POSTS = [ not found in raw.html")
        sys.exit(1)

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
