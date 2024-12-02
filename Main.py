import importlib
import sys
from pathlib import Path


def main() -> None:
    days:list[str] = []
    for day_path in Path("./Days").iterdir():
        day_name = day_path.name
        days.append(day_name)
        importlib.import_module(f".{day_name}", f"Days.{day_name}")
    selected_day = input("Day: ")
    sys.modules[f"Days.{day_name}.{day_name}"].main()

if __name__ == "__main__":
    main()
