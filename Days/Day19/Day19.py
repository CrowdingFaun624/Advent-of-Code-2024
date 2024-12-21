from pathlib import Path

import Util


class Onsen():
    
    def __init__(self, towels:list[str], designs:list[str]) -> None:
        self.towels = towels
        self.designs = designs
        self.towels.sort(key=lambda towel: len(towel))
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.towels)} towels, {len(self.designs)} designs>"

    def design_is_possible(self, design:str, cache:dict[str,bool]) -> bool:
        if (result := cache.get(design)) is not None:
            # empty string is assumed to be included within cache.
            return result
        for pattern in self.towels:
            if design[:len(pattern)] == pattern and self.design_is_possible(design[len(pattern):], cache):
                cache[design] = True
                return True
        else:
            cache[design] = False
            return False
    
    def get_design_combinations(self, design:str, cache:dict[str,int]) -> int:
        if (result := cache.get(design)) is not None:
            # empty string is assumed to be 1.
            return result
        total = 0
        for pattern in self.towels:
            if design[:len(pattern)] == pattern:
                total += self.get_design_combinations(design[len(pattern):], cache)
        cache[design] = total
        return total
    
    def count_possible_designs(self) -> int:
        cache:dict[str,bool] = {"": True}
        return sum(self.design_is_possible(design, cache) for design in self.designs)

    def count_design_combinations(self) -> int:
        cache:dict[str,int] = {"": 1}
        return sum(self.get_design_combinations(design, cache) for design in self.designs)

def parse_onsen(file:Path) -> Onsen:
    with open(file, "rt") as f:
        lines = f.readlines()
    towels:list[str] = [pattern for pattern in lines[0].rstrip().split(", ")]
    designs:list[str] = [design.rstrip() for design in lines[2:]]
    return Onsen(towels, designs)

def main() -> None:
    onsen = parse_onsen(Util.get_input_path(19, "Input"))
    print("Part 1:")
    print(onsen.count_possible_designs())
    print("Part 2:")
    print(onsen.count_design_combinations())
