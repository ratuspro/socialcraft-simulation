from typing import List
from .entity import Entity


class Object(Entity):
    __name: str
    __labels: List[str]

    def __init__(self, name: str, labels: List[str]) -> None:
        super().__init__()
        self.__name = name
        self.__labels = labels

    @property
    def name(self) -> str:
        return self.__name

    @property
    def labels(self) -> List[str]:
        return self.__labels

    def tick(self) -> None:
        return super().tick()
