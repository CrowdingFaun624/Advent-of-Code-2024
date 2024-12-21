from itertools import product
from pathlib import Path

import Util
from Util import Grid

OFFSETS:list[tuple[int,int]] = [
    (0, -1), # up
    (0, 1), # down
    (-1, 0), # left
    (1, 0), # right
]

class Racetrack():

    def __init__(self, walls:Grid[bool], start:tuple[int,int], end:tuple[int,int]) -> None:
        self.walls = walls
        self.start = start
        self.end = end
        self.size = self.walls.size

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def _find_minimum_distance(self, unvisited_tiles:list[tuple[int,int]], distances:Grid[int]) -> tuple[tuple[int,int],int]:
        minimum_distance = self.size[0] * self.size[1]
        minimum_index:int|None = None
        for index, position in enumerate(unvisited_tiles):
            if distances[position] < minimum_distance:
                minimum_index = index
                minimum_distance = distances[position]
        assert minimum_index is not None
        return unvisited_tiles[minimum_index], minimum_index

    def get_distance_from_start(self) -> Grid[int]:
        max_distance = self.size[0] * self.size[1]
        distances:Grid[int] = Grid.new_filled(lambda: max_distance, self.size)
        distances[self.end] = 0
        visited_tiles:Grid[bool] = Grid.new_filled(lambda: False, self.size)
        unvisited_tiles:list[tuple[int,int]] = [self.end]
        unvisited_grid:Grid[bool] = Grid.new_filled(lambda: True, self.size)
        previous_tiles:Grid[tuple[int,int]|None] = Grid.new_filled(lambda: None, self.size)
        while len(unvisited_tiles) > 0:
            (x, y), unvisited_index = self._find_minimum_distance(unvisited_tiles, distances)
            unvisited_tiles.pop(unvisited_index)
            distance = distances[x, y]
            for neighbor_x, neighbor_y in (
                (x + dx, y + dy)
                for dx, dy in OFFSETS
                if self.walls.get((x + dx, y + dy)) is False
                if not visited_tiles[x + dx, y + dy]
            ):
                if unvisited_grid[neighbor_x, neighbor_y] and distance < distances[neighbor_x, neighbor_y]:
                    previous_tiles[neighbor_x, neighbor_y] = (x, y)
                    unvisited_tiles.append((neighbor_x, neighbor_y))
                    unvisited_grid[neighbor_x, neighbor_y] = False
                    distances[neighbor_x, neighbor_y] = distance + 1
            visited_tiles[x, y] = True
        return distances

    def _get_taxicab_pattern(self, size:int) -> list[tuple[int,int,int]]:
        return [
            (x, y, distance)
            for x, y in product(range(-size, size + 1), range(-size, size + 1))
            if (distance := abs(x) + abs(y)) <= size
            if abs(x) > 1 or abs(y) > 1 # Immediate surroundings cannot be
            # jumped to.
        ]

    def get_awesome_cheats(self, distances:Grid[int], save_threshold:int, cheat_length:int) -> int:
        awesome_cheat_count = 0
        taxicab_pattern = self._get_taxicab_pattern(cheat_length)
        for x1, y1 in product(range(self.size[0]), range(self.size[1])):
            if self.walls[x1, y1]: continue
            for dx, dy, distance in taxicab_pattern:
                x2, y2 = x1 + dx, y1 + dy
                if self.walls.get((x2, y2)) is not False:
                    continue
                time_saved = distances[x1, y1] - distances[x2, y2] - distance
                if time_saved >= save_threshold:
                    awesome_cheat_count += 1
        return awesome_cheat_count

def parse_racetrack(file:Path) -> Racetrack:
    with open(file, "rt") as f:
        lines:list[str] = f.readlines()
    size = (len(lines[0]) - 1, len(lines))
    walls:Grid[bool] = Grid.new_filled(lambda: False, size)
    start_position:tuple[int,int]|None = None
    end_position:tuple[int,int]|None = None
    for y, line in enumerate(lines):
        for x, character in enumerate(line.rstrip()):
            match character:
                case "S":
                    start_position = (x, y)
                case "E":
                    end_position = (x, y)
                case "#":
                    walls[x, y] = True
    assert start_position is not None and end_position is not None
    return Racetrack(walls, start_position, end_position)

def main() -> None:
    racetrack = parse_racetrack(Util.get_input_path(20, "Input"))
    print("Part 1:")
    distances = racetrack.get_distance_from_start()
    print(racetrack.get_awesome_cheats(distances, 100, 2))
    print("Part 2:")
    print(racetrack.get_awesome_cheats(distances, 100, 20))
