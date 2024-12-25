import json
from collections import defaultdict
from itertools import chain, count, takewhile
from pathlib import Path
from typing import cast

import Util


class Gate():

    short_name:str
    logigator_type:int

    def __init__(self, wire1:str, wire2:str, output:str) -> None:
        self.wire1 = wire1
        self.wire2 = wire2
        self.output = output
        if self.wire1.startswith("y") and self.wire2.startswith("x"):
            self.wire1, self.wire2 = self.wire2, self.wire1

    def __repr__(self) -> str:
        return f"<{self.wire1} {self.short_name} {self.wire2} -> {self.output}>"

    def __contains__(self, wire:str) -> bool:
        return self.wire1 == wire or self.wire2 == wire

    def __hash__(self) -> int:
        return hash((self.logigator_type, self.wire1, self.wire2, self.output))

    def startswith(self, letter:str) -> bool:
        return self.wire1.startswith(letter) or self.wire2.startswith(letter)

    def run(self, value1:bool, value2:bool) -> bool: ...

class AndGate(Gate):

    short_name = "AND"
    logigator_type = 2

    def run(self, value1: bool, value2: bool) -> bool:
        return value1 and value2

class OrGate(Gate):

    short_name = "OR"
    logigator_type = 3

    def run(self, value1: bool, value2: bool) -> bool:
        return value1 or value2

class XorGate(Gate):

    short_name = "XOR"
    logigator_type = 4

    def run(self, value1: bool, value2: bool) -> bool:
        return value1 ^ value2

GATE_TYPES:list[type[Gate]] = [AndGate, OrGate, XorGate]

def swap_gates(gate1:Gate, gate2:Gate, exceptions:list[str], debug:bool=False) -> None:
    # swaps the outputs of the gates.
    if debug:
        print(f"Swapping {gate1} and {gate2}'s output wires.")
    exceptions.append(gate1.output)
    exceptions.append(gate2.output)
    gate1.output, gate2.output = gate2.output, gate1.output

