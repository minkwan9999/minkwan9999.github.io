# [Version 1.0] - named/justice 앱과 동일한 posts.json 직접 조작 방식.
import os
import json
import time
import sys
import datetime
from datetime import timezone, timedelta

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_path = os.path.join(base_dir, "debate", "posts.json")
    pool_path = os.path.join(base_dir, "scripts", "debate_pool.json")

    for p in (posts_path, pool_path):
        if not os.path.exists(p):
            print(f"[ERROR] File not found: {p}")
            sys.exit(1)

    with open(pool_path, "r", encoding="utf-8") as f:
        pool = json.load(f)

    if not pool:
        print("[WARN] 글감 풀이 비었습니다. 오늘은 추가하지 않고 정상 종료합니다.")
        print("[WARN] scripts/debate_pool.json에 새 논쟁을 채워주세요.")
        sys.exit(0)

    picked = pool.pop(0)
    picked["id"] = f"d_auto_{int(time.time())}"
    remaining = len(pool)

    print(f"[INFO] 이번에 사용한 논쟁: {picked['title']['ko']}")
    print(f"[INFO] 남은 글감 풀 개수: {remaining}개")
    if remaining <= 3:
        print(f"[WARN] 글감 풀이 {remaining}개밖에 안 남았습니다. 곧 채워주세요.")

    with open(posts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["posts"].append(picked)

    kst = timezone(timedelta(hours=9))
    data["lastUpdated"] = datetime.datetime.now(kst).strftime("%Y.%m.%d %H:%M")

    with open(posts_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Appended new post to debate/posts.json. Total posts: {len(data['posts'])}")

    with open(pool_path, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Pool updated. {remaining} items remaining.")

if __name__ == "__main__":
    main()
