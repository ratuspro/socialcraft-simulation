from .practice import Practice
from ..world import World
from typing import Dict, Any, Optional
from ..entities import Entity


class Sleep(Practice):

    label: str = "Sleep"

    def __init__(
        self, owner, world: World, bed: Entity, min_sleeping_time: int
    ) -> None:
        super().__init__(owner, world)
        self.__bed: Entity = bed
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

    def targetEntity(self) -> Optional[Entity]:
        return self.__bed


class Idle(Practice):

    label: str = "Idle"

    def __init__(self, owner, world: World, min_idle_time: int) -> None:
        super().__init__(owner, world)
        self.__min_idle_time = min_idle_time
        self.__timer = 0

    def enter(self) -> None:
        super().enter()
        self.__timer = 0

    def has_ended(self) -> bool:
        return self.__timer > self.__min_idle_time

    def tick(self) -> None:
        self.__timer += 1

    def exit(self) -> None:
        super().exit()

    def properties(self) -> Dict[str, Any]:
        return super().properties()
