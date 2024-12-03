from functools import reduce
from itertools import pairwise
from pathlib import Path

import Util

SAFE_RANGE = range(1, 4)

def parse_reports(file:Path) -> list[tuple[int,...]]:
    with open(file, "rt") as f:
        return [tuple(int(level) for level in report.split(" ")) for report in f.readlines()]

def is_safe(report:tuple[int,...]) -> bool:
    is_increasing:bool|None = None
    for previous_level, next_level in pairwise(report):
        if is_increasing is None:
            is_increasing = next_level > previous_level
        elif (next_level > previous_level) != is_increasing:
            return False
        if abs(next_level - previous_level) not in SAFE_RANGE:
            return False
    else:
        return True

def is_safe2(report:tuple[int,...]) -> bool: # evil but works
    return any(is_safe(tuple(list(report[:exclude_index]) + list(report[exclude_index + 1:]))) for exclude_index in range(len(report)))

def main() -> None:
    print("Part 1:")
    reports = parse_reports(Util.get_input_path(2, "Input"))
    print(reduce(lambda x, y: x + y, (is_safe(report) for report in reports)))
    print("Part 2:")
    print(reduce(lambda x, y: x + y, (is_safe2(report) for report in reports)))
