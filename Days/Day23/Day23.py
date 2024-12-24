from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Iterator

import Util


def get_all_connections(connections:list[tuple[str,str]]) -> defaultdict[str,set[str]]:
    output:defaultdict[str,set[str]] = defaultdict(lambda: set())
    for computer1, computer2 in connections:
        output[computer1].add(computer2)
        output[computer2].add(computer1)
    return output

def get_triads(all_connections:dict[str,set[str]]) -> Iterator[tuple[str,str,str]]:
    already_connections:set[frozenset[str]] = set()
    for computer, connections in all_connections.items():
        for computer2, computer3 in combinations(connections, 2):
            if computer2 not in all_connections[computer3]:
                continue
            triad = (computer, computer2, computer3)
            triad_set = frozenset(triad)
            if triad_set in already_connections:
                continue
            already_connections.add(triad_set)
            yield triad

def get_largest_party_at(all_connections:dict[str,set[str]], computer:str, connected_computers:set[str], depth:int, maximum_depth:int, cache:set[frozenset[str]]) -> tuple[str,...]|None:
    if depth == maximum_depth:
        return tuple(connected_computers)
    for connection in all_connections[computer]:
        if connection in connected_computers:
            continue
        if len(connected_computers - all_connections[connection]) > 0:
            # if there are any computers already in the group that this new
            # computer is not connected to.
            continue
        connected_computers.add(connection)
        computer_party_frozenset = frozenset(connected_computers)
        if computer_party_frozenset not in cache:
            computer_largest_party = get_largest_party_at(all_connections, connection, connected_computers, depth + 1, maximum_depth, cache)
            if computer_largest_party is not None:
                return computer_largest_party
        cache.add(computer_party_frozenset)
        connected_computers.remove(connection)
    return None

def get_largest_party(all_connections:dict[str,set[str]]) -> tuple[str,...]:
    maximum_connections = len(next(iter(all_connections.values())))
    for computer in all_connections:
        computer_largest_party = get_largest_party_at(all_connections, computer, {computer}, 0, maximum_connections - 1, set())
        if computer_largest_party is not None:
            return computer_largest_party
    else:
        raise RuntimeError("No group detected :(")

def construct_graph(all_connections:dict[str,set[str]]) -> None:
    # https://csacademy.com/app/graph_editor/ is cool
    output:list[str] = []
    sorted_connections:dict[str,list[str]] = {key: sorted(value) for key, value in sorted(all_connections.items())}
    output.extend(sorted_connections.keys())
    output.extend(f"{key} {connection}" for key, connections in sorted_connections.items() for connection in connections)
    print("\n".join(output))

def parse_connections(file:Path) -> list[tuple[str,str]]:
    with open(file, "rt") as f:
        return [tuple(line.rstrip().split("-")) for line in f.readlines()] # type: ignore

def main() -> None:
    connections = parse_connections(Util.get_input_path(23, "Input"))
    print("Part 1:")
    all_connections:defaultdict[str,set[str]] = get_all_connections(connections)
    print(sum(1 for triad in get_triads(all_connections) if any(computer.startswith("t") for computer in triad)))
    print("Part 2:")
    print(",".join(sorted(get_largest_party(all_connections))))
