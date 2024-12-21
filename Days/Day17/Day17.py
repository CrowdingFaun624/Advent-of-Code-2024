from itertools import pairwise, permutations, product
from pathlib import Path
from typing import Optional, cast, overload

import Util


def bool_list_to_int(bool_list:list[bool]) -> int:
    '''
    Converts the list of bools to a little-endian int.
    '''
    length = len(bool_list) - 1
    return sum(bit << (length - index) for index, bit in enumerate(bool_list))

def int_to_bool_list(data:int, length:int) -> list[bool]:
    return [bool(data & 1 << index) for index in reversed(range(0, length))]

class Operand():

    def __init__(self, value:int, program:"Program") -> None:
        self.value = value
        self.literal = value
        self._combo:int|Register|None
        match value:
            case 0 | 1 | 2 | 3:
                self._combo = value
            case 4:
                self._combo = program.a
            case 5:
                self._combo = program.b
            case 6:
                self._combo = program.c
            case 7:
                self._combo = None

    @property
    def combo(self) -> int:
        combo = self._combo
        if combo is None:
            raise RuntimeError()
        elif isinstance(combo, int):
            return combo
        else:
            return combo.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"<Operand {self.value}>"

class Register():

    def __init__(self, name:str, value:int) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.value}>"

    def write(self, value:int) -> None:
        self.value = value

class Instruction():

    short_name:str

    def __init__(self, operand:Operand) -> None:
        self.operand:Operand = operand

    def __repr__(self) -> str:
        return f"<{self.short_name} {str(self.operand)}>"

    def run(self, program:"Program", debug:bool=False) -> Optional[int]: ...

class AdvInstruction(Instruction): # division -> A

    short_name = "ADV"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tOperand combo is {self.operand.combo}; A is {program.a.value}; {program.a.value} >> {self.operand.combo} == {program.a.value >> self.operand.combo}.\n\tWriting {program.a.value >> self.operand.combo} to A.")
        program.a.write(program.a.value >> self.operand.combo)

class BxlInstruction(Instruction): # bitwise xor B, operand

    short_name = "BXL"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tOperand literal is {self.operand.literal}; B is {program.b.value}; {program.b.value} ^ {self.operand.literal} == {program.b.value ^ self.operand.literal}.\n\tWriting {program.b.value ^ self.operand.literal} to B")
        program.b.write(program.b.value ^ self.operand.literal)

class BstInstruction(Instruction): # modulo 8

    short_name = "BST"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tOperand combo is {self.operand.combo}; {self.operand.combo} % 8 == {self.operand.combo % 8}.\n\tWriting {self.operand.combo % 8} to B.")
        program.b.write(self.operand.combo % 8)

class JnzInstruction(Instruction): # conditional jump

    short_name = "JNZ"

    def run(self, program:"Program", debug:bool=False) -> Optional[int]:
        if debug:
            print(f"{repr(self)}:\n\tValue of A is 0; advancing by 2." if program.a.value == 0 else f"{repr(self)}:\n\tValue of A is {program.a.value}; going to instruction {program.a.value % 8}.")
        return self.operand.literal if program.a.value != 0 else None

class BxcInstruction(Instruction): # bitwise xor B, C

    short_name = "BXC"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tValue of B is {program.b.value}; value of C is {program.c.value}; {program.b.value} ^ {program.c.value} == {program.b.value ^ program.c.value}.\n\tWriting {program.b.value ^ program.c.value} to B.")
        program.b.write(program.b.value ^ program.c.value)

class OutInstruction(Instruction): # output

    short_name = "OUT"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tOperand combo is {self.operand.combo}; {self.operand.combo} % 8 == {self.operand.combo % 8}.\n\tWriting {self.operand.combo % 8} to output.")
        program.out(self.operand.combo % 8)

class BdvInstruction(Instruction): # division -> B

    short_name = "BDV"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tOperand combo is {self.operand.combo}; A is {program.a.value}; {program.a.value} >> {self.operand.combo} == {program.a.value >> self.operand.combo}.\n\tWriting {program.a.value >> self.operand.combo} to B.")
        program.b.write(program.a.value >> self.operand.combo)

