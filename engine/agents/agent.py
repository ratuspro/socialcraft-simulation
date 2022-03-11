from __future__ import annotations
import random
from typing import Dict, List, Any

from ..entities import Entity


class Context:
    __features: Dict[str, float]

    def __init__(self) -> None:
        self.__features = {}

    def add_feature(self, label: str, value: float) -> None:
        self.__features[label] = value

    def get_feature(self, label: str) -> float:
        if label not in self.__features.keys():
            raise Exception("Getting feature with non-existent label.")

        return self.__features[label]

    def get_all_features(self) -> Dict[str, float]:
        return self.__features


class Agent(Entity):
    __name: str
    __practices: List
    __current_practice: Any
    __context: Context

    def __init__(self, name: str) -> None:
        super().__init__()
        self.__name = name
        self.__practices = []
        self.__current_practice = None
        self.__context = Context()

    def set_context(self, context: Context) -> None:
        self.__context = context

    @property
    def context(self) -> Context:
        return self.__context

    @property
    def name(self) -> str:
        return self.__name

    def add_practice(self, new_practice) -> None:
        self.__practices.append(new_practice)

    def __get_best_practices(self) -> List:
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
