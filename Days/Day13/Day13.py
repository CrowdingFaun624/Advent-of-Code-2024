from pathlib import Path

import Util


class Machine():

    def __init__(self, a_behavior:tuple[int,int], b_behavior:tuple[int,int], prize_location:tuple[int,int]) -> None:
        self.a_behavior = a_behavior
        self.b_behavior = b_behavior
        self.prize_location = prize_location

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} prize at ({self.prize_location[0]}, {self.prize_location[1]})>"

    def stringify(self) -> str:
        return "\n".join([
            f"Button A: X+{self.a_behavior[0]}, Y+{self.a_behavior[1]}",
            f"Button B: X+{self.b_behavior[0]}, Y+{self.a_behavior[1]}",
            f"Prize: X={self.prize_location[0]}, Y={self.prize_location[1]}"
        ])

    def print(self) -> None:
        print(self.stringify())

    def minimum_tokens(self, offset:int) -> int|None:
        # Let ax, ay, bx, by, px, py, a, b be integers.
        # a*ax + b*bx = px
        # a*ay + b*by = py

        # a = (px - b*bx)/ax
        # a = (py - b*by)/ay
        # (px - b*bx)/ax = (py - b*by)/ay
        # ay * (px - b*bx) = ax * (py - b*by)
        # ay*px - b*ay*bx = ax*py - b*ax*by
        # b*ax*by - b*ay*bx = ax*py - ay*px
        # b*(ax*by - ay*bx) = ax*py - ay*px
        # b = (ax*py - ay*px) / (ax*by - ay*bx)

        # b = (px - a*ax)/bx
        # b = (py - a*ay)/by
        # (px - a*ax)/bx = (py - a*ay)/by
        # by*(px - a*ax) = bx*(py - a*ay)
        # by*px - a*by*ax = bx*py - a*bx*ay
        # a*bx*ay - a*by*ax = bx*py - by*px
        # a*(bx*ay - by*ax) = bx*py - by*px
        # a = (bx*py - by*px) / (bx*ay - by*ax)
        ax, ay = self.a_behavior
        bx, by = self.b_behavior
        px, py = self.prize_location
        px += offset
        py += offset
        a, mod_a = divmod(bx*py - by*px, bx*ay - by*ax)
        b, mod_b = divmod(ax*py - ay*px, ax*by - ay*bx)
        if mod_a == 0 and mod_b == 0:
            return 3*a + b
        else:
            return None

def parses_machines(file:Path) -> list[Machine]:
    with open(file, "rt") as f:
        text = f.read()
    machines:list[Machine] = []
    for machine_lines in text.split("\n\n"):
        button_a_line, button_b_line, prize_line = machine_lines.split("\n")
        ax, ay = (int(coordinate.split("+")[1]) for coordinate in button_a_line.split(","))
        bx, by = (int(coordinate.split("+")[1]) for coordinate in button_b_line.split(","))
        prize_x, prize_y = (int(coordinate.split("=")[1]) for coordinate in prize_line.split(","))
        machines.append(Machine((ax, ay), (bx, by), (prize_x, prize_y)))
    return machines

def main() -> None:
    machines = parses_machines(Util.get_input_path(13, "Input"))
    print("Part 1:")
    print(sum(minimum_tokens for machine in machines if (minimum_tokens := machine.minimum_tokens(offset=0)) is not None))
    print("Part 2:")
    print(sum(minimum_tokens for machine in machines if (minimum_tokens := machine.minimum_tokens(offset=10000000000000)) is not None))
