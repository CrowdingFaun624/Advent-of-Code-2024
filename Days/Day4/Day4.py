from itertools import chain, product
from pathlib import Path

import Util


def get_diagonals[T](matrix:list[list[T]]) -> tuple[list[T],list[T]]:
    '''
    Returns each diagonal of a square matrix.
    '''
    size = len(matrix)
    return [matrix[i][i] for i in range(size)], [matrix[size-i-1][i] for i in range(size)]

class WordSearch():
    
    def __init__(self, characters:str) -> None:
        '''
        :characters: A string containing characters from "XMAS\\n" and no ending newline.
        '''
        self.rows:list[str] = characters.split("\n")
        self.size:tuple[int,int] = (len(self.rows[0]), len(self.rows))
        self.columns:list[str] = ["".join(self.rows[y][x] for y in range(self.size[1])) for x in range(self.size[0])]
        self.diagonals1:list[str] = [
            "".join(
                self.rows[y][x]
                for x, y in zip(
                    range(max(0, start_x), min(start_x + self.size[1], self.size[0])),
                    range(max(0, -start_x), min(self.size[1], self.size[0]-start_x)),
                    strict=True
                )
            ) for start_x in range(-self.size[1]+1, self.size[0])
        ]
        self.diagonals2:list[str] = [
            "".join(
                self.rows[y][self.size[0]-x-1]
                for x, y in zip(
                    range(max(0, start_x), min(start_x + self.size[1], self.size[0])),
                    range(max(0, -start_x), min(self.size[1], self.size[0]-start_x)),
                    strict=True
                )
            ) for start_x in range(-self.size[1]+1, self.size[0])
        ]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def stringify(self) -> str:
        return "\n".join("".join(character for character in row) for row in self.rows)

    def print(self) -> None:
        print(self.stringify())

    def collections(self) -> list[list[str]]:
        return [self.rows, self.columns, self.diagonals1, self.diagonals2]

    def search(self, text:str) -> int:
        reversed_text = text[::-1]
        return sum(
            1
            for line in chain.from_iterable(self.collections())
            for offset in range(len(line)-len(text)+1)
            if line[offset:offset+len(text)] in (text, reversed_text)
        )

    def get_window(self, start_x:int, start_y:int, width:int, height:int) -> list[list[str]]:
        return [
            [
                self.rows[y][x]
                for x in range(start_x, start_x+width)
            ]
            for y in range(start_y, start_y+height)
        ]

    def search_x(self, text:str) -> int:
        reversed_text:str = text[::-1]
        return sum(
            1
            for x, y in product(range(0, self.size[0]-len(text)+1), range(0, self.size[1]-len(text)+1))
            if all(
                "".join(diagonal) in (text, reversed_text)
                for diagonal in get_diagonals(self.get_window(x, y, len(text), len(text)))
            )
        )

def parse_search(file:Path) -> WordSearch:
    with open(file, "rt") as f:
        text = f.read()
        assert not text.endswith("\n")
        return WordSearch(text)

def main() -> None:
    word_search = parse_search(Util.get_input_path(4, "Input"))
    print("Part 1:")
    print(word_search.search("XMAS"))
    print("Part 2:")
    print(word_search.search_x("MAS"))
