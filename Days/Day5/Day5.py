from pathlib import Path

import Util


def swap(pages:list[int], positions:dict[int,int], page1:int, page2:int) -> None:
    '''
    Swaps the two items by modifying both `pages` and `positions`.
    '''
    index1:int = positions[page1]
    index2:int = positions[page2]
    pages[index1], pages[index2] = pages[index2], pages[index1]
    positions[page1] = index2
    positions[page2] = index1

class Rule():

    def __init__(self, before:int, after:int) -> None:
        self.before:int = before
        self.after:int = after

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.before}|{self.after}>"

    def __contains__(self, page:set[int]) -> bool:
        return self.before in page and self.after in page

    def satisfied(self, positions:dict[int,int]) -> bool:
        '''
        Returns if the Rule is satisfied.
        Precondition: Both `before` and `after` are keys of `positions`.

        :positions: A mapping of each page to its index in an Update.
        '''
        return positions[self.before] < positions[self.after]

class Update():

    def __init__(self, pages:list[int]) -> None:
        self.pages:list[int] = pages
        self.positions:dict[int,int] = {page: index for index, page in enumerate(self.pages)}
        assert len(self.pages) % 2 == 1

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Update) and self.pages == value.pages

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {",".join(str(page) for page in self.pages)}>"

    def __len__(self) -> int:
        return len(self.pages)

    def middle(self) -> int:
        '''
        Returns the middle page.
        '''
        return self.pages[len(self) // 2]

    def is_in_order(self, all_rules:list[Rule]) -> bool:
        return all(rule.satisfied(self.positions) for rule in all_rules if (rule.before in self.positions and rule.after in self.positions))

    def sort(self, all_rules:list[Rule]) -> "Update":
        pages:list[int] = self.pages.copy()
        positions:dict[int,int] = self.positions.copy()
        pages_set:set[int] = set(pages)
        relevant_rules = [rule for rule in all_rules if pages_set in rule]
        satisfied = False
        while not satisfied:
            satisfied = True
            for rule in relevant_rules:
                if not rule.satisfied(positions):
                    swap(pages, positions, rule.before, rule.after)
                    satisfied = False
        return Update(pages)

def parse(file:Path) -> tuple[list[Rule], list[Update]]:
    with open(file, "rt") as f:
        text = f.read()
    rules_text, updates_text = text.split("\n\n")
    rules:list[Rule] = [Rule(*(int(page) for page in line.split("|", maxsplit=1))) for line in rules_text.split("\n")]
    updates:list[Update] = [Update([int(page) for page in line.split(",")]) for line in updates_text.split("\n")]
    return rules, updates

def main() -> None:
    rules, updates = parse(Util.get_input_path(5, "Input"))
    print("Part 1:")
    print(sum(update.middle() for update in updates if update.is_in_order(rules)))
    print("Part 2:")
    print(sum(update.sort(rules).middle() for update in updates if not update.is_in_order(rules)))
