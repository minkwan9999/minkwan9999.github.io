"""
[사용법] python interleave_named_pool.py
scripts/named_pool.json을 열어서 cardType(LESSON/TRACK/ONGOING)이
연속으로 몰리지 않게 라운드로빈으로 섞은 뒤 같은 파일에 다시 저장합니다.
각 타입 내부의 순서(먼저 넣은 것 먼저 나옴)는 그대로 유지됩니다.
"""
import json
import sys
from collections import defaultdict

def main():
    path = "scripts/named_pool.json"
    with open(path, "r", encoding="utf-8") as f:
        pool = json.load(f)

    groups = defaultdict(list)
    order = []
    for item in pool:
        ct = item.get("cardType", "LESSON")
        if ct not in groups:
            order.append(ct)
        groups[ct].append(item)

    print("[INFO] 재정렬 전 타입별 개수:")
    for ct in order:
        print(f"   - {ct}: {len(groups[ct])}개")

    interleaved = []
    while any(groups[ct] for ct in order):
        for ct in order:
            if groups[ct]:
                interleaved.append(groups[ct].pop(0))

    with open(path, "w", encoding="utf-8") as f:
        json.dump(interleaved, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] {len(interleaved)}개 항목을 인터리빙하여 저장했습니다.")
    print("[INFO] 재정렬 후 앞 10개 타입 순서:", [i.get("cardType") for i in interleaved[:10]])

if __name__ == "__main__":
    main()
