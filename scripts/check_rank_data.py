"""
[사용법] python scripts/check_rank_data.py
rank/posts.json의 구조(플랫폼별 5개씩 총 25개)와
lastUpdated 신선도를 확인합니다.
named/justice/debate와 달리 rank는 '매일 통째로 갱신되는 스냅샷'이라
pool 개수가 아니라 '최근에 실제로 갱신됐는지'를 체크하는 게 핵심입니다.
"""
import os
import json
import sys
import datetime
from datetime import timezone, timedelta

PLATFORM_ORDER = ["YOUTUBE", "TIKTOK", "THREADS", "INSTA", "X"]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_path = os.path.join(base_dir, "rank", "posts.json")

    if not os.path.exists(posts_path):
        print(f"[ERROR] File not found: {posts_path}")
        sys.exit(1)

    with open(posts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ranks = data.get("ranks", [])
    problems = []

    # 1. 구조 체크: 플랫폼별 정확히 5개씩, 총 25개
    if len(ranks) != 25:
        problems.append(f"전체 항목 수가 25개가 아님 (현재 {len(ranks)}개)")

    for plat in PLATFORM_ORDER:
        count = len([r for r in ranks if r.get("platform") == plat])
        if count != 5:
            problems.append(f"{plat} 항목 수가 5개가 아님 (현재 {count}개)")

    # 2. overallRank 중복/누락 체크
    overall_ranks = sorted([r.get("overallRank") for r in ranks])
    if overall_ranks != list(range(1, len(ranks) + 1)):
        problems.append(f"overallRank가 1~{len(ranks)} 연속이 아님: {overall_ranks}")

    # 3. 신선도 체크: lastUpdated가 48시간 이내인지
    last_updated_str = data.get("lastUpdated", "")
    try:
        kst = timezone(timedelta(hours=9))
        last_updated = datetime.datetime.strptime(last_updated_str, "%Y.%m.%d %H:%M").replace(tzinfo=kst)
        now = datetime.datetime.now(kst)
        age_hours = (now - last_updated).total_seconds() / 3600
        print(f"[INFO] lastUpdated: {last_updated_str} ({age_hours:.1f}시간 전)")
        if age_hours > 48:
            problems.append(f"lastUpdated가 {age_hours:.1f}시간 전 — 최근 갱신이 안 되고 있을 가능성. Actions 로그에서 API 키/오류 확인 필요")
    except ValueError:
        problems.append(f"lastUpdated 형식을 읽을 수 없음: '{last_updated_str}'")

    if problems:
        print("\n[FAIL]")
        for p in problems:
            print(f"   - {p}")
        sys.exit(1)
    else:
        print("[OK] 구조와 신선도 모두 정상입니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
