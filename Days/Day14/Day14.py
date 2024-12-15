from functools import reduce
from itertools import count
from operator import mul
from pathlib import Path

from PIL import Image, ImageDraw

import Util


class Robot():

    def __init__(self, x:int, y:int, vx:int, vy:int) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} p={self.x},{self.y} v={self.vx},{self.vy}>"

    def move(self, security_size:tuple[int,int]) -> None:
        self.x += self.vx
        self.y += self.vy
        self.x %= security_size[0]
        self.y %= security_size[1]

    def copy(self) -> "Robot":
        return Robot(self.x, self.y, self.vx, self.vy)

class BathroomSecurity():

    def __init__(self, size:tuple[int,int], robots:list[Robot]) -> None:
        self.size = size
        self.robots = robots

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]} len {len(self.robots)}>"

    def copy(self) -> "BathroomSecurity":
        robots = [robot.copy() for robot in self.robots]
        return BathroomSecurity(self.size, robots)

    def stringify(self) -> str:
        output:list[list[int]] = [[0] * self.size[0] for i in range(self.size[1])]
        for robot in self.robots:
            output[robot.y][robot.x] += 1
        return "\n".join(
            "".join(
                "." if item == 0 else
                "#" if item > 9 else
                str(item)
                for item in row
            )
            for row in output
        )

    def print(self) -> None:
        print(self.stringify())

    def wait_1_second(self) -> None:
        for robot in self.robots:
            robot.move(self.size)

    def wait_seconds(self, amount:int) -> None:
        for i in range(amount):
            self.wait_1_second()

    def to_file(self) -> Image.Image:
        image = Image.new("1", self.size)
        draw = ImageDraw.ImageDraw(image, )
        draw.point([(robot.x, robot.y) for robot in self.robots], fill=1)
        return image

    def to_files(self, length:int, offset:int) -> None:
        output_path = Util.get_path(14, "Output")
        output_path.mkdir(exist_ok=True)
        for file in output_path.iterdir():
            file.unlink()
        self.wait_seconds(offset)
        for second in range(length):
            image = self.to_file()
            image.save(output_path.joinpath(f"{second+offset}.png"), "PNG")
            self.wait_1_second()

    def get_safety_factor(self) -> int:
        center_x, x_odd = divmod(self.size[0], 2)
        center_y, y_odd = divmod(self.size[1], 2)
        x_odd, y_odd = bool(x_odd), bool(y_odd)
        quadrants:list[int] = [0 for i in range(4)]
        for robot in self.robots:
            if x_odd and robot.x == center_x or y_odd and robot.y == center_y:
                continue
            elif robot.x < center_x and robot.y < center_y:
                quadrants[0] += 1 # top left
            elif robot.x > center_x and robot.y < center_y:
                quadrants[1] += 1 # top right
            elif robot.x < center_x and robot.y > center_y:
                quadrants[2] += 1 # bottom left
            elif robot.x > center_x and robot.y > center_y:
                quadrants[3] += 1 # bottom right
        return reduce(mul, quadrants, 1)

    def get_bunchedness(self, vertical:bool) -> int:
        overlappedness:list[int] = [0] * (self.size[vertical])
        for robot in self.robots:
            overlappedness[robot.y if vertical else robot.x] += 1
        return overlappedness.count(0)

def parse_security(file:Path) -> BathroomSecurity:
    with open(file, "rt") as f:
        lines = f.readlines()
    # In each file, I placed an additional line such as "size=101,103".
    size_x, size_y = (int(coordinate) for coordinate in lines.pop(0).split("=")[1].split(","))
    robots:list[Robot] = []
    for line in lines:
        line_position, line_velocity = line.split(" ")
        position_x, position_y = (int(coordinate) for coordinate in line_position.split("=")[1].split(","))
        velocity_x, velocity_y = (int(coordinate) for coordinate in line_velocity.split("=")[1].split(","))
        robots.append(Robot(position_x, position_y, velocity_x, velocity_y))
    return BathroomSecurity((size_x, size_y), robots)

def get_christmas_tree_time(security:BathroomSecurity) -> int:
    robot_count = len(security.robots)
    expected_horizontal_bunchedness = security.size[0] * (1 - 1/security.size[0])**robot_count
    expected_vertical_bunchedness   = security.size[1] * (1 - 1/security.size[1])**robot_count
    horizontal_offset:int|None = None
    vertical_offset:int|None = None
    for second in range(max(security.size)):
        horizontal_bunchedness = security.get_bunchedness(False)
        vertical_bunchedness = security.get_bunchedness(True)
        if horizontal_bunchedness > 10 * expected_horizontal_bunchedness:
            if horizontal_offset is not None:
                raise RuntimeError("Multiple horizontal bunchedness anomalies detected!")
            horizontal_offset = second
        if vertical_bunchedness > 10 * expected_vertical_bunchedness:
            if vertical_offset is not None:
                raise RuntimeError("Multiple vertical bunchedness anomalies detected!")
            vertical_offset = second
        security.wait_1_second()
    if horizontal_offset is None:
        raise RuntimeError("No horizontal bunchedness anomalies detected!")
    if vertical_offset is None:
        raise RuntimeError("No vertical bunchedness anomalies detected!")
    for i in count():
        cycle1_point = security.size[1] * i + vertical_offset
        if (cycle1_point - horizontal_offset) % security.size[0] == 0:
            return cycle1_point
    else:
        assert False

def main() -> None:
    security = parse_security(Util.get_input_path(14, "Input"))
    print("Part 1:")
    security_1 = security.copy()
    security_1.wait_seconds(100)
    print(security_1.get_safety_factor())
    print("Part 2:")
    print(get_christmas_tree_time(security))
