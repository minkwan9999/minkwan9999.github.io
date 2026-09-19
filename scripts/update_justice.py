# [Version 1.0] - named 앱과 동일한 posts.json 직접 조작 방식.
import os
import json
import time
import sys
import datetime
from datetime import timezone, timedelta

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_path = os.path.join(base_dir, "justice", "posts.json")
    pool_path = os.path.join(base_dir, "scripts", "justice_pool.json")

    for p in (posts_path, pool_path):
        if not os.path.exists(p):
            print(f"[ERROR] File not found: {p}")
            sys.exit(1)

    with open(pool_path, "r", encoding="utf-8") as f:
        pool = json.load(f)

    if not pool:
        print("[WARN] 글감 풀이 비었습니다. 오늘은 추가하지 않고 정상 종료합니다.")
        print("[WARN] scripts/justice_pool.json에 새 사건을 채워주세요.")
        sys.exit(0)

    kst = timezone(timedelta(hours=9))
    now_kst = datetime.datetime.now(kst)

    picked = pool.pop(0)
    picked["id"] = f"j_auto_{int(time.time())}"
    picked["addedAt"] = now_kst.strftime("%Y-%m-%d")
    remaining = len(pool)

    print(f"[INFO] 이번에 사용한 사건: {picked['title']['ko']}")
    print(f"[INFO] 남은 글감 풀 개수: {remaining}개")
    if remaining <= 3:
        print(f"[WARN] 글감 풀이 {remaining}개밖에 안 남았습니다. 곧 채워주세요.")

    with open(posts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["posts"].append(picked)

    data["lastUpdated"] = now_kst.strftime("%Y.%m.%d %H:%M")

    with open(posts_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Appended new post to justice/posts.json. Total posts: {len(data['posts'])}")

    with open(pool_path, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Pool updated. {remaining} items remaining.")

if __name__ == "__main__":
    main()
