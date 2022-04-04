from __future__ import annotations
from abc import abstractmethod
from utils import DependencyManager
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
        DependencyManager.instance().get_logger().register_entry(self._world.time, Logger.A_PRACTICESTARTS, self._owner, {'practice_label': self.label} | self.properties())
        
    @abstractmethod
    def exit(self) -> None:
        DependencyManager.instance().get_logger().register_entry(self._world.time, Logger.A_PRACTICEENDS, self._owner, {'practice_label': self.label})

    @abstractmethod
    def has_ended(self) -> bool:
        pass

    def properties(self) -> Dict[str, Any]:
        return {}

    def targetLocation(self) -> Optional[Location]:
        return None

    def targetEntity(self) -> Optional[Object]:
        return None
