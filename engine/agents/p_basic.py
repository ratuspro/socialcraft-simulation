from .practice import Practice
from .agent import Agent
from ..world import World


class Sleep(Practice):
    def __init__(self, owner: Agent, world: World, min_sleep_time: int = 100) -> None:
        super().__init__(owner, world, "Sleep")
        self.__min_sleep_time = min_sleep_time

    def tick(self) -> None:
        self.__sleep_time += 1

    def enter(self) -> None:
        super().enter()
        self.__sleep_time = 0

    def exit(self) -> None:
        super().exit()

    def has_ended(self) -> bool:
        return self.__sleep_time >= self.__min_sleep_time
