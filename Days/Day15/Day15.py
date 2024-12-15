import enum
from pathlib import Path
from typing import Sequence

import Util


class Tile(enum.Enum):
    empty = "."
    box = "O"
    wall = "#"
    robot = "@"

class Direction(enum.Enum):
    up = 0
    down = 1
    left = 2
    right = 3

OFFSETS:list[tuple[int,int]] = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
]

WIDE_TILES:dict[Tile,tuple[Tile,Tile]] = {
    Tile.empty: (Tile.empty, Tile.empty),
    Tile.box: (Tile.box, Tile.empty), # The WideWarehouse considers only the left tile to be containing a box.
    Tile.wall: (Tile.wall, Tile.empty), # The WideWarehouse considers only the left tile to be containing a wall.
}

DIRECTION_CHARACTERS:dict[str,Direction] = {"^": Direction.up, "v": Direction.down, "<": Direction.left, ">": Direction.right}
DIRECTION_CHARACTERS_REVERSE:Sequence[str] = "^v<>"

class Warehouse():

    def __init__(self, tiles:list[list[Tile]], robot_location:tuple[int,int], instructions:list[Direction], size:tuple[int,int]) -> None:
        self.tiles = tiles
        self.robot_location = robot_location
        self.instructions = instructions
        self.size = size

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def stringify(self) -> str: ...

    def print(self) -> None:
        print(self.stringify())

    def __getitem__(self, position:tuple[int,int]) -> Tile:
        return self.tiles[position[1]][position[0]]

    def __setitem__(self, position:tuple[int,int], tile:Tile) -> None:
        self.tiles[position[1]][position[0]] = tile

    def get[T](self, position:tuple[int,int], default:T=None) -> Tile|T:
        x, y = position
        if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]:
            return self.tiles[y][x]
        else:
            return default

    def push(self, tile_position:tuple[int,int], offset:tuple[int,int]) -> bool: ...

    def move_robot(self, direction:Direction) -> None: ...

    def follow_instructions(self) -> None:
        for instruction in self.instructions:
            self.move_robot(instruction)

    def get_gps_coordinates(self) -> int:
        return sum(
            x + 100 * y
            for y, row in enumerate(self.tiles)
            for x, tile in enumerate(row)
            if tile is Tile.box
        )

class SkinnyWarehouse(Warehouse):

    def stringify(self) -> str:
        return "\n".join(
            "".join(
                "@" if (x, y) == self.robot_location
                else tile.value
                for x, tile in enumerate(row)
            ) for y, row in enumerate(self.tiles)
        )

    def push(self, tile_position:tuple[int,int], offset:tuple[int,int]) -> bool:
        start_x, start_y = tile_position
        x, y = tile_position
        dx, dy = offset
        while self[x, y] is Tile.box:
            x += dx
            y += dy
        if self[x, y] is Tile.empty:
            self[start_x, start_y], self[x, y] = self[x, y], self[start_x, start_y]
            # if box line is pushable, swap the empty tile at the end and the
            # first box in the line.
            return True
        else: return False

    def move_robot(self, direction: Direction) -> None:
        x, y = self.robot_location
        dx, dy = OFFSETS[direction.value]
        tile_x, tile_y = x + dx, y + dy
        if self.push((tile_x, tile_y), (dx, dy)):
            # If True, the box moved.
            self.robot_location = (tile_x, tile_y)

