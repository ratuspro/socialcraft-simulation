import typing
from typing import List

from ..world import Location, World
from .practice import Practice
from .agent import Agent


class MoveToLocation(Practice):
    __destination: Location
    __path: List[Location]

    def __init__(
        self,
        owner: Agent,
        world: World,
        destination: Location,
        label: str = "MoveToLocation",
    ) -> None:
        super().__init__(owner, world, label)
        self.__destination = destination
        self.__path = []

    def enter(self) -> None:
        super().enter()
        agent_location = self._world.get_entity_location(self._owner)
        self.__path = self._world.get_path_to(agent_location, self.__destination)

    def has_ended(self) -> bool:
        return self._world.get_entity_location(self._owner) == self.__destination

    def tick(self) -> None:

        current_path_position = self.__path.index(
            self._world.get_entity_location(self._owner)
        )
        if current_path_position < len(self.__path) - 1:
            self._world.move_entity_to_location(
                self._owner, self.__path[current_path_position + 1]
            )

    def exit(self) -> None:
        super().exit()
