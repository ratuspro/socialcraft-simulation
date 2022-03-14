from .practice import Practice
from ..world import World
from .agent import Agent


class InteractWithOther(Practice):
    def __init__(self, owner: Agent, world: World, label: str) -> None:
        super().__init__(owner, world, label)

    def tick(self) -> None:
        self.__time += 1

    def enter(self) -> None:
        super().enter()
        self.__time = 0

    def exit(self) -> None:
        super().exit()

    def has_ended(self) -> bool:
        return self.__time > 12