class WideWarehouse(Warehouse):

    def stringify(self) -> str:
        return "\n".join(
            "".join(
                "@" if (x, y) == self.robot_location
                else "[" if tile is Tile.box
                else "]" if self.get((x - 1, y)) is Tile.box
                else "#" if self.get((x - 1, y)) is Tile.wall
                else tile.value
                for x, tile in enumerate(row)
            ) for y, row in enumerate(self.tiles)
        )

    def push(self, tile_position: tuple[int, int], offset: tuple[int, int]) -> bool:
        if self[tile_position] is Tile.empty:
            return True
        dx, dy = offset
        visited_tiles:list[tuple[int,int]] = []
        visited_map:list[list[bool]] = [[False] * self.size[0] for y in range(self.size[1])]
        unexplored_tiles:list[tuple[int,int]] = [tile_position]
        # GRAPH THEORY; huzzah!

        while len(unexplored_tiles) > 0:
            x, y = unexplored_tiles.pop()
            if visited_map[y][x]:
                continue
            if self[x, y] is Tile.wall:
                return False
            # because it goes depth first it's going to find any walls in the way faster (probably)

            neighbor_tiles:list[tuple[int,int]]
            if dx == 0:
                neighbor_tiles = [
                    neighbor_position
                    for offset in range(-1, 2)
                    if self[neighbor_position := (x + offset, y + dy)] is not Tile.empty
                ]
            else:
                # The only tile that can affect this tile is the one at x + 2.
                # There cannot be a tile at x + 1.
                neighbor_position = (x + 2*dx, y)
                neighbor_tiles = [neighbor_position] if self[neighbor_position] is not Tile.empty else []

            unexplored_tiles.extend(neighbor_tiles)
            visited_tiles.append((x, y))
            visited_map[y][x] = True

        visited_tiles.reverse() # in a vertical line push, this will cause
        # tiles furthest away to be moved first. This prevents a situation in
        # which a tile attempts to swap itself with another tile.
        for (x, y) in visited_tiles:
            x2, y2 = x + dx, y + dy
            self[x, y], self[x2, y2] = self[x2, y2], self[x, y]
        return True

    def move_robot(self, direction: Direction) -> None:
        x, y = self.robot_location
        dx, dy = OFFSETS[direction.value]
        tile_x, tile_y = x + dx - 1, y + dy
        if self[tile_x, tile_y] is Tile.empty:
            tile_x += 1
        # (tile_x, tile_y) will be the Tile in direction that is not empty.
        # preference is given to the adjacent tile.
        if self.push((tile_x, tile_y), (dx, dy)):
            # If True, the box moved.
            self.robot_location = (x + dx, y + dy)

def parse_warehouse(file:Path) -> tuple[SkinnyWarehouse, WideWarehouse]:
    with open(file, "rt") as f:
        text = f.read()
    warehouse_text, instructions_text = text.split("\n\n", maxsplit=1)
    skinny_tiles:list[list[Tile]] = []
    wide_tiles:list[list[Tile]] = []
    tile_characters:dict[str,Tile] = {tile.value: tile for tile in Tile}
    skinny_robot_location:tuple[int,int]|None = None
    wide_robot_location:tuple[int,int]|None = None
    for y, warehouse_line in enumerate(warehouse_text.split("\n")):
        skinny_row:list[Tile] = []
        wide_row:list[Tile] = []
        for x, character in enumerate(warehouse_line):
            tile = tile_characters[character]
            if tile is Tile.robot:
                skinny_robot_location = (x, y)
                wide_robot_location = (x*2, y)
                tile = Tile.empty
            skinny_row.append(tile)
            wide_row.extend(WIDE_TILES[tile])
        skinny_tiles.append(skinny_row)
        wide_tiles.append(wide_row)
    if skinny_robot_location is None or wide_robot_location is None:
        raise RuntimeError("No robot detected!")
    instructions:list[Direction] = [
        DIRECTION_CHARACTERS[character]
        for character in instructions_text
        if character != "\n"
    ]
    skinny_size = (len(skinny_tiles[0]), len(skinny_tiles))
    wide_size = (len(wide_tiles[0]), len(wide_tiles))
    return SkinnyWarehouse(skinny_tiles, skinny_robot_location, instructions, skinny_size), WideWarehouse(wide_tiles, wide_robot_location, instructions, wide_size)

def main() -> None:
    skinny_warehouse, wide_warehouse = parse_warehouse(Util.get_input_path(15, "Input"))
    print("Part 1:")
    skinny_warehouse.follow_instructions()
    print(skinny_warehouse.get_gps_coordinates())
    print("Part 2:")
    wide_warehouse.follow_instructions()
    print(wide_warehouse.get_gps_coordinates())
