from pathlib import Path


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
