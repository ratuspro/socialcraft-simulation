from ..world import Updatable


class Agent(Updatable):
    __name: str

    def __init__(self, name: str) -> None:
        super().__init__()
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    def tick(self) -> None:
        return None

    def __str__(self) -> str:
        return f"Agent {self.name}"
