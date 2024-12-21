from pathlib import Path
from typing import Callable

from typing_extensions import Self


class Grid[T]():

    @classmethod
    def new_filled(cls, fill_item:Callable[[],T], size:tuple[int,int]) -> Self:
        return cls([[fill_item() for x in range(size[0])] for y in range(size[1])], size)

    def __init__(self, grid:list[list[T]], size:tuple[int,int]) -> None:
        self.grid = grid
        self.size = size
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.size[0]}×{self.size[1]}>"

    def __getitem__(self, position:tuple[int,int]) -> T:
        x, y = position
        if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]:
            return self.grid[y][x]
        else:
            raise KeyError(f"Position {position} is out of bounds!")
    
    def get[D](self, position:tuple[int,int], default:D=None) -> T|D:
        x, y = position
        if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]:
            return self.grid[y][x]
        else:
            return default
    
    def __setitem__(self, position:tuple[int,int], value:T) -> None:
        x, y = position
        if x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]:
            self.grid[y][x] = value
        else:
            raise KeyError(f"Position {position} is out of bounds!")

def get_path(day:int, path:str) -> Path:
    root_path = Path("./Days/")
    day_path = root_path.joinpath(f"Day{day}")
    return day_path.joinpath(path)

def get_input_path(day:int, name:str|None, suffix:str|None="txt") -> Path:
    '''
    Returns the Path of an input file.
    
    :day: The day number.
    :name: The name of the file, not including path or suffix.
    :suffix: A suffix to use besides txt. Do not include the starting period.
    '''
    root_path = Path("./Days/")
    day_path = root_path.joinpath(f"Day{day}")
    input_path = day_path.joinpath(f"Input")
    if name is None:
        name = input("Select a file name (without suffix): ")
    if suffix is None:
        file_path = input_path.joinpath(name)
    else:
        file_path = input_path.joinpath(f"{name}.{suffix}")
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot find file {file_path.as_posix()}!")
    return file_path
