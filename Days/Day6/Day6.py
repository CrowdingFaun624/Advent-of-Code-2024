import enum
from collections import defaultdict
from itertools import count, product, takewhile
from pathlib import Path
from typing import Iterator

import Util


class Direction(enum.Enum):
    up = "^"
    right = ">"
    down = "v"
    left = "<"

# maps (if it's an obstacle, if it's traversed) with its character
TILE_STRINGS:dict[tuple[bool,bool],str] = {
    (False, False): ".",
    (True,  False): "#",
    (False, True ): "X",
    (True,  True ): "?",
}

TILE_OFFSETS:tuple[tuple[int,int,Direction],...] = (
    (1, 0, Direction.up),
    (0, 1, Direction.right),
    (-1, 0, Direction.down),
    (0, -1, Direction.left),
)

DIRECTION_OFFSETS:dict[Direction,tuple[int,int]] = {
    Direction.up: (0, -1),
    Direction.right: (1, 0),
    Direction.down: (0, 1),
    Direction.left: (-1, 0),
}

RIGHT_DIRECTION:dict[Direction,Direction] = {
    Direction.up: Direction.right,
    Direction.right: Direction.down,
    Direction.down: Direction.left,
    Direction.left: Direction.up,
}

def point_in_bounds(position:tuple[int,int], size:tuple[int,int]) -> bool:
    x, y = position
    return x >= 0 and x < size[0] and y >= 0 and y < size[1]

class Guard():

    def __init__(self, position:tuple[int,int], direction:Direction) -> None:
        self.position = position
        self.direction = direction

    def node(self) -> tuple[int,int,Direction]:
        return self.position[0], self.position[1], self.direction

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.direction.name} at {self.position[0]}, {self.position[1]}>"

    def __str__(self) -> str:
        return self.direction.value

    def in_front_of_position(self) -> tuple[int,int]:
        '''
        Returns the position immediately in front of the guard.
        '''
        x, y = self.position
        dx, dy = DIRECTION_OFFSETS[self.direction]
        return x + dx, y + dy

    def advance(self) -> tuple[int,int]:
        '''
        Moves the guard to the position in front of her; returns the new position.
        '''
        position = self.in_front_of_position()
        self.position = position
        return position

    def turn_right(self) -> Direction:
        '''
        Turns the guard right, returning her new direction.
        '''
        output = RIGHT_DIRECTION[self.direction]
        self.direction = output
        return output

class Edge():

    start:tuple[int,int,Direction]

    def __iter__(self) -> Iterator[tuple[int,int]]: ...

    def insert_obstacle(self, position:tuple[int, int]) -> "FiniteEdge":
        obstacle_x, obstacle_y = position
        dx, dy = DIRECTION_OFFSETS[self.start[2]]
        end_x, end_y = obstacle_x - dx, obstacle_y - dy
        end_direction = RIGHT_DIRECTION[self.start[2]]
        return FiniteEdge(self.start, (end_x, end_y, end_direction))

class FiniteEdge(Edge):

    def __init__(self, start:tuple[int,int,Direction], end:tuple[int,int,Direction]) -> None:
        self.start:tuple[int,int,Direction] = start
        self.end:tuple[int,int,Direction] = end

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.start} → {self.end}>"

    def __iter__(self) -> Iterator[tuple[int,int]]:
        if self.start[0] == self.end[0]:
            x = self.start[0]
            yield from ((x, y) for y in range(min(self.start[1], self.end[1]), max(self.start[1], self.end[1])+1))
        else:
            y = self.start[1]
            yield from ((x, y) for x in range(min(self.start[0], self.end[0]), max(self.start[0], self.end[0])+1))

class InfiniteEdge(Edge):

    def __init__(self, start:tuple[int,int,Direction]) -> None:
        self.start = start

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.start} → ∞ >"

    def __iter__(self) -> Iterator[tuple[int,int]]:
        x, y, direction = self.start
        match direction:
            case Direction.up: yield from ((x, y - i) for i in count())
            case Direction.right: yield from ((x + i, y) for i in count())
            case Direction.down: yield from ((x, y + i) for i in count())
            case Direction.left: yield from ((x - i, y) for i in count())

