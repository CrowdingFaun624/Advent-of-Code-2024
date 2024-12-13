import enum
from itertools import product
from pathlib import Path

import Util

PLOTS = dict(zip(*[list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")]*2)) # allows plots to be compared using `is`.

class Visitedness(enum.Enum):
    unvisited = 0
    planned = 1
    visited = 2

class Direction(enum.Enum):
    right = 0
    left = 1
    down = 2
    up = 3

OFFSETS = [
    (Direction.right, 1, 0), # right
    (Direction.left, -1, 0), # left
    (Direction.down, 0, 1), # down
    (Direction.up, 0, -1), # up
]

class Garden():

    def __init__(self, plots:list[list[str]], size:tuple[int,int]) -> None:
        self.plots = plots
        self.size = size

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def stringify(self) -> str:
        return "\n".join("".join(row) for row in self.plots)

    def print(self) -> None:
        print(self.stringify())

    def __getitem__(self, position:tuple[int,int]) -> str:
        return self.plots[position[1]][position[0]]

    def get[T](self, position:tuple[int,int], default:T=None) -> str|T:
        x, y = position
        if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]:
            return self.plots[y][x]
        else:
            return default

    def explore_region(self, start_pos:tuple[int,int], visited_plots:list[list[Visitedness]]) -> tuple[list[tuple[int,int]], int, int]:
        '''
        Returns all internal area plots of the region and the perimeter of the region.
        '''
        start_plot = self[start_pos]
        unvisited_plots:list[tuple[int,int]] = [start_pos]
        region_area:list[tuple[int,int]] = []
        region_perimeter = 0
        sides:tuple[list[list[int]],...] = tuple([[] for j in range(self.size[i > 1] + 1)] for i in range(4))
        # right, left, down, up

        while len(unvisited_plots) > 0:
            current_x, current_y = unvisited_plots.pop()
            visited_plots[current_y][current_x] = Visitedness.visited
            neighbor_plots:list[tuple[bool,Direction,tuple[int,int]]] = [
                ((adjacent_plot := self.get(adjacent_position := (current_x + dx, current_y + dy))) is not None and adjacent_plot is start_plot, direction, adjacent_position)
                for direction, dx, dy in OFFSETS
            ]
            for is_in_region, direction, (neighbor_x, neighbor_y) in neighbor_plots:
                if is_in_region:
                    if visited_plots[neighbor_y][neighbor_x] is Visitedness.unvisited:
                        unvisited_plots.append((neighbor_x, neighbor_y))
                        visited_plots[neighbor_y][neighbor_x] = Visitedness.planned
                else:
                    region_perimeter += 1
                    sides[direction.value][neighbor_x + (direction.value % 2) if direction.value < 2 else neighbor_y + (direction.value % 2)].append(neighbor_y if direction.value < 2 else neighbor_x)
            region_area.append((current_x, current_y))

        side_count:int = 0
        for direction_sides in sides:
            for position_sides in direction_sides:
                position_sides.sort()
                if len(position_sides) == 0: continue
                next_expected_side:int|None = None
                for side in position_sides:
                    if side != next_expected_side:
                        side_count += 1
                    next_expected_side = side + 1

        return region_area, region_perimeter, side_count

    def calculate_regions(self) -> list[tuple[int,int,int]]:
        visited_plots:list[list[Visitedness]] = [[Visitedness.unvisited] * self.size[0] for i in range(self.size[1])]
        regions:list[tuple[int,int,int]] = []
        for x, y in product(range(self.size[0]), range(self.size[1])):
            if visited_plots[y][x] is Visitedness.visited:
                continue
            region, perimeter, side_count = self.explore_region((x, y), visited_plots)
            regions.append((len(region), perimeter, side_count))
        return regions

def parse_garden(file:Path) -> Garden:
    with open(file, "rt") as f:
        lines = f.readlines()
    size = (len(lines[0])-1, len(lines))
    return Garden([
        [
            PLOTS[character]
            for character in line.rstrip()
        ]
        for line in lines
    ], size)

def main() -> None:
    garden = parse_garden(Util.get_input_path(12, "Input"))
    print("Part 1:")
    pricing_info = garden.calculate_regions()
    print(sum(map(lambda item: item[0] * item[1], pricing_info)))
    print("Part 2:")
    print(sum(map(lambda item: item[0] * item[2], pricing_info)))
