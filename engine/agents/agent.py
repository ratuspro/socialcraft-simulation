from __future__ import annotations
from ..logger import Logger
from typing import Dict, Tuple, Type
from engine.agents.context_manager import ContextManager
from engine.agents.practice import Practice
from ..entities import Entity
from ..world import World
from .p_movement import MoveToLocation
import numpy
import math


def softmax(x, exp_sum):
    return math.exp(x) / exp_sum


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

    @property
    def context(self):
        return self.__context_manager

    def __str__(self) -> str:
        return f"{self.__name}"

    def get_practices_and_weights(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        practices_and_weights = {}

        for practice, weights in self.__weights_per_practice_type.items():
            practices_and_weights[practice.__name__] = weights

        return practices_and_weights

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
        features["CurrentLocation"] = current_location

        if self.__current_practice is not None:
            if self.__current_practice.has_ended():
                self.__current_practice.exit()
                self.__current_practice = None
            else:
                self.__current_practice.tick()
        else:

            best_salience, best_practices = -1, []

            practice_saliences = {}

            for practice in practices:
                features["TargetLocation"] = practice.targetLocation()
                practice_saliences[
                    practice
                ] = self.__context_manager.calculate_salience(features)

            sum_saliences = sum(
                [math.exp(value) for value in practice_saliences.values()]
            )

            for practice in practice_saliences.keys():
                practice_saliences[practice] = softmax(
                    practice_saliences[practice], sum_saliences
                )

            selected_practice = numpy.random.choice(
                list(practice_saliences.keys()), p=list(practice_saliences.values())
            )

            if selected_practice is not None:
                self.__current_practice = selected_practice
                self.__current_practice.enter()
