import enum
from itertools import product
from pathlib import Path

import Util


class Tile(enum.Enum):
    wall = "#"
    empty = "."

class Direction(enum.Enum):
    north = 0
    south = 1
    west = 2
    east = 3

OFFSETS = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0)
]

LEFTS = [
    Direction.west,
    Direction.east,
    Direction.south,
    Direction.north,
]

RIGHTS = [
    Direction.east,
    Direction.west,
    Direction.north,
    Direction.south,
]

class Maze():

    def __init__(self, grid:list[list[Tile]], size:tuple[int,int], start:tuple[int,int], end:tuple[int,int]) -> None:
        self.grid:list[list[Tile]] = grid
        self.size:tuple[int,int] = size
        self.start:tuple[int,int] = start
        self.end:tuple[int,int] = end

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def stringify(self, highlight_set:list[list[bool]]) -> str:
        return "\n".join(
            "".join(
                tile.value if not highlight_set[y][x] else "$"
                for x, tile in enumerate(row)
            )
            for y, row in enumerate(self.grid)
        )

    def print(self, highlight_set:list[list[bool]], other_stuff:str|None=None) -> None:
        output = self.stringify(highlight_set)
        with open(Util.get_path(16, "Output.txt"), "at") as f:
            if other_stuff is not None:
                f.write(other_stuff + "\n")
            f.write(output + "\n")
        print(output)

    def __getitem__(self, position:tuple[int,int]) -> Tile:
        return self.grid[position[1]][position[0]]

    def get[T](self, position:tuple[int,int], default:T=None) -> Tile|T:
        x, y = position
        if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]:
            return self.grid[y][x]
        else:
            return default

    def in_direction(self, x:int, y:int, direction:Direction) -> tuple[int,int]:
        dx, dy = OFFSETS[direction.value]
        return x + dx, y + dy

    def compete(self) -> tuple[int,int]:
        start = (self.start[0], self.start[1], Direction.east)
        unvisited_tiles:list[tuple[int,int,Direction]] = [start]
        visited_set:list[list[list[bool]]] = [[[False] * self.size[0] for i in range(self.size[1])] for i in range(4)]
        maximum_score = 1000 * self.size[0] * self.size[1] + 1 # probably can't get higher than this lol.
        minimum_scores:list[list[list[int]]] = [[[maximum_score] * self.size[0] for i in range(self.size[1])] for i in range(4)]
        minimum_scores[start[2].value][start[1]][start[0]] = 0
        end_x, end_y = self.end
        path:list[list[list[list[tuple[int, int, Direction, int]]]]] = [[[[] for i in range(self.size[0])] for i in range(self.size[1])] for i in range(4)]
        while len(unvisited_tiles) > 0 and not all(visited_set[end_y][end_x][direction] for direction in range(4)):

            minimum_score = maximum_score
            minimum_index:int|None = None
            for i, (unvisited_x, unvisited_y, unvisited_direction) in enumerate(reversed(unvisited_tiles)):
                if (this_score := minimum_scores[unvisited_direction.value][unvisited_y][unvisited_x]) < minimum_score:
                    minimum_index = -1 - i # because reversed
                    minimum_score = this_score
            assert minimum_index is not None
            x, y, direction = unvisited_tiles.pop(minimum_index)

            score = minimum_scores[direction.value][y][x]
            neighbors:list[tuple[tuple[int,int,Direction],int]] = []
            # rotation neighbors
            if self.in_direction(x, y, left := LEFTS[direction.value]) not in (None, Tile.wall):
                neighbors.append(((x, y, left), score + 1000))
            if self.in_direction(x, y, right := RIGHTS[direction.value]) not in (None, Tile.wall):
                neighbors.append(((x, y, right), score + 1000))
            # movement neighbor
            if self.get(neighbor_position := self.in_direction(x, y, direction)) not in (None, Tile.wall):
                neighbors.append(((neighbor_position[0], neighbor_position[1], direction), score + 1))

            for (neighbor_x, neighbor_y, neighbor_direction), neighbor_score in neighbors:
                if visited_set[neighbor_direction.value][neighbor_y][neighbor_x]:
                    continue
                minimum_score = minimum_scores[neighbor_direction.value][neighbor_y][neighbor_x]
                if neighbor_score < minimum_score:
                    minimum_scores[neighbor_direction.value][neighbor_y][neighbor_x] = neighbor_score
                    unvisited_tiles.append((neighbor_x, neighbor_y, neighbor_direction))
                    path[neighbor_direction.value][neighbor_y][neighbor_x] = [(x, y, direction, neighbor_score)]
                elif neighbor_score == minimum_score:
                    path[neighbor_direction.value][neighbor_y][neighbor_x].append((x, y, direction, neighbor_score))
            visited_set[direction.value][y][x] = True

        assert not any(minimum_scores[direction.value][end_y][end_x] == 1000 for direction in Direction)
        minimum_direction, minimum_score = None, maximum_score
        for direction, score in zip(Direction, (minimum_scores[direction][end_y][end_x] for direction in range(4))):
            if score < minimum_score:
                minimum_score = score
                minimum_direction = direction
        assert minimum_direction is not None

        unvisited_tiles = [(end_x, end_y, minimum_direction)]
        visited_tiles_set:list[list[list[bool]]] = [[[False] * self.size[0] for i in range(self.size[1])] for i in range(4)]
        best_tiles_count = 1
        best_tiles_set:list[list[bool]] = [[False] * self.size[0] for i in range(self.size[1])]
        x, y, direction = end_x, end_y, minimum_direction
        while len(unvisited_tiles):
            x, y, direction = unvisited_tiles.pop()
            for neighbor_x, neighbor_y, neighbor_direction, _ in path[direction.value][y][x]:
                if not visited_tiles_set[neighbor_direction.value][neighbor_y][neighbor_x]:
                    unvisited_tiles.append((neighbor_x, neighbor_y, neighbor_direction))
                    visited_tiles_set[neighbor_direction.value][neighbor_y][neighbor_x] = True
                    if not best_tiles_set[neighbor_y][neighbor_x]:
                        best_tiles_count += 1
                        best_tiles_set[neighbor_y][neighbor_x] = True
        return minimum_score, best_tiles_count

def parse_maze(file:Path) -> Maze:
    with open(file, "rt") as f:
        lines = f.readlines()
    tile_characters = {tile.value: tile for tile in Tile}
    tiles:list[list[Tile]] = []
    start_position:tuple[int,int]|None = None
    end_position:tuple[int,int]|None = None
    for y, line in enumerate(lines):
        row:list[Tile] = []
        for x, character in enumerate(line.rstrip()):
            if character == "E":
                end_position = (x, y)
                character = "."
            elif character == "S":
                start_position = (x, y)
                character = "."
            row.append(tile_characters[character])
        tiles.append(row)
    assert start_position is not None and end_position is not None
    size = (len(tiles[0]), len(tiles))
    return Maze(tiles, size, start_position, end_position)

def main() -> None:
    with open(Util.get_path(16, "Output.txt"), "wt") as f:
        f.write("")
    maze = parse_maze(Util.get_input_path(16, "Input"))
    print("Part 1:")
    minimum_score, best_tiles =maze.compete()
    print(minimum_score)
    print("Part 2:")
    print(best_tiles)
