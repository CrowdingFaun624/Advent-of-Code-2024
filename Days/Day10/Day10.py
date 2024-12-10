from collections import defaultdict
from itertools import product
from pathlib import Path

import Util

ADJACENT_POSITIONS = [
    (-1,  0), # left
    ( 1,  0), # right
    ( 0, -1), # up
    ( 0,  1), # down
]

class TopographicMap():

    def __init__(self, heights:list[list[int]], size:tuple[int,int]) -> None:
        self.heights = heights
        self.size = size

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def __getitem__(self, position:tuple[int,int]) -> int:
        x, y = position
        return self.heights[y][x]

    def get[a](self, x:int, y:int, default:a=None) -> int|a:
        return self.heights[y][x] if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1] else default

    def construct_graph(self) -> dict[tuple[int,int],list[tuple[int,int]]]:
        return {
            (x, y): [
                (adjacent_x, adjacent_y)
                for dx, dy in ADJACENT_POSITIONS
                if (adjacent_height := self.get(adjacent_x := x + dx, adjacent_y := y + dy)) is not None and adjacent_height == self[x, y] + 1
            ]
            for x, y in product(range(self.size[0]), range(self.size[1]))
        }

    def traverse_graph(self, start:tuple[int,int], graph:dict[tuple[int,int],list[tuple[int,int]]], output:dict[tuple[int,int],tuple[set[tuple[int,int]],int]]) -> tuple[set[tuple[int,int]],int]:
        # recursive function that finds all distinct and indistinct nines reachable from a point.
        distinct_nines_reachable:set[tuple[int,int]] = {start} if self[start] == 9 else set()
        indistinct_nines_reachable = int(self[start] == 9)
        for destination in graph[start]:
            if destination in output:
                destination_distinct, destination_indistinct = output[destination]
                distinct_nines_reachable.update(destination_distinct)
                indistinct_nines_reachable += destination_indistinct
            else:
                destination_distinct, destination_indistinct = self.traverse_graph(destination, graph, output)
                distinct_nines_reachable.update(destination_distinct)
                indistinct_nines_reachable += destination_indistinct
        output[start] = (distinct_nines_reachable, indistinct_nines_reachable)
        return distinct_nines_reachable, indistinct_nines_reachable

    def get_trailhead_scores_distinct(self, simple_graph:dict[tuple[int,int],list[tuple[int,int]]]) -> dict[tuple[int,int],tuple[int,int]]:
        trailheads:list[tuple[int,int]] = [(x, y) for y, x in product(range(self.size[1]), range(self.size[0])) if self[x, y] == 0]
        nines_reachable:dict[tuple[int,int],tuple[set[tuple[int,int]],int]] = {}
        for trailhead in trailheads:
            self.traverse_graph(trailhead, simple_graph, nines_reachable)
        return {trailhead: (len(nines_reachable[trailhead][0]), nines_reachable[trailhead][1]) for trailhead in trailheads}

def parse_map(file:Path) -> TopographicMap:
    with open(file, "rt") as f:
        lines = f.readlines()
    map:list[list[int]] = [ [ int(character) for character in line.rstrip() ] for line in lines ]
    size = (len(lines[0]) - 1, len(lines))
    return TopographicMap(map, size)

def main() -> None:
    import time
    t1 = time.time()
    topographic_map = parse_map(Util.get_input_path(10, "Input"))
    graph = topographic_map.construct_graph()
    scores = topographic_map.get_trailhead_scores_distinct(graph)
    t2 = time.time()
    print(t2 - t1)
    print("Part 1:")
    print(sum(score[0] for score in scores.values()))
    print("Part 2:")
    print(sum(score[1] for score in scores.values()))
    
