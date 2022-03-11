from abc import ABC, abstractmethod
from typing import Callable

from ..agents import Agent, Context
from ..logger import Logger
from ..world import World


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
