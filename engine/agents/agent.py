from ..entities import Entity


class Agent(Entity):
    def __init__(self, name: str, world) -> None:
        self.__name = name
        self.__world = world

    @property
    def name(self):
        return self.__name

    @property
    def world(self):
        return self.__world

    def tick(self) -> None:
        pass
