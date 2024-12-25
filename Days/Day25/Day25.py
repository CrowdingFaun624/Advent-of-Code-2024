from itertools import product
from pathlib import Path

import Util


def parse_keys_and_locks(file:Path) -> tuple[list[tuple[int,...]], list[tuple[int,...]]]:
    with open(file, "rt") as f:
        schematics = f.read().split("\n\n")
    keys: list[tuple[int,...]] = []
    locks:list[tuple[int,...]] = []
    for schematic in schematics:
        lines = schematic.split("\n")
        is_lock = schematic[0] == "#"
        heights = tuple(sum(1 for y in range(7) if lines[y][x] == "#") - 1 for x in range(5))
        (locks if is_lock else keys).append(heights)
    return keys, locks

def main() -> None:
    keys, locks = parse_keys_and_locks(Util.get_input_path(25, "Input"))
    print("Part 1:")
    print(sum(1 for lock, key in product(locks, keys) if all(lock_pin + key_pin <= 5 for lock_pin, key_pin in zip(lock, key, strict=True))))
