"""
[사용법] python scripts/check_debate_pool.py
scripts/debate_pool.json 과 debate/posts.json 전체를 훑어서
imageBeforeUrl 중복 및 pool 개수를 확인합니다.
"""
import os
import json
import sys
from collections import defaultdict

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_path = os.path.join(base_dir, "debate", "posts.json")
    pool_path = os.path.join(base_dir, "scripts", "debate_pool.json")

    with open(posts_path, "r", encoding="utf-8") as f:
        posts = json.load(f)["posts"]
    with open(pool_path, "r", encoding="utf-8") as f:
        pool = json.load(f)

    url_to_items = defaultdict(list)

    for p in posts:
        label = f"[posts.json] {p.get('id', '?')} - {p.get('title', {}).get('ko', '')[:20]}"
        url_to_items[p.get("imageBeforeUrl")].append(label)

    for p in pool:
        label = f"[pool] {p.get('title', {}).get('ko', '')[:20]}"
        url_to_items[p.get("imageBeforeUrl")].append(label)

    dupes_found = False
    for url, items in url_to_items.items():
        if len(items) > 1:
            dupes_found = True
            print(f"\n[DUPLICATE] {url}")
            for item in items:
                print(f"   - {item}")

    print(f"\n[INFO] debate/posts.json 게시글 수: {len(posts)}개")
    print(f"[INFO] scripts/debate_pool.json 남은 글감 수: {len(pool)}개")
    if len(pool) <= 3:
        print(f"[WARN] pool이 {len(pool)}개 남았습니다. 채워주세요.")

    if not dupes_found:
        print("\n[OK] 중복된 imageBeforeUrl이 없습니다.")
        sys.exit(0)
    else:
        print("\n[FAIL] 위 항목들의 이미지를 서로 다른 것으로 교체해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
