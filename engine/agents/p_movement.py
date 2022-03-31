from .practice import Practice
from ..world import Location, World
from typing import List, Dict, Any, Optional


class MoveToLocation(Practice):

    label: str = "MoveToLocation"

    def __init__(
        self,
        owner,
        world: World,
        destination: Location,
    ) -> None:
        super().__init__(owner, world)
        self.__destination: Location = destination
        self.__path: List[Location] = []

    def enter(self) -> None:
        super().enter()
        agent_location = self._world.get_entity_location(self._owner)
        if agent_location is None:
            raise Exception("Attempting to move to a location agent not yet placed")
        self.__path = self._world.get_path_to(agent_location, self.__destination)

    def has_ended(self) -> bool:
        return self._world.get_entity_location(self._owner) == self.__destination

    def tick(self) -> None:

        current_location = self._world.get_entity_location(self._owner)

        if current_location is None:
            raise Exception("Attempting to move agent without a location")

        if (
            self._world.get_time_since_last_movement(self._owner)
            <= current_location.min_time_inside
        ):
            return

        current_path_position = self.__path.index(current_location)

        if current_path_position < len(self.__path) - 1:
            self._world.move_entity_to_location(
                self._owner, self.__path[current_path_position + 1]
            )

    def exit(self) -> None:
        super().exit()

    def properties(self) -> Dict[str, Any]:
        return super().properties() | {"destination": str(self.__destination)}

    def targetLocation(self) -> Optional[Location]:
        return self.__destination
