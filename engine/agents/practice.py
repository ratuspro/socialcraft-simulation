from __future__ import annotations
from abc import abstractmethod
from cProfile import label

from engine.world.location import Location
from ..world import World
from ..logger import Logger
from typing import Any, Dict, Optional
from ..entities import Object


class Practice:
    label: str = "Practice"

    def __init__(self, owner, world: World) -> None:
        self._owner = owner
        self._world: World = world

    @abstractmethod
    def tick(self) -> None:
        pass

    @abstractmethod
    def enter(self) -> None:
        Logger.instance().on_practice_starts(self._owner, self.label, self.properties())

    @abstractmethod
    def exit(self) -> None:
        Logger.instance().on_practice_ends(self._owner, self.label)

    @abstractmethod
    def has_ended(self) -> bool:
        pass

    def properties(self) -> Dict[str, Any]:
        return {}

    def targetLocation(self) -> Optional[Location]:
        return None

    def targetEntity(self) -> Optional[Object]:
        return None
