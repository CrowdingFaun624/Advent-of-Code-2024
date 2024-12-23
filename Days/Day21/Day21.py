from itertools import pairwise, product
from pathlib import Path

import Util
from Util import Grid


class Keypad():

    def __init__(self, buttons:str, start:tuple[int,int]) -> None:
        rows = buttons.split("\n")
        self.buttons = Grid([list(row) for row in rows], (len(rows[0]), len(rows)))
        self.size = self.buttons.size
        self.positions:dict[str,tuple[int,int]] = {button: (x, y) for x, y in product(range(self.size[0]), range(self.size[1])) if (button := self.buttons[x, y]) != " "}
        self.paths:dict[tuple[str,str],list[str]] = self._calculate_efficient_paths()
        self.start_button = self.buttons[start]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def _calculate_efficient_paths(self) -> dict[tuple[str,str],list[str]]:
        output:dict[tuple[str,str],list[str]] = {}
        for (button1, (x1, y1)), (button2, (x2, y2)) in product(self.positions.items(), self.positions.items()):
            dx, dy = x2 - x1, y2 - y1
            sequence:list[str] = []
            if   dx == 0 and dy == 0:
                sequence.append("A")
            elif dx == 0 and dy >  0:
                sequence.append("v" * dy + "A")
            elif dx == 0 and dy <  0:
                sequence.append("^" * -dy + "A")
            elif dx >  0 and dy == 0:
                sequence.append(">" * dx + "A")
            elif dx >  0 and dy >  0:
                if self.buttons[x2, y1] != " ":
                    sequence.append(">" * dx + "v" * dy + "A")
                if self.buttons[x1, y2] != " ":
                    sequence.append("v" * dy + ">" * dx + "A")
            elif dx >  0 and dy <  0:
                if self.buttons[x2, y1] != " ":
                    sequence.append(">" * dx + "^" * -dy + "A")
                if self.buttons[x1, y2] != " ":
                    sequence.append("^" * -dy + ">" * dx + "A")
            elif dx <  0 and dy == 0:
                sequence.append("<" * -dx + "A")
            elif dx <  0 and dy >  0:
                if self.buttons[x2, y1] != " ":
                    sequence.append("<" * -dx + "v" * dy + "A")
                if self.buttons[x1, y2] != " ":
                    sequence.append("v" * dy + "<" * -dx + "A")
            elif dx <  0 and dy <  0:
                if self.buttons[x1, y2] != " ":
                    sequence.append("^" * -dy + "<" * -dx + "A")
                if self.buttons[x2, y1] != " ":
                    sequence.append("<" * -dx + "^" * -dy + "A")
            else: raise RuntimeError("wow yes logic failure whoopsies.") # appease linter
            output[button1, button2] = sequence
        return output

    def encode(self, code:str, keypads:list["Keypad"], keypad_offset:int, cache:dict[tuple[str,int],int]) -> int:
        if (result := cache.get((code, keypad_offset))) is not None:
            return result
        if keypad_offset >= len(keypads):
            minimum_total_length = sum(len(self.paths[button1, button2][0]) for button1, button2 in pairwise("A" + code))
        else:
            next_keypad = keypads[keypad_offset]
            minimum_total_length = 0
            for button1, button2 in pairwise("A" + code):
                minimum_length = 1 << 64
                for path in self.paths[button1, button2]:
                    if (encoding_length := next_keypad.encode(path, keypads, keypad_offset+1, cache)) < minimum_length:
                        minimum_length = encoding_length
                assert minimum_length < 1 << 64
                minimum_total_length += minimum_length
        cache[code, keypad_offset] = minimum_total_length
        return minimum_total_length

def get_minimum_sequence_length(keypads:list[Keypad], numeric_code:str) -> int:
    return keypads[0].encode(numeric_code, keypads, 1, {})

def parse_codes(file:Path) -> list[str]:
    with open(file, "rt") as f:
        return f.read().split("\n")

def main() -> None:
    codes = parse_codes(Util.get_input_path(21, "Input"))
    numeric_keypad = Keypad("789\n456\n123\n 0A", (2, 3))
    directional_keypad = Keypad(" ^A\n<v>", (2, 0))
    assert get_minimum_sequence_length([numeric_keypad], "029A") == 12
    assert get_minimum_sequence_length([numeric_keypad, directional_keypad], "029A") == 28
    assert get_minimum_sequence_length([numeric_keypad, directional_keypad, directional_keypad], "029A") == 68
    assert get_minimum_sequence_length([numeric_keypad, directional_keypad, directional_keypad], "980A") == 60
    assert get_minimum_sequence_length([numeric_keypad, directional_keypad, directional_keypad], "179A") == 68
    assert get_minimum_sequence_length([numeric_keypad, directional_keypad, directional_keypad], "456A") == 64
    assert get_minimum_sequence_length([numeric_keypad, directional_keypad, directional_keypad], "379A") == 64
    print("Part 1:")
    print(sum(int(code[:-1]) * get_minimum_sequence_length([numeric_keypad, directional_keypad, directional_keypad], code) for code in codes))
    print("Part 2:")
    print(sum(int(code[:-1]) * get_minimum_sequence_length([numeric_keypad] + [directional_keypad] * 25, code) for code in codes))
