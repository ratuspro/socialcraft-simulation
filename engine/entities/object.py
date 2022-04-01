from typing import List
from .entity import Entity


class Object(Entity):
    __name: str

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def tick(self) -> None:
        return super().tick()

    def __str__(self) -> str:
        return self.name
