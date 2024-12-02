from collections import Counter
from pathlib import Path

import Util


def parse_input(file:Path) -> tuple[list[int],list[int]]:
    list1:list[int] = []
    list2:list[int] = []
    with open(file, "rt") as f:
        for line in f.readlines():
            item1, item2 = line.split("   ")
            list1.append(int(item1))
            list2.append(int(item2))
    return list1, list2

def main() -> None:
    print("Part 1:")
    left_list, right_list = parse_input(Util.get_input_path(1, "Input"))
    print(sum(abs(left-right) for left, right in zip(sorted(left_list), sorted(right_list), strict=True)))
    print("Part 2:")
    right_counter = Counter(right_list)
    print(sum(item * right_counter[item] for item in left_list))

if __name__ == "__main__":
    main()
