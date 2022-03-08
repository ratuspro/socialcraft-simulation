from ..world import Updatable


class Time(Updatable):
    __tick: int

    def __init__(self) -> None:
        super().__init__()
        self.__tick = 0

    def tick(self) -> None:
        self.__tick += 1

    def value(self) -> int:
        return self.__tick

    def __str__(self) -> str:
        return f"Time [tick={self.__tick}]"
