from __future__ import annotations
from ..logger import Logger
from typing import Dict, Tuple, Type
from engine.agents.context_manager import ContextManager
from engine.agents.practice import Practice
from ..entities import Entity
from ..world import World
from .p_movement import MoveToLocation
import random
import math


def sigmoid(input):
    return 1 / (1 + math.exp(-input))


def calculate_salience(
    feature_vector: Dict[str, float], weights_vector: Dict[str, Tuple[float, float]]
) -> float:
    sum = 0
    for label, weight in weights_vector.items():
        value = 0
        if label in feature_vector:
            value = feature_vector[label]

        sum += value * weight[0]  # + weight[1]
    return sigmoid(sum)


class Agent(Entity):
    def __init__(
        self, name: str, world: World, context_manager: ContextManager
    ) -> None:
        self.__name: str = name
        self.__world: World = world
        self.__current_practice = None
        self.__context_manager: ContextManager = context_manager
        self.__weights_per_practice_type: Dict[
            Type[Practice], Dict[str, Tuple[float, float]]
        ] = {}

    @property
    def name(self):
        return self.__name

    @property
    def world(self):
        return self.__world

    def __str__(self) -> str:
        return f"{self.__name}"

    def set_weights(
        self, pratice_type: Type[Practice], weigths: Dict[str, Tuple[float, float]]
    ):
        self.__weights_per_practice_type[pratice_type] = weigths
        Logger.instance().log_salience_vecotr(self, pratice_type, weigths)

    def tick(self) -> None:

        # Inspect the world
        day_time = (self.__world.time % 24000) / 24000
        current_location = self.__world.get_entity_location(self)
        world_locations = self.__world.locations

        # Generate the practices
        practices = []

        ## Generate moving to practices
        for location in world_locations:
            if location != current_location and not location.is_path:
                practices.append(MoveToLocation(self, self.__world, location))

        ## Generate Context
        features = {}
        features["Time"] = day_time
        features["CurrentLocation"] = str(current_location)

        if self.__current_practice is not None:
            if self.__current_practice.has_ended():
                self.__current_practice.exit()
                self.__current_practice = None
            else:
                self.__current_practice.tick()
        else:

            best_salience, best_practices = -1, []

            # print(self.name)
            for practice in practices:

                features["TargetLocation"] = str(practice.targetLocation())
                vector = self.__context_manager.create_feature_vector(features)

                salience = calculate_salience(
                    vector, self.__weights_per_practice_type[type(practice)]
                )

                # print(f"{features} => {salience}")

                if salience > best_salience:
                    best_salience = salience
                    best_practices = [practice]
                elif salience == best_salience:
                    best_practices.append(practice)
            # input()
            new_practice = random.choice(best_practices)
            if new_practice is not None:
                self.__current_practice = new_practice
                self.__current_practice.enter()
