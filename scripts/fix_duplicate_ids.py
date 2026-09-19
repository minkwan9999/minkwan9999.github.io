"""
[사용법] python scripts/fix_duplicate_ids.py named   (또는 justice, debate)
해당 앱의 posts.json을 열어서 중복된 id를 찾아 뒤에 나온 항목의 id 뒤에
_2, _3 ... 접미사를 붙여 고유하게 만들어 저장합니다.
"""
import json
import sys
from collections import defaultdict

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("named", "justice", "debate"):
        print("사용법: python scripts/fix_duplicate_ids.py [named|justice|debate]")
        sys.exit(1)

    app = sys.argv[1]
    path = f"{app}/posts.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    posts = data["posts"]
    seen = defaultdict(int)
    fixed_count = 0

    for post in posts:
        pid = post.get("id")
        if pid is None:
            continue
        seen[pid] += 1
        if seen[pid] > 1:
            new_id = f"{pid}_{seen[pid]}"
            print(f"[FIX] {pid} -> {new_id}  ({post.get('title', {}).get('ko', post.get('target', {}).get('ko', ''))[:30]})")
            post["id"] = new_id
            fixed_count += 1

    if fixed_count == 0:
        print("[OK] 중복된 id가 없습니다. 수정할 것이 없어요.")
        return

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] {fixed_count}개 항목의 id를 고유하게 수정했습니다.")

if __name__ == "__main__":
    main()
