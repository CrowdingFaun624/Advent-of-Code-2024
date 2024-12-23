from collections import Counter
from itertools import pairwise
from pathlib import Path
from typing import Iterator

import Util


def get_window[T](iterable:list[T]) -> Iterator[tuple[tuple[T,T,T,T],int]]:
    for i in range(0, len(iterable)-3):
        yield tuple(iterable[i:i+4]), i + 3 # type: ignore

def get_next_secret_number(secret_number:int) -> int:
    secret_number = (secret_number ^ (secret_number << 6 )) % 16777216
    secret_number = (secret_number ^ (secret_number >> 5 )) % 16777216
    return (secret_number ^ (secret_number << 11)) % 16777216

def repeat_secret_number(initial_secret_number:int, repeat:int) -> list[int]:
    output:list[int] = [initial_secret_number]
    secret_number = initial_secret_number
    for i in range(repeat):
        secret_number = get_next_secret_number(secret_number)
        output.append(secret_number)
    return output

def parse_secret_numbers(file:Path) -> list[int]:
    with open(file, "rt") as f:
        return [int(line.rstrip()) for line in f.readlines()]

def monkey_pricing(monkey_prices:list[int], prices:Counter[tuple[int,int,int,int]]) -> None:
    deltas = [p2 - p1 for p1, p2 in pairwise(monkey_prices)]
    already_windows:set[tuple[int,int,int,int]] = set()
    for window, index in get_window(deltas):
        if window in already_windows: continue
        prices[window] += monkey_prices[index + 1]
        already_windows.add(window)

def part2(monkeys_secrets:list[list[int]]) -> int:
    prices:Counter[tuple[int,int,int,int]] = Counter()
    for monkey_secrets in monkeys_secrets:
        monkey_pricing([monkey_secret % 10 for monkey_secret in monkey_secrets], prices)
    return max(prices.values())

def main() -> None:
    monkeys_initials = parse_secret_numbers(Util.get_input_path(22, "Input"))
    print("Part 1:")
    monkeys_secrets = [repeat_secret_number(initial_secret_number, 2000) for initial_secret_number in monkeys_initials]
    print(sum(secret_number[-1] for secret_number in monkeys_secrets))
    print("Part 2:")
    print(part2(monkeys_secrets))
