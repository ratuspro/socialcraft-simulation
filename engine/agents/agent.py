from __future__ import annotations

from utils import DependencyManager

from ..logger import Logger
from typing import Dict, Type
from engine.agents.context_registry import WeightVector
from engine.agents.practice import Practice
from ..entities import Entity, Object
from ..world import World
from .p_movement import MoveToLocation
from .p_basic import Sleep, Idle

import numpy
import math


def softmax(x, exp_sum):
    return math.exp(x) / exp_sum


class Agent(Entity):
    def __init__(self, name: str, world: World) -> None:
        self.__name: str = name
        self.__world: World = world
        self.__current_practice = None
        self.__weight_vector_by_practice: Dict[Type[Practice], WeightVector] = {}

    @property
    def name(self):
        return self.__name

    @property
    def world(self):
        return self.__world

    def __str__(self) -> str:
        return f"{self.__name}"

    def add_weight_vector(
        self, practice_type: Type, weight_vector: WeightVector
    ) -> None:
        self.__weight_vector_by_practice[practice_type] = weight_vector

        serialized_vector = {}
        for (
            feature_label,
            feature_weight,
        ) in weight_vector.get_scalar_features().items():
            serialized_vector[
                f"{practice_type.label}_{feature_label}_weight"
            ] = feature_weight.weight
            serialized_vector[
                f"{practice_type.label}_{feature_label}_bias"
            ] = feature_weight.bias
        for (
            feature_label,
            feature_weight,
        ) in weight_vector.get_categorical_features().items():
            serialized_vector[
                f"{practice_type.label}_{feature_label[0]}_{feature_label[1]}_weight"
            ] = feature_weight.weight
            serialized_vector[
                f"{practice_type.label}_{feature_label[0]}_{feature_label[1]}_bias"
            ] = feature_weight.bias

        DependencyManager.instance().get_logger().register_entry(-1, Logger.EntryType.SALIENCEVECTOR, self, {'practice_label': practice_type.label, 'practice_weight_vector':serialized_vector})

    def get_practice_and_weights(self) -> Dict[Type[Practice], WeightVector]:
        return self.__weight_vector_by_practice

    def tick(self) -> None:

        # Inspect the world
        day_time = (self.__world.time % 24000) / 24000
        current_location = self.__world.get_entity_location(self)
        if current_location is None:
            raise Exception("Agent not yet placed in the world")

        world_locations = self.__world.locations

        # Generate the practices
        practices = []

        ## Generate Idle
        practices.append(Idle(self, self.__world, 5))

        ## Generate moving to practices
        for location in world_locations:
            if location != current_location and not location.is_path:
                practices.append(MoveToLocation(self, self.__world, location))

        ## Generate sleeping practice
        for entity in self.__world.get_entities_at_location(self, current_location):
            if (
                isinstance(entity, Object)
                and "bed" in entity.attributes
                and "occupied" in entity.attributes
                and not entity.attributes["occupied"]
            ):
                practices.append(Sleep(self, self.__world, entity, 2000))

        ## Generate Context
        features = {} 
        features["Time"] = day_time
        features["CurrentLocation"] = current_location
        features["NumberNearbyAgent"] = len(list(filter(lambda entity: isinstance(entity, Agent), self.__world.get_entities_at_location(self, current_location))))

        if self.__current_practice is not None:
            if self.__current_practice.has_ended():
                self.__current_practice.exit()
                self.__current_practice = None
            else:
                self.__current_practice.tick()
        else:

            practice_saliences = {}

            for practice in practices:
                features["TargetEntity"] = practice.targetEntity()
                features["TargetLocation"] = practice.targetLocation()
                weight_vector = self.__weight_vector_by_practice[type(practice)]
                practice_saliences[practice] = weight_vector.calculate_salience(
                    features
                )

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