class MonitoringDevice():

    def __init__(self, wire_initial:dict[str,bool], gates:list[Gate], all_wires:list[str]) -> None:
        self.wire_initial:dict[str,bool] = wire_initial
        self.gates:list[Gate] = gates
        self.all_wires:list[str] = all_wires

    def get_inputs(self) -> tuple[int,int]:
        num1, num2 = (sum(cast(bool, self.wire_initial[wire_name]) << index for index, wire_name in takewhile(lambda wire: wire[1] in self.wire_initial, enumerate(map(lambda index: letter + str(index).zfill(2), count())))) for letter in "xy")
        return num1, num2

    def __repr__(self) -> str:
        num1, num2 = self.get_inputs()
        return f"<{self.__class__.__name__} {num1} + {num2}>"

    def run(self) -> int:
        wire_gates:defaultdict[str,list[Gate]] = defaultdict(lambda: [])
        for gate in self.gates:
            wire_gates[gate.wire1].append(gate)
            wire_gates[gate.wire2].append(gate)
        unexplored_wires:list[str] = list(self.wire_initial.keys())
        all_wires:dict[str,bool|None] = {wire: None for wire in self.all_wires}
        all_wires.update(self.wire_initial)
        while len(unexplored_wires) > 0:
            # because each wire is the output of only one gate, checking if
            # it's visited at this point does not matter.
            unexplored_wire = unexplored_wires.pop()
            for gate in wire_gates[unexplored_wire]:
                value1, value2 = all_wires[gate.wire1], all_wires[gate.wire2]
                if value1 is not None and value2 is not None:
                    all_wires[gate.output] = gate.run(value1, value2)
                    unexplored_wires.append(gate.output)
        return sum(
            cast(bool, all_wires[wire_name]) << index
            for index, wire_name in takewhile(
                lambda wire: wire[1] in all_wires,
                enumerate(map(lambda index: f"z{str(index).zfill(2)}", count()))
            )
        )

    def make_logigator_circuit(self) -> None:
        elements:list[dict] = []
        wire_ids = {wire: index for index, wire in enumerate(self.all_wires)} # used for tunnels
        for index, (input_wire, value) in enumerate(self.wire_initial.items()):
            elements.append({"t": 201, "p": [1, index], "o": 1}) # switch
            if value:
                elements.append({"t": 1, "p": [3, index], "i": 1, "o": 1}) # not gate
            else:
                elements.append({"t": 0, "p": [2, index], "q": [5, index]}) # wire
            elements.append({"t": 8, "p": [6, index], "n": [wire_ids[input_wire]], "i": 1}) # tunnel
            elements.append({"t": 7, "p": [8, index], "s": input_wire}) # label

        for index, wire_name in takewhile(lambda wire: wire[1] in wire_ids, enumerate(map(lambda index: f"z{str(index).zfill(2)}", count()))):
            elements.append({"t": 7, "p": [12, index], "s": wire_name}) # label
            elements.append({"t": 8, "r": 2, "p": [15, index], "n": [wire_ids[wire_name]], "i": 1}) # tunnel
            elements.append({"t": 202, "p": [18, index], "i": 1})

        input_gates:list[Gate] = []
        internal_gates:list[Gate] = []
        output_gates:list[Gate] = []
        for gate in self.gates:
            if gate.startswith("x") or gate.startswith("y"):
                input_gates.append(gate)
            elif gate.output.startswith("z"):
                output_gates.append(gate)
            else:
                internal_gates.append(gate)
        input_gates.sort(key=lambda gate: (gate.wire1 if gate.wire1 < gate.wire2 else gate.wire2, gate.logigator_type))
        output_gates.sort(key=lambda gate: gate.output)

        for set_index, gate_set in enumerate([input_gates, internal_gates, output_gates]):
            for index, gate in enumerate(gate_set):
                elements.append({"t": 7, "p": [22 + 14*set_index, index * 2 + 0], "s": gate.wire1}) # label 1
                elements.append({"t": 8, "p": [25 + 14*set_index, index * 2 + 0], "r": 2, "n": [wire_ids[gate.wire1]], "i": 1}) # tunnel 1
                elements.append({"t": 7, "p": [22 + 14*set_index, index * 2 + 1], "s": gate.wire2}) # label 2
                elements.append({"t": 8, "p": [25 + 14*set_index, index * 2 + 1], "r": 2, "n": [wire_ids[gate.wire2]], "i": 1}) # tunnel 2
                elements.append({"t": gate.logigator_type, "p": [28 + 14*set_index, index * 2], "i": 2, "o": 1}) # gate
                elements.append({"t": 8, "p": [31 + 14*set_index, index * 2], "n": [wire_ids[gate.output]], "i": 1}) # tunnel output
                elements.append({"t": 7, "p": [33 + 14*set_index, index * 2], "s": gate.output}) # label output

        project = {"project": {"name": "CrowdingFaun624", "elements": elements}, "components": []}
        with open(Util.get_path(24, "diagram.json"), "wt") as f:
            json.dump(project, f)

    def correct_full_adder(
        self,
        index:int,
        carry_in:Gate,
        gates:dict[tuple[str,str,type[Gate]],Gate],
        gate_outputs:dict[str,Gate],
        wire_inputs:dict[tuple[str,type[Gate]],tuple[Gate,str]],
        wire_all_inputs:dict[str,list[Gate]],
        gate_inputs:dict[tuple[Gate, type[Gate]], list[Gate]],
        adder_width:int,
        exceptions:list[str],
        debug:bool=False
    ) -> None:
        # I am currently looking at https://images.squarespace-cdn.com/content/v1/5d52f7bd9d7b3e0001819015/1576095351164-BYVI8SL6SD4FMP819T2F/full-adder-circuit.png
        # for a diagram of a full adder. From top to bottom, the gates are named here as [xor, sum_gate, and1, carry_out, and2].

        # For sum_gate, there are three possible scenarios:
        #   1. xor and carry_in do not point to the same XOR gate and xor or
        #      carry point to sum_gate. To fix it, swap the output wires of
        #      sum_gate's other input with carry_in.
        #   2. sum_gate points to the wrong wire. If both xor and carry_in
        #      point to a different gate than z{index}, then we are in this
        #      scenario. To fix it, we swap the output wire of the XOR gate
        #      that xor and carry_in point to with the one that points at
        #      z{index}.
        #   3. Multiple XOR gates point to sum_gate. To fix it, we add the XOR
        #      gates that are not xor to the exceptions list.
        #   4. xor points to the wrong wire. If xor is not the same gate as the
        #      XOR gate that points to sum_gate, then we are in this scenario.
        #      To fix it, we swap the output wires of the XOR gate that points
        #      to sum_gate with xor's output wire.
        #   5. Multiple AND gates (when index > 1) or OR gates (when index ==
        #      1) point to sum_gate. To fix it, we add the AND or OR gates that
        #      are not carry_in to the exceptions list.
        #   6. carry_in points to the wrong wire. If the AND or OR gate that
        #      points to sum_gate is not the same as carry_in, then we are in
        #      this scenario. To fix it, we swap the output wire of carry_in
        #      with with the output wire of the AND or OR gate that points at
        #      sum_gate.
        xor_gate_from_left = gates[f"x{str(index).zfill(2)}", f"y{str(index).zfill(2)}", XorGate]
        sum_gate_from_left = gates.get((xor_gate_from_left.output, carry_in.output, XorGate))
        sum_gate_from_right = gate_outputs[f"z{str(index).zfill(2)}"]
        if sum_gate_from_left is None:
            # scenario 1 is true.
            if xor_gate_from_left.output in sum_gate_from_right:
                other_wire = sum_gate_from_right.wire1 if sum_gate_from_right.wire2 == xor_gate_from_left.output else sum_gate_from_right.wire2
                swap_gates(carry_in, gate_outputs[other_wire], exceptions, debug=debug)
            elif carry_in.output in sum_gate_from_right:
                other_wire = sum_gate_from_right.wire1 if sum_gate_from_right.wire2 == carry_in.output else sum_gate_from_right.wire2
                swap_gates(xor_gate_from_left, gate_outputs[other_wire], exceptions, debug=debug)
            else:
                raise RuntimeError()
        elif sum_gate_from_left is not sum_gate_from_right:
            # scenario 2 is true.
            swap_gates(sum_gate_from_left, sum_gate_from_right, exceptions, debug=debug)
            sum_gate_from_left = sum_gate_from_right
        sum_gate = sum_gate_from_right

        xor_gate_from_right = gate_inputs[sum_gate, XorGate]
        if len(xor_gate_from_right) != 1:
            # scenario 3 is true.
            exceptions.extend(gate.output for gate in xor_gate_from_right if gate is not xor_gate_from_left)
        elif xor_gate_from_left is not xor_gate_from_right[0]:
            # scenario 4 is true.
            swap_gates(xor_gate_from_left, xor_gate_from_right[0], exceptions, debug=debug)
        xor_gate = xor_gate_from_left

        # Because the zeroth output bit uses a half adder (due to there being
        # no carry in), carry_in is an AND gate for the oneth output bit.
        carry_in_from_right = gate_inputs[sum_gate, AndGate if index == 1 else OrGate]
        if len(carry_in_from_right) != 1:
            # scenario 5 is true.
            exceptions.extend(gate.output for gate in carry_in_from_right if gate is not carry_in)
        elif carry_in is not carry_in_from_right[0]:
            # scenario 6 is true.
            swap_gates(carry_in, carry_in_from_right[0], exceptions, debug=debug)

        # For carry_out, there are two possible scenarios:
        #   1. and1 points to the wrong wire. If and1 points to a gate that is
        #      not an OR gate, we are in this scenario. To fix it, we assume
        #      that the OR gate that and2 points to is the correct OR gate, and
        #      continue from there. (No swapping occurs.)
        #   2. and2 points to the wrong wire. If and2 points to a gate that is
        #      not an OR gate, we are in this scenario. To fix it, we assume
        #      that the OR gate that and1 points to is the correct OR gate, and
        #      continue from there. (No swapping occurs.)
        # If both and1 and and2 point to different OR gates, it is impossible
        # to know which one is correct, so an exception is raised.
        and2_gate = gates[f"x{str(index).zfill(2)}", f"y{str(index).zfill(2)}", AndGate]
        and1_gate = gates[xor_gate.output, carry_in.output, AndGate]
        and1_outputs = wire_all_inputs[and1_gate.output]
        and2_outputs = wire_all_inputs[and2_gate.output]
        if len(and1_outputs) != 1 or not isinstance(and1_outputs[0], OrGate):
            # scenario 1
            exceptions.append(and1_gate.output)
            carry_out = and2_outputs[0]
        elif len(and2_outputs) != 1 or not isinstance(and2_outputs[0], OrGate):
            # scenario 2
            exceptions.append(and2_gate.output)
            carry_out = and1_outputs[0]
        elif and1_outputs[0] is not and2_outputs[0]:
            # cannot be determined.
            raise RuntimeError("Cannot find carry_out!")
        else:
            # no error
            carry_out = and1_outputs[0]

        if index == adder_width:
            if carry_out.output != f"z{str(adder_width + 1).zfill(2)}":
                exceptions.append(carry_out.output)
        else:
            self.correct_full_adder(index + 1, carry_out, gates, gate_outputs, wire_inputs, wire_all_inputs, gate_inputs, adder_width, exceptions, debug=debug)

    def correct(self, debug:bool=False) -> list[str]:
        gates:dict[tuple[str,str,type[Gate]],Gate] = {(gate.wire1, gate.wire2, type(gate)): gate for gate in self.gates}
        gates.update(((gate.wire2, gate.wire1, type(gate)), gate) for gate in self.gates)
        gate_outputs:dict[str,Gate] = {gate.output: gate for gate in self.gates}
        wire_inputs:dict[tuple[str,type[Gate]],tuple[Gate,str]] = {}
        gate_inputs:dict[tuple[Gate,type[Gate]], list[Gate]] = defaultdict(lambda: [])
        wire_all_inputs:defaultdict[str,list[Gate]] = defaultdict(lambda: [])
        for gate in self.gates:
            wire_inputs[gate.wire1, type(gate)] = (gate, gate.wire2)
            wire_inputs[gate.wire2, type(gate)] = (gate, gate.wire1)
            if gate.wire1 in gate_outputs:
                
                gate_inputs[gate, type(input_gate := gate_outputs[gate.wire1])].append(input_gate)
            if gate.wire2 in gate_outputs:
                
                gate_inputs[gate, type(input_gate := gate_outputs[gate.wire2])].append(input_gate)
            wire_all_inputs[gate.wire1].append(gate)
            wire_all_inputs[gate.wire2].append(gate)
        adder_width = max(int(wire[1:]) for wire in self.all_wires if wire.startswith("x"))

        exceptions:list[str] = []
        if (gate := gates["x00", "y00", XorGate]).output != "z00":
            swap_gates(gate, gate_outputs["z00"], exceptions, debug=debug)
        carry_out = gates["x00", "y00", AndGate]
        self.correct_full_adder(1, carry_out, gates, gate_outputs, wire_inputs, wire_all_inputs, gate_inputs, adder_width, exceptions, debug=debug)
        return exceptions

def parse_monitoring_device(file:Path) -> MonitoringDevice:
    with open(file, "rt") as f:
        initial_text, gates_text = f.read().split("\n\n", maxsplit=1)
    wire_initial = {(split_line := line.split(":", maxsplit=1))[0]: bool(int(split_line[1])) for line in initial_text.split("\n")}
    gate_names = {gate.short_name: gate for gate in GATE_TYPES}
    gates = [gate_names[(split_line := line.split(" ", maxsplit=4))[1]](split_line[0], split_line[2], split_line[4]) for line in gates_text.split("\n")]
    all_wires:set[str] = {wire for wire in chain((gate.wire1 for gate in gates), (gate.wire2 for gate in gates), (gate.output for gate in gates))}
    all_wires.update(wire_initial)
    return MonitoringDevice(wire_initial, gates, sorted(all_wires))

def main() -> None:
    monitoring_device = parse_monitoring_device(Util.get_input_path(24, "Input"))
    print("Part 1:")
    print(monitoring_device.run())
    print("Part 2:")
    print(",".join(sorted(set(monitoring_device.correct()))))
