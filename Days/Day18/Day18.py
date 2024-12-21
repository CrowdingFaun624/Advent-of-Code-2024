from pathlib import Path

import Util
from Util import Grid

OFFSETS:list[tuple[int,int]] = [
    (0, -1), # up
    (0, 1), # down
    (-1, 0), # left
    (1, 0), # right
]

class MemorySpace():

    def __init__(self, size:int, byte_positions:list[tuple[int,int]]) -> None:
        self.size = size
        self.byte_positions = byte_positions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size {self.size} len {len(self.byte_positions)}>"

    def simulate(self, count:int) -> Grid[bool]:
        output:Grid[bool] = Grid.new_filled(lambda: False, (self.size + 1, self.size + 1))
        for byte_x, byte_y in self.byte_positions[:count]:
            output[byte_x, byte_y] = True
        return output

    def _find_minimum_distance(self, unvisited_tiles:list[tuple[int,int]], distances:Grid[int]) -> tuple[tuple[int,int],int]:
        minimum_distance = self.size ** 2
        minimum_index:int|None = None
        for index, position in enumerate(unvisited_tiles):
            if distances[position] < minimum_distance:
                minimum_index = index
                minimum_distance = distances[position]
        assert minimum_index is not None
        return unvisited_tiles[minimum_index], minimum_index

    def _get_path(self, previous_tiles:Grid[tuple[int,int]|None], start:tuple[int,int]) -> Grid[bool]:
        output:Grid[bool] = Grid.new_filled(lambda: False, (self.size + 1, self.size + 1))
        position:tuple[int,int]|None = start
        while position is not None:
            output[position] = True
            position = previous_tiles[position]
        return output

    def pathfind(self, obstacles:Grid[bool]) -> tuple[bool, int, Grid[bool]]:
        max_distance:int = self.size ** 2
        distances:Grid[int] = Grid.new_filled(lambda: max_distance, (self.size + 1, self.size + 1))
        distances[0, 0] = 0
        visited_tiles:Grid[bool] = Grid.new_filled(lambda: False, (self.size + 1, self.size + 1))
        unvisited_tiles:list[tuple[int,int]] = [(0, 0)]
        unvisited_grid:Grid[bool] = Grid.new_filled(lambda: True, (self.size + 1, self.size + 1))
        previous_tiles:Grid[tuple[int,int]|None] = Grid.new_filled(lambda: None, (self.size + 1, self.size + 1))
        while distances[self.size, self.size] == max_distance and len(unvisited_tiles) > 0:
            (x, y), unvisited_index = self._find_minimum_distance(unvisited_tiles, distances)
            unvisited_tiles.pop(unvisited_index)
            distance = distances[x, y]
            for neighbor_x, neighbor_y in (
                (x + dx, y + dy)
                for dx, dy in OFFSETS
                if obstacles.get((x + dx, y + dy)) is False
                if not visited_tiles[x + dx, y + dy]
            ):
                if unvisited_grid[neighbor_x, neighbor_y] and distance < distances[neighbor_x, neighbor_y]:
                    previous_tiles[neighbor_x, neighbor_y] = (x, y)
                    unvisited_tiles.append((neighbor_x, neighbor_y))
                    unvisited_grid[neighbor_x, neighbor_y] = False
                    distances[neighbor_x, neighbor_y] = distance + 1
            visited_tiles[x, y] = True
        if distances[self.size, self.size] == max_distance:
            return False, 0, Grid.new_filled(lambda: False, (self.size + 1, self.size + 1))
        else:
            return True, distances[self.size, self.size], self._get_path(previous_tiles, start=(self.size, self.size))

    def get_cutoff_byte(self, first_simulation_count:int, path:Grid[bool]) -> tuple[int,int]:
        obstacles = self.simulate(first_simulation_count)
        for byte_x, byte_y in self.byte_positions[first_simulation_count:]:
            obstacles[byte_x, byte_y] = True
            if path[byte_x, byte_y]:
                has_path, _, new_path = self.pathfind(obstacles)
                if not has_path:
                    return byte_x, byte_y
                path = new_path
            else:
                continue
        else:
            raise RuntimeError("No byte blocks the path!")

def parse_memory_space(file:Path) -> MemorySpace:
    with open(file, "rt") as f:
        lines:list[str] = f.readlines()
    size = int(lines[0].rstrip().split(":")[1]) # line with format "Size:70" is
    # prepended to file.
    byte_positions:list[tuple[int,int]] = []
    for line in lines[1:]:
        x, y = line.rstrip().split(",")
        byte_positions.append((int(x), int(y)))
    return MemorySpace(size, byte_positions)

def main() -> None:
    memory_space = parse_memory_space(Util.get_input_path(18, "Input"))
    print("Part 1:")
    simulation_count = 1024
    _, path_length, path = memory_space.pathfind(memory_space.simulate(count=simulation_count))
    print(path_length)
    print("Part 2:")
    print(",".join(str(coordinate) for coordinate in memory_space.get_cutoff_byte(simulation_count, path)))
