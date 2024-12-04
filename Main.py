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
    if selected_day == "*":
        for selected_day in days:
            print(f"\n--- {selected_day} ---")
            sys.modules[f"Days.{selected_day}.{selected_day}"].main()
    else:
        sys.modules[f"Days.Day{selected_day}.Day{selected_day}"].main()

if __name__ == "__main__":
    main()
