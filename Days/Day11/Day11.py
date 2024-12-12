from collections import Counter
from math import ceil, log10
from pathlib import Path

import Util


class Stones():

    def __init__(self, stones:list[int]) -> None:
        self.stones:Counter[int] = Counter(stones)

    def __len__(self) -> int:
        return len(self.stones)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self)}>"

    def stringify(self) -> str:
        return " ".join(str(stone) for stone in self.stones)

    def blink(self) -> Counter[int]:
        stones:Counter[int] = Counter()
        for stone, count in self.stones.items():
            if stone == 0:
                stones[1] += count
            elif (engraving_length := ceil(log10(stone + 1))) % 2 == 0:
                power = 10 ** (engraving_length // 2)
                left_stone, right_stone = divmod(stone, power)
                stones[left_stone] += count
                stones[right_stone] += count
            else:
                stones[2024 * stone] += count
        self.stones = stones
        return stones

    def blinks(self, amount:int) -> Counter[int]:
        for i in range(amount):
            self.blink()
        return self.stones

def parse_stones(file:Path) -> Stones:
    with open(file, "rt") as f:
        text = f.read()
    return Stones([int(stone) for stone in text.split(" ")])

def main() -> None:
    stones = parse_stones(Util.get_input_path(11, "Input"))
    print("Part 1:")
    print(sum(stones.blinks(25).values()))
    print("Part 2:")
    print(sum(stones.blinks(50).values())) # 50 more times = 75
