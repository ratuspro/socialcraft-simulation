from xml.dom.minidom import Entity
from .practice import Practice
from ..world import Location, World
from typing import List, Dict, Any, Optional
from ..entities import Object


class Sleep(Practice):

    label: str = "Sleep"

    def __init__(
        self, owner, world: World, bed: Object, min_sleeping_time: int
    ) -> None:
        super().__init__(owner, world)
        self.__bed: Object = bed
        self.__min_sleeping_time = min_sleeping_time
        self.__timer = 0

    def enter(self) -> None:
        super().enter()
        self.__timer = 0
        self._world.change_entity_attribute(self._owner, self.__bed, "occupied", True)

    def has_ended(self) -> bool:
        return self.__timer > self.__min_sleeping_time

    def tick(self) -> None:
        self.__timer += 1

    def exit(self) -> None:
        super().exit()
        self._world.change_entity_attribute(self._owner, self.__bed, "occupied", False)

    def properties(self) -> Dict[str, Any]:
        return super().properties() | {"bed": str(self.__bed)}

    def targetLocation(self) -> Optional[Location]:
        return None