class CdvInstruction(Instruction): # division -> C

    short_name = "CDV"

    def run(self, program:"Program", debug:bool=False) -> None:
        if debug:
            print(f"{repr(self)}:\n\tOperand combo is {self.operand.combo}; A is {program.a.value}; {program.a.value} >> {self.operand.combo} == {program.a.value >> self.operand.combo}.\n\tWriting {program.a.value >> self.operand.combo} to C.")
        program.c.write(program.a.value >> self.operand.combo)

opcodes:list[type[Instruction]] = [
    AdvInstruction,
    BxlInstruction,
    BstInstruction,
    JnzInstruction,
    BxcInstruction,
    OutInstruction,
    BdvInstruction,
    CdvInstruction,
]

class Program():

    def __init__(self, a_register:int, b_register:int, c_register:int, codes:list[int]) -> None:
        self.a = Register("A", a_register)
        self.b = Register("B", b_register)
        self.c = Register("C", c_register)
        self.original_a = a_register
        self.original_b = b_register
        self.original_c = c_register
        self.codes = codes
        self.instructions = [opcodes[opcode](Operand(operand, self)) for opcode, operand in pairwise(codes)]
        self.output:list[int] = []

    def reset(self) -> None:
        self.a.write(self.original_a)
        self.b.write(self.original_b)
        self.c.write(self.original_c)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.a.value}, {self.b.value}, {self.c.value}>"

    def out(self, value:int) -> None:
        self.output.append(value)

    def run(self) -> list[int]:
        self.output = []
        instruction_pointer = 0
        max_range = range(0, len(self.instructions))
        while instruction_pointer in max_range:
            instruction = self.instructions[instruction_pointer]
            instruction_output = instruction.run(self, debug=False)
            if instruction_output is None:
                instruction_pointer += 2
            else:
                instruction_pointer = instruction_output
        self.reset()
        return self.output

class A():

    def __init__(self, data:dict[int,bool|None]|None=None, maximum:int|None=None, minimum:int|None=None) -> None:
        self.data:dict[int, bool|None] = {} if data is None else data
        self.minimum = 1000 if minimum is None else minimum
        self.maximum = -1000 if maximum is None else maximum

    @overload
    def __getitem__(self, position:slice, /) -> list[bool|None]: ...
    @overload
    def __getitem__(self, position:int, /) -> bool|None: ...
    def __getitem__(self, position:int|slice, /) -> bool|None|list[bool|None]:
        if isinstance(position, int):
            return self.data.get(position)
        else:
            return [self.data.get(index) for index in range(position.start, position.stop)]

    def stringify(self) -> str:
        output:list[str] = []
        for bit in self[self.minimum:self.maximum+1]:
            if bit is True:
                output.append("1")
            elif bit is False:
                output.append("0")
            else:
                output.append("?")
        return ",".join(output)

    def __repr__(self) -> str:
        if self.minimum >= 1000 or self.maximum <= -1000:
            return "<A unset>"
        return f"<A {self.stringify()}>"

    def __setitem__(self, index:int, value:bool, /) -> None:
        if index in self.data:
            raise KeyError(f"Bit at {index} is already set!")
        self.data[index] = value
        self.minimum = min(self.minimum, index)
        self.maximum = max(self.maximum, index)

    def to_int(self) -> int:
        '''
        Returns the A as the lowest possible (little-endian) integer.
        '''
        maximum = self.maximum
        return sum((item << (maximum - index)) if (item := self[index]) is True else 0 for index in reversed(range(self.minimum, self.maximum + 1)))

    def copy(self) -> "A":
        return A(self.data.copy(), self.maximum, self.minimum)

