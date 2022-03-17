from __future__ import annotations
from abc import ABC, abstractmethod

from engine.world.location import Location
from ..world import World
from ..logger import Logger
from typing import Any, Dict, Tuple, Optional


class Practice(ABC):
    def __init__(self, owner, world: World, label: str) -> None:
        self._owner = owner
        self._world: World = world
        self.__practice_label = label

    @abstractmethod
    def tick(self) -> None:
        pass

    @abstractmethod
    def enter(self) -> None:
        Logger.instance().on_practice_starts(
            self._owner, self.__practice_label, self.properties()
        )

    @abstractmethod
    def exit(self) -> None:
        Logger.instance().on_practice_ends(self._owner, self.__practice_label)

    @abstractmethod
    def has_ended(self) -> bool:
        pass

    def properties(self) -> Dict[str, Any]:
        return {}

    def targetLocation(self) -> Optional[Location]:
        return None