class Map():

    def __init__(self, guard:Guard, size:tuple[int,int], obstacle_positions:list[tuple[int,int]], edges:dict[tuple[int,int,Direction],Edge], relevant_edges:dict[tuple[int,int],list[Edge]]) -> None:
        self.guard = guard
        self.size = size
        self.obstacle_positions:list[tuple[int,int]] = obstacle_positions
        self.edges:dict[tuple[int,int,Direction],Edge] = edges
        self.relevant_edges = relevant_edges

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def stringify(self, traversed_positions: set[tuple[int, int]] | None = None) -> str:
        if traversed_positions is None: traversed_positions = set()
        return "\n".join(
            "".join(
                str(self.guard) if (x, y) == self.guard.position else TILE_STRINGS[(x, y) in self.obstacle_positions, (x, y) in traversed_positions]
                for x in range(self.size[0])
            ) for y in range(self.size[1])
        )

    def print(self, traversed_positions:set[tuple[int,int]]|None=None) -> None:
        print(self.stringify(traversed_positions))

    def traverse(self, ignore_visited_tiles:bool) -> tuple[set[tuple[int,int]], bool]:
        '''
        Returns the set of visited positions and if a loop was entered.
        '''
        visited_nodes:set[tuple[int,int,Direction]] = set()
        visited_tiles:set[tuple[int,int]] = set()
        node = self.guard.node()
        while True:
            if node in visited_nodes:
                return visited_tiles, True
            visited_nodes.add(node)
            edge = self.edges[node]
            if isinstance(edge, FiniteEdge):
                if not ignore_visited_tiles:
                    visited_tiles.update(edge)
                node = edge.end
            elif isinstance(edge, InfiniteEdge):
                if not ignore_visited_tiles:
                    visited_tiles.update(takewhile(lambda position: point_in_bounds(position, self.size), edge))
                return visited_tiles, False

    def get_loop_causing_obstacles(self, traversed_positions:set[tuple[int,int]]) -> list[tuple[int,int]]:
        loop_causing_obstacles:list[tuple[int,int]] = []
        for new_obstacle in traversed_positions:
            new_map = insert_obstacle(self, new_obstacle)
            _, looped = new_map.traverse(True)
            if looped:
                loop_causing_obstacles.append(new_obstacle)
        return loop_causing_obstacles

def traverse_grid(obstacle_set:set[tuple[int,int]], size:tuple[int,int], start_x:int, start_y:int, start_direction:Direction) -> Edge:
    guard = Guard((start_x, start_y), start_direction)
    while True:
        if guard.in_front_of_position() in obstacle_set:
            end_x, end_y = guard.position
            end_direction = guard.turn_right()
            return FiniteEdge((start_x, start_y, start_direction), (end_x, end_y, end_direction))
        elif not point_in_bounds(guard.position, size):
            return InfiniteEdge((start_x, start_y, start_direction))
        else:
            guard.advance()

def construct_initial_map(obstacle_positions:list[tuple[int,int]], guard:Guard, size:tuple[int,int]) -> Map:
    obstacle_set:set[tuple[int,int]] = set(obstacle_positions)
    edges:dict[tuple[int,int,Direction],Edge] = {
        (obstacle_x + dx, obstacle_y + dy, start_direction): traverse_grid(obstacle_set, size, obstacle_x + dx, obstacle_y + dy, start_direction)
        for (obstacle_x, obstacle_y), (dx, dy, start_direction) in product(obstacle_positions, TILE_OFFSETS)
        if point_in_bounds((obstacle_x + dx, obstacle_y + dy), size)
    }
    guard_x, guard_y = guard.position
    edges[guard.node()] = traverse_grid(obstacle_set, size, guard_x, guard_y, guard.direction)
    relevant_edges:dict[tuple[int,int],list[Edge]] = defaultdict(lambda: [])
    for edge in edges.values():
        for position in takewhile(lambda position: point_in_bounds(position, size), edge):
            relevant_edges[position].append(edge)
    return Map(guard, size, obstacle_positions, edges, relevant_edges)

def insert_obstacle(initial_map:Map, new_obstacle_position:tuple[int,int]) -> Map:
    # relevant_edges does not need to be updated, since it's only used in creating new obstacles.
    new_obstacle_positions:list[tuple[int,int]] = initial_map.obstacle_positions.copy()
    new_obstacle_positions.append(new_obstacle_position)
    new_edges:dict[tuple[int,int,Direction],Edge] = initial_map.edges.copy()
    for relevant_edge in initial_map.relevant_edges[new_obstacle_position]:
        # An edge's start should always be its key in edges, so it should be overwritten.
        new_edges[relevant_edge.start] = relevant_edge.insert_obstacle(new_obstacle_position)
    obstacle_x, obstacle_y = new_obstacle_position
    obstacle_set:set[tuple[int,int]] = set(new_obstacle_positions)
    for dx, dy, start_direction in TILE_OFFSETS:
        if point_in_bounds((obstacle_x + dx, obstacle_y + dy), initial_map.size):
            new_edges[obstacle_x + dx, obstacle_y + dy, start_direction] = traverse_grid(obstacle_set, initial_map.size, obstacle_x + dx, obstacle_y + dy, start_direction)
    return Map(initial_map.guard, initial_map.size, new_obstacle_positions, new_edges, initial_map.relevant_edges)

def parse_map(file:Path) -> Map:
    with open(file, "rt") as f:
        map_rows_text = f.read().splitlines() # stupid readlines won't remove the ends.
    size = (len(map_rows_text[0]), len(map_rows_text))
    direction_characters = {direction.value: direction for direction in Direction}
    guard:Guard|None = None
    obstacle_positions:list[tuple[int,int]] = []
    for y, row_text in enumerate(map_rows_text):
        for x, char in enumerate(row_text):
            if char in direction_characters:
                assert guard is None
                guard = Guard((x, y), direction_characters[char])
            elif char == "#":
                obstacle_positions.append((x, y))
    assert guard is not None
    return construct_initial_map(obstacle_positions, guard, size)

def main() -> None:
    map = parse_map(Util.get_input_path(6, "Input"))
    print("Part 1:")
    traversed_points, _ = map.traverse(False)
    print(len(traversed_points))
    print("Part 2:")
    print(len(map.get_loop_causing_obstacles(traversed_points)))
