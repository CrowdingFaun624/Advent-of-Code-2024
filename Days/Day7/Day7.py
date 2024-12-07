from math import ceil, log10
from pathlib import Path

import Util


class Equation():

    def __init__(self, test_value:int, numbers:list[int]) -> None:
        self.test_value = test_value
        self.numbers = numbers

    def __len__(self) -> int:
        return len(self.numbers)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.test_value}: {" ".join(str(number) for number in self.numbers)}"

    def can_be_made_true(self, allow_concat:bool) -> bool:
        return self.try_value(self.test_value, len(self) - 1, allow_concat, self.numbers[0])

    def try_value(self, result:int, index:int, allow_concat:bool, goal:int) -> bool:
        if index == 0:
            return result == self.numbers[index]
        if result < goal:
            return False
        number = self.numbers[index]
        if allow_concat:
            power = 10**ceil(log10(number + 1))
            if result % power == number and self.try_value(result//power, index - 1, allow_concat, goal):
                return True
        quotient, remainder = divmod(result, number)
        if remainder == 0 and self.try_value(quotient, index - 1, allow_concat, goal):
            return True
        if self.try_value(result-number, index - 1, allow_concat, goal):
            return True
        return False

def parse_equations(file:Path) -> list[Equation]:
    with open(file, "rt") as f:
        text:list[str] = f.readlines()
    equations:list[Equation] = []
    for line in text:
        test_value_string, numbers_strings = line.split(": ")
        test_value = int(test_value_string)
        numbers = [int(number) for number in numbers_strings.rstrip().split(" ")]
        equations.append(Equation(test_value, numbers))
    return equations

def main() -> None:
    equations = parse_equations(Util.get_input_path(7, "Input"))
    print("Part 1:")
    print(sum(equation.test_value for equation in equations if equation.can_be_made_true(False)))
    print("Part 2:")
    print(sum(equation.test_value for equation in equations if equation.can_be_made_true(True)))
