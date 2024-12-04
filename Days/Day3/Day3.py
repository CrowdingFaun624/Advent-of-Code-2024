from pathlib import Path
from typing import Callable

import Util

NoneType = type(None)

class DataReader():

    def __init__(self, memory:str) -> None:
        self.memory:str = memory
        self.position:int = 0

    def __repr__(self) -> str:
        return f"<DataReader at {self.position}>"

    def __len__(self) -> int:
        return len(self.memory)

    def peek(self, amount:int=1) -> str:
        return self.memory[self.position:self.position + amount]

    def read(self, amount:int=1) -> str:
        output:str = self.memory[self.position:self.position + amount]
        self.position += amount
        return output

    def back(self, amount:int) -> None:
        self.position -= amount

    def advance(self, amount:int) -> None:
        self.position += amount

    def __bool__(self) -> bool:
        return self.position < len(self.memory)

    def read_while(self, func:Callable[[str,int],bool]) -> str:
        '''
        Reads while the func(character, index_from_start) is True.
        '''
        index:int = 0
        output:list[str] = []
        while self:
            character = self.read()
            if func(character, index):
                output.append(character)
            else:
                break
            index += 1
        return "".join(output)

    def startswith(self, text:str) -> bool:
        '''
        If position has the text, advances and returns True;
        otherwise stay put and return False.
        '''
        if self.position + len(text) <= len(self.memory) and self.peek(len(text)) == text:
            self.advance(len(text))
            return True
        else:
            return False

    def reset(self) -> None:
        self.position = 0

class Instruction():

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

class MulInstruction(Instruction):

    def __init__(self, left:int, right:int) -> None:
        self.left:int = left
        self.right:int = right

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.left}, {self.right}>"

    def do(self) -> int:
        return self.left * self.right

class EnableInstruction(Instruction):
    ...

class DisableInstruction(Instruction):
    ...

def get_file(file:Path) -> DataReader:
    with open(file, "rt") as f:
        return DataReader(f.read())

def scan_for_mul(memory:DataReader) -> Instruction|None:
    if memory.startswith("do()"):
        return EnableInstruction()
    elif memory.startswith("don't()"):
        return DisableInstruction()
    start = memory.read_while(lambda character, index: index < 4 and "mul("[index] == character)
    if start != "mul(":
        return
    memory.back(1)
    num1 = memory.read_while(lambda character, index: character.isdigit())
    if len(num1) == 0:
        return
    memory.back(1)
    comma = memory.read_while(lambda character, index: character == ",")
    if comma != ",":
        return
    memory.back(1)
    num2 = memory.read_while(lambda character, index: character.isdigit())
    if len(num2) == 0:
        return
    memory.back(1)
    last = memory.read_while(lambda character, index: index < 1 and character == ")")
    if last != ")":
        return
    memory.back(1)
    return MulInstruction(int(num1), int(num2))

def scan1(memory:DataReader, consider_conditionals:bool) -> list[MulInstruction]:
    instructions:list[MulInstruction] = []
    enabled = True
    while memory:
        instruction = scan_for_mul(memory)
        match instruction:
            case NoneType():
                continue
            case MulInstruction():
                if enabled or not consider_conditionals:
                    instructions.append(instruction)
            case EnableInstruction():
                enabled = True
            case DisableInstruction():
                enabled = False
            case _:
                raise ValueError(f"Invalid Instruction {instruction}!")
    memory.reset()
    return instructions

def main() -> None:
    path = Util.get_input_path(3, "Input")
    memory = get_file(path)
    print("Part 1:")
    print(sum(instruction.do() for instruction in scan1(memory, False)))
    print("Part 2:")
    print(sum(instruction.do() for instruction in scan1(memory, True)))
