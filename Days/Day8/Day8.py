from collections import defaultdict
from itertools import combinations, count
from pathlib import Path
from typing import Callable, Iterable

import Util


def point_in_bounds(point:tuple[int,int], size:tuple[int,int]) -> bool:
    x, y = point
    sx, sy = size
    return x >= 0 and x < sx and y >= 0 and y < sy

class Map():

    def __init__(self, antennas:dict[str,list[tuple[int,int]]], size:tuple[int,int]) -> None:
        self.antennas = antennas
        self.size = size

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"
    
    def get_antinodes(self, antinode_range:Callable[[],Iterable[int]]) -> set[tuple[int,int]]:
        antinodes:set[tuple[int,int]] = set()
        for frequency, antennas in self.antennas.items():
            for (x1, y1), (x2, y2) in combinations(antennas, 2):
                rise = y2 - y1
                run  = x2 - x1
                for offset in antinode_range():
                    antinode = (x1 - run * offset, y1 - rise * offset)
                    if not point_in_bounds(antinode, self.size):
                        break
                    antinodes.add(antinode)
                for offset in antinode_range():
                    antinode = (x2 + run * offset, y2 + rise * offset)
                    if not point_in_bounds(antinode, self.size):
                        break
                    antinodes.add(antinode)
        return antinodes

def parse_map(file:Path) -> Map:
    with open(file, "rt") as f:
        lines = f.readlines()
    antennas:defaultdict[str,list[tuple[int,int]]] = defaultdict(lambda: [])
    for y, line in enumerate(lines):
        for x, character in enumerate(line.rstrip()):
            if character == ".": continue
            antennas[character].append((x, y))
    size = (len(lines[0]) - 1, len(lines))
    # -1 because of newlines
    return Map(antennas, size)

def main() -> None:
    map = parse_map(Util.get_input_path(8, "Input"))
    print("Part 1:")
    print(len(map.get_antinodes(lambda: [1])))
    print("Part 2:")
    print(len(map.get_antinodes(lambda: count(0))))
