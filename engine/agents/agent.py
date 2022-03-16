from __future__ import annotations
import random
from typing import Dict, List, Any

from ..entities import Entity


class Feature:
    __label: str
    __value: Any
    __salience: float

    def __init__(self, label: str, value: Any, salience: float) -> None:
        self.__label = label
        self.__value = value
        self.__salience = salience

    @property
    def label(self) -> str:
        return self.__label

    @property
    def value(self) -> Any:
        return self.__value

    @property
    def salience(self) -> float:
        return self.__salience


class Context:
    __features_by_label: Dict[str, List[Feature]]

    def __init__(self) -> None:
        self.__features_by_label = {}

    def add_feature(self, feature: Feature) -> None:
        if feature.label in self.__features_by_label.keys():
            self.__features_by_label[feature.label].append(feature)
        else:
            self.__features_by_label[feature.label] = [feature]

    def get_feature_by_label(self, label: str) -> List[Feature]:

        if label not in self.__features_by_label.keys():
            raise Exception("Getting feature with non-existent label.")

        return self.__features_by_label[label]

    def get_salience_of_feature_by_label_and_value(
        self, label: str, value: Any
    ) -> float:

        if label not in self.__features_by_label.keys():
            return 0

        features_with_label = self.__features_by_label[label]

        for feature in features_with_label:
            if feature.value == value:
                return feature.salience

        return 0

    def get_all_features(self) -> List[Feature]:
        all_features = []
        [
            all_features.extend(features)
            for _, features in self.__features_by_label.items()
        ]

        return all_features


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
