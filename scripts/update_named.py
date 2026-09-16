import os
import re
import json
import urllib.request
import urllib.parse
import time
import sys

def fetch_new_named_item():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[WARN] GEMINI_API_KEY is missing.")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = """
    당신은 과거 빅마우스들의 발언을 추적하는 팩트체커입니다. Google Search를 활용하여, 
    글로벌 빅테크 CEO, 금융계 인사, 유명 학자의 호언장담 중 '완벽히 빗나간 예측(흑역사)' 또는 
    '현재 치열하게 논쟁 중인 진행형 발언' 1개를 찾아 아래 JSON 형식으로만 출력하세요.
    (기존에 유명한 폴 크루그먼 팩스 발언, 일론 머스크 로보택시, 팀 쿡 비전프로, 스티브 발머 아이폰 조롱 외의 새롭고 신선한 사례를 발굴할 것)

    출력 형식 (JSON 객체 1개):
    {
      "cardType": "TRACK 또는 ONGOING 또는 LESSON",
      "eraTag": {"ko": "연도 · 핵심키워드", "en": "Year · Keyword"},
      "statusBadge": {"ko": "예측 빗나감 ✕ 또는 진행중 ⏳", "en": "Result verdict"},
      "statusColor": "결과에 따라 bg-rose-500/10 text-rose-400 border-rose-500/20 또는 bg-slate-500/10 등",
      "author": {"ko": "이름", "en": "Name"},
      "authorTitle": {"ko": "직책", "en": "Title"},
      "avatar": "관련 이모지 1개",
      "imageBeforeUrl": "관련된 고화질 무료 이미지 URL (Unsplash 등)",
      "imageCaption": {"ko": "이미지 설명", "en": "Caption"},
      "title": {"ko": "발언 핵심 1줄", "en": "Quote in 1 line"},
      "quoteSource": {"ko": "출처(예: 2021년 인터뷰)", "en": "Source"},
      "quoteText": {"ko": "실제 발언 내용", "en": "Original quote"},
      "timelineLabel": {"ko": "📊 N년 뒤 결과", "en": "📊 N Years Later"},
      "realityStat": {"ko": "결과 요약", "en": "Outcome short"},
      "realityText": {"ko": "실제 벌어진 일 팩트체크", "en": "Fact check detail"},
      "actionHighlight": {"ko": "이 사례에서 얻을 수 있는 통찰/행동 지침", "en": "Insight"},
      "upvotes": 100,
      "disagrees": 20
    }
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            text = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"^```\s*", "", text)
            text = re.sub(r"\s*```$", "", text).strip()
            
            return json.loads(text)
    except Exception as e:
        print(f"[ERROR] Gemini API Error: {e}")
        return None

def main():
    html_path = "named/raw.html"
    if not os.path.exists(html_path):
        print(f"[ERROR] {html_path} not found.")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_item = fetch_new_named_item()
    if not new_item:
        print("[FAIL] No new item generated.")
        sys.exit(1)

    # 파싱 에러 방지용 랜덤 ID 생성
    new_item['id'] = f"p_auto_{int(time.time())}"
    new_item_str = json.dumps(new_item, ensure_ascii=False, indent=6)

    # JSON 파싱 없이 정규식으로 직접 외과적 끼워넣기
    # const POSTS = [...] 배열의 마지막 } 뒤에 새 객체를 이어붙임
    match = re.search(r'(const POSTS = \[.*?\})(\s*\];)', content, flags=re.DOTALL)
    if not match:
        print("[ERROR] POSTS array closing not found.")
        sys.exit(1)

    new_content = content[:match.end(1)] + ",\n" + new_item_str + match.group(2)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("[SUCCESS] Appended 1 new record via Regex bypass.")

if __name__ == "__main__":
    main()