def recursive_thing(a:A, offset:int, output_index:int, required_output:list[int], x:int, y:int) -> list[A]:
    # each recursion, offset decreases by 3, output_index increases by 1.
    if output_index >= len(required_output):
        # if output_index is beyond the length of required_output, that means
        # that a valid solution has been reached.
        return [a]
    # b is the window of bits from offset-3 to offset. It can include None
    b = a[offset-3:offset]
    # cs (plural of c) is the list of bit-lists. Each one could be a value of b
    # if the Nones are filled in. The second item of the tuple has a copy of a
    # with the bits set like that.
    cs:list[tuple[list[bool],A]] = []
    none_indices:list[int] = [index for index, bit in enumerate(b) if bit is None]
    for bits in product([False, True], repeat=len(none_indices)):
        c = b.copy()
        a_copy = a.copy()
        for index, bit in zip(none_indices, bits, strict=True):
            c[index] = bit
            a_copy[offset-3+index] = bit
        cs.append((cast(list[bool], c), a_copy)) # by now, c is only bools.
    
    x_list:list[bool] = int_to_bool_list(x, 3)
    # ds is same as cs but every c is xored with x.
    ds:list[tuple[list[bool],A]] = [([c_bit ^ x_bit for c_bit, x_bit in zip(c[0], x_list, strict=True)], c[1]) for c in cs]
    # permutations is a list of tuples. The first item of the tuple is a d.
    # The second item of the tuple is possible values of another window of a
    # (does not include None). The third item of the tuple is a copy of a that
    # includes the bits from the first and second item.
    fs:list[tuple[list[bool],list[bool],A]] = []
    for d, a_copy in ds:
        d_int = bool_list_to_int(d)
        # e is the window of bits from offset-d_int-3 to offset-d_int. It may
        # include None.
        e = a_copy[offset-d_int-3:offset-d_int]
        none_indices:list[int] = [index for index, bit in enumerate(e) if bit is None]
        for bits in product([False, True], repeat=len(none_indices)):
            f = e.copy()
            a_copy_copy = a_copy.copy()
            for index, bit in zip(none_indices, bits, strict=True):
                f[index] = bit
                a_copy_copy[offset-d_int-3+index] = bit
            fs.append((d, cast(list[bool], f), a_copy_copy))
    
    # valid_as is the list of As that produces the valid character.
    valid_as:list[A] = []
    output_item = required_output[output_index] ^ y
    for item1, item2, a_copy in fs:
        int1, int2 = bool_list_to_int(item1), bool_list_to_int(item2)
        if int1 ^ int2 == output_item:
            valid_as.append(a_copy)
    
    output:list[A] = []
    for a_copy in valid_as:
        output.extend(recursive_thing(a_copy, offset - 3, output_index + 1, required_output, x, y))
    return output

def smart_part_2(program:Program) -> int:
    required_instructions:list[type[Instruction]] = [BstInstruction, BxlInstruction, CdvInstruction, BxcInstruction, BxlInstruction, AdvInstruction, OutInstruction, JnzInstruction]
    assert all(isinstance(instruction, required_instruction) for instruction, required_instruction in zip(program.instructions[::2], required_instructions, strict=True))
    instructions = program.instructions[::2] # only relevant instructions; other ones are unreachable.
    x = instructions[1].operand.literal
    y = instructions[4].operand.literal
    solutions = recursive_thing(A(), 0, 0, program.codes, x, y)
    assert len(solutions) == 1
    output = solutions[0].to_int()
    program.a.write(output)
    assert program.run() == program.codes
    return output

def parse_program(file:Path) -> Program:
    with open(file, "rt") as f:
        lines = f.readlines()
    a_register = int(lines[0].split(" ", maxsplit=2)[2].rstrip())
    b_register = int(lines[1].split(" ", maxsplit=2)[2].rstrip())
    c_register = int(lines[2].split(" ", maxsplit=2)[2].rstrip())
    program = [int(code) for code in lines[4].split(" ", maxsplit=1)[1].rstrip().split(",")]
    return Program(a_register, b_register, c_register, program)

def main() -> None:
    program = parse_program(Util.get_input_path(17, "Input"))
    print("Part 1:")
    print(",".join(str(output) for output in program.run()))
    print("Part 2:")
    print(smart_part_2(program))
