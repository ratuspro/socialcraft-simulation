from typing import List
from .entity import Entity


class Object(Entity):
    __name: str

    def __init__(self, name: str) -> None:
        super().__init__()
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    def tick(self) -> None:
        return super().tick()

    def __str__(self) -> str:
        return self.__name
