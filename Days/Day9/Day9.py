from itertools import starmap, takewhile
from pathlib import Path
from typing import Callable, Iterator

import Util


class DiskMap():

    def __init__(self, space:list[int|None]|None=None) -> None:
        self.space:list[int|None] = [] if space is None else space

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self)}>"

    def __len__(self) -> int:
        return len(self.space)

    def copy(self) -> "DiskMap":
        return DiskMap(self.space.copy())

    def stringify(self) -> str:
        return "".join(str(id_number % 10) if id_number is not None else "." for id_number in self.space)

    def allocate(self, id_number:int|None, amount:int) -> None:
        self.space.extend([id_number] * amount)

    def move_blocks(self) -> None:
        empty_blocks = (block for block in range(0, len(self)) if self.space[block] is None)
        file_blocks = (block for block in range(len(self)-1, -1, -1) if self.space[block] is not None)
        for empty_block, file_block in takewhile(lambda item: item[1] > item[0], zip(empty_blocks, file_blocks)):
            self.space[empty_block], self.space[file_block] = self.space[file_block], self.space[empty_block]

    def get_free_space(self, required_length:int) -> Iterator[int]:
        '''
        Returns positions with `required_length` free space.
        '''
        for block in range(required_length, len(self)):
            window = self.space[block-required_length:block]
            if all(item is None for item in window):
                yield block - required_length

    def get_files(self) -> Iterator[tuple[int,int,int]]:
        '''
        Returns the id number, length, and starting position of all files in reversed order.
        '''
        current_id:int|None = None
        length = 0
        for block in range(len(self)-1, -1, -1):
            if self.space[block] is current_id:
                length += 1
            elif current_id is not None:
                # the next higher block is the start of a file.
                yield current_id, length, block + 1
                current_id = self.space[block]
                length = 1
            else:
                current_id = self.space[block]
                # current_id is now None
                length = 1
        if current_id is not None and length > 0:
            yield current_id, length, 0

    def move_blocks_defragmented(self) -> None:
        self.free_spaces = [self.get_free_space(length) for length in range(1, 10)]
        for id_number, length, start_block in self.get_files():
            try:
                free_block = next(self.free_spaces[length-1])
            except StopIteration:
                # cannot move file if no space is available.
                continue
            if free_block > start_block:
                # cannot move file if no space is to the left.
                continue
            for new_block, old_block in zip(range(free_block, free_block+length), range(start_block, start_block+length), strict=True):
                self.space[new_block], self.space[old_block] = self.space[old_block], self.space[new_block]

    def get_checksum(self) -> int:
        func:Callable[[tuple[int,int|None]],bool] = lambda item: item[1] is not None # for some reason doesn't allow this to be in-line.
        return sum(starmap(lambda block, id_number: block * id_number, filter(func, enumerate(self.space))))

def parse_disk_map(file:Path) -> DiskMap:
    with open(file, "rt") as f:
        text = f.read()
    disk_map = DiskMap()
    for i, character in enumerate(text):
        id_number = i // 2 if i % 2 == 0 else None
        amount = int(character)
        disk_map.allocate(id_number, amount)
    return disk_map

def main() -> None:
    disk_map = parse_disk_map(Util.get_input_path(9, "Input"))
    print("Part 1:")
    disk_map2 = disk_map.copy() # probably faster to copy than to reparse.
    disk_map2.move_blocks()
    print(disk_map2.get_checksum())
    print("Part 2:")
    disk_map.move_blocks_defragmented()
    print(disk_map.get_checksum())
