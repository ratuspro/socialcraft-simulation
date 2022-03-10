from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Callable, Dict, Any, List

import random
from engine.world.core import Location
from ..world import Entity, World, Context
from ..logger import Logger


class Agent(Entity):
    __name: str
    __practices: List[Practice]
    __current_practice: Practice | None

    def __init__(self, name: str) -> None:
        super().__init__()
        self.__name = name
        self.__practices = []
        self.__current_practice = None

    @property
    def name(self) -> str:
        return self.__name

    def add_practice(self, new_practice: Practice) -> None:
        self.__practices.append(new_practice)

    def __get_best_practices(self) -> List[Practice]:
        best_practices, best_practice_salience = [], -1

        for practice in self.__practices:
            salience = practice.calculate_salience(self.context)
            if salience == best_practice_salience:
                best_practices.append(practice)
            elif salience > best_practice_salience:
                best_practices = [practice]
                best_practice_salience = salience

        return best_practices

    def tick(self) -> None:

        if self.__current_practice is not None:
            if self.__current_practice.has_ended():
                self.__current_practice.exit()
                self.__current_practice = None
            else:
                self.__current_practice.tick()
        else:
            new_practice = random.choice(self.__get_best_practices())
            if new_practice is not None:
                self.__current_practice = new_practice
                self.__current_practice.enter()

    def __str__(self) -> str:
        return f"Agent {self.name}"


class Practice(ABC):
    _owner: Agent
    _world: World
    __salience_function: Callable[[Context], float]

    def __init__(self, owner: Agent, world: World, label: str) -> None:
        self._owner = owner
        self._world = world
        self.__practice_label = label

    def set_salience_function(self, fn_salience: Callable[[Context], float]) -> None:
        self.__salience_function = fn_salience

    def calculate_salience(self, context: Context) -> float:
        return self.__salience_function(context)

    @abstractmethod
    def tick(self) -> None:
        pass

    @abstractmethod
    def enter(self) -> None:
        Logger.instance().on_practice_starts(self._owner, self.__practice_label)

    @abstractmethod
    def exit(self) -> None:
        Logger.instance().on_practice_ends(self._owner, self.__practice_label)

    @abstractmethod
    def has_ended(self) -> bool:
        pass


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
