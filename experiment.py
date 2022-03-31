import csv
from datetime import datetime
import os
import random
from typing import List

import numpy

from engine.agents import Agent, ContextRegistry, MoveToLocation, WeightVector
from engine.agents.p_basic import Idle, Sleep
from engine.entities.object import Object
from engine.logger import Logger
from engine.world import Location, World

NUM_TICKS = 24000
NUM_TICKS_TO_LOG_COMMIT = 10000


def create_bed(name: str, world: World, location: Location) -> Object:
    bed = Object(name)
    bed.add_attribute("bed", True)
    bed.add_attribute("occupied", False)
    world.register_entity(bed)
    world.place_entity(bed, location)
    return bed


def create_random_weight_vector(context_registry: ContextRegistry) -> WeightVector:
    weight_vector = context_registry.createEmptyWeightVector()

    weight_vector.registerScalarFeatureWeights(
        "Time", numpy.random.uniform(-1, 1), numpy.random.uniform(-1, 1)
    )

    for location in context_registry.getFeatureValues("CurrentLocation"):
        weight_vector.registerCategorialFeatureWeights(
            "CurrentLocation",
            location,
            numpy.random.uniform(-1, 1),
            numpy.random.uniform(-1, 1),
        )

    for location in context_registry.getFeatureValues("TargetLocation"):
        weight_vector.registerCategorialFeatureWeights(
            "TargetLocation",
            location,
            numpy.random.uniform(-1, 1),
            numpy.random.uniform(-1, 1),
        )

    for entity in context_registry.getFeatureValues("TargetEntity"):
        weight_vector.registerCategorialFeatureWeights(
            "TargetEntity",
            entity,
            numpy.random.uniform(-1, 1),
            numpy.random.uniform(-1, 1),
        )

    weight_vector.registerScalarFeatureWeights(
        "NumberNearbyAgent", numpy.random.uniform(
            -1, 1), numpy.random.uniform(-1, 1)
    )

    return weight_vector


def create_base_agent(
    name: str,
    world: World,
    starting: Location,
) -> Agent:

    agent = Agent(name, world)
    world.register_entity(agent)
    world.place_entity(agent, starting)
    return agent


def add_random_weights_to_practices(agent: Agent, context: ContextRegistry) -> None:
    agent.add_weight_vector(
        MoveToLocation, create_random_weight_vector(context))

    agent.add_weight_vector(Sleep, create_random_weight_vector(context))

    agent.add_weight_vector(Idle, create_random_weight_vector(context))


def run_world(logs_path: str):

    Logger.set_file_path(path=logs_path)
    logger = Logger.instance()

    w1 = World(logger)

    # Add Locations
    house1 = Location("House1", min_time_inside=10, is_path=False)
    house2 = Location("House2", min_time_inside=10, is_path=False)
    house3 = Location("House3", min_time_inside=10, is_path=False)
    house4 = Location("House4", min_time_inside=8, is_path=False)
    square = Location("Square", min_time_inside=50, is_path=False)
    path1 = Location("Path1", min_time_inside=1, is_path=True)
    path2 = Location("Path2", min_time_inside=2, is_path=True)
    path3 = Location("Path3", min_time_inside=2, is_path=True)
    path4 = Location("Path4", min_time_inside=5, is_path=True)
    path5 = Location("Path5", min_time_inside=10, is_path=True)
    workplace1 = Location("Workplace 1", min_time_inside=10, is_path=False)
    workplace2 = Location("Workplace 2", min_time_inside=10, is_path=False)

    w1.register_location(house1)
    w1.register_location(house2)
    w1.register_location(house3)
    w1.register_location(house4)
    w1.register_location(workplace1)
    w1.register_location(workplace2)
    w1.register_location(square)
    w1.register_location(path1)
    w1.register_location(path2)
    w1.register_location(path3)
    w1.register_location(path4)
    w1.register_location(path5)

    w1.register_location_connection(house1, path1)
    w1.register_location_connection(house2, path2)
    w1.register_location_connection(house3, path2)
    w1.register_location_connection(path1, square)
    w1.register_location_connection(path2, square)
    w1.register_location_connection(path3, square)
    w1.register_location_connection(path3, path4)
    w1.register_location_connection(path4, house4)
    w1.register_location_connection(path3, workplace1)
    w1.register_location_connection(path5, square)
    w1.register_location_connection(path5, workplace2)

    # Create Beds
    create_bed("Bed 1", w1, house1)
    create_bed("Bed 2", w1, house2)
    create_bed("Bed 3", w1, house3)
    create_bed("Bed 4", w1, house4)
    create_bed("Bed 5", w1, house3)
    create_bed("Bed 6", w1, house4)
    create_bed("Bed 7", w1, house2)
    create_bed("Bed 8", w1, house2)
    create_bed("Bed 9", w1, house1)

    # Create Agent 1
    agent_1 = create_base_agent(name="Agent1", world=w1, starting=house1)
    agent_2 = create_base_agent(name="Agent2", world=w1, starting=house2)
    agent_3 = create_base_agent(name="Agent3", world=w1, starting=house3)
    agent_4 = create_base_agent(name="Agent4", world=w1, starting=house4)
    agent_5 = create_base_agent(name="Agent5", world=w1, starting=house1)
    agent_6 = create_base_agent(name="Agent6", world=w1, starting=house1)
    agent_7 = create_base_agent(name="Agent7", world=w1, starting=house2)
    agent_8 = create_base_agent(name="Agent8", world=w1, starting=house3)
    agent_9 = create_base_agent(name="Agent9", world=w1, starting=house3)
    agents = [agent_1, agent_2, agent_3, agent_4,
              agent_5, agent_6, agent_7, agent_8, agent_9]

    # Define Features
    context_registry = ContextRegistry()
    context_registry.registerScalarFeature("Time")
    context_registry.registerScalarFeature("NumberNearbyAgent")
    context_registry.registerCategoricalFeature(
        "CurrentLocation", w1.locations
    )
    context_registry.registerCategoricalFeature(
        "TargetLocation", w1.locations
    )
    context_registry.registerCategoricalFeature(
        "TargetEntity", w1.entities
    )

    add_random_weights_to_practices(agent_1, context_registry)
    add_random_weights_to_practices(agent_2, context_registry)
    add_random_weights_to_practices(agent_3, context_registry)
    add_random_weights_to_practices(agent_4, context_registry)
    add_random_weights_to_practices(agent_5, context_registry)
    add_random_weights_to_practices(agent_6, context_registry)
    add_random_weights_to_practices(agent_7, context_registry)
    add_random_weights_to_practices(agent_8, context_registry)
    add_random_weights_to_practices(agent_9, context_registry)

    # w1.plot_map()

    # Simulate
    print("Starting Simulation...")
    start = datetime.datetime.now()
    for i in range(NUM_TICKS):
        w1.tick()
        logger.set_tick(w1.time)
        if i % NUM_TICKS_TO_LOG_COMMIT == 0:
            logger.commit()
    logger.commit()
    print("Simulation ended")

    end = datetime.datetime.now()
    delta = end - start
    total_miliseconds = delta.total_seconds() * 1000 + delta.microseconds / 1000

    print(f"Total simulation took {total_miliseconds/1000} seconds")
    print(f"Average tick took {total_miliseconds/NUM_TICKS} miliseconds")


if __name__ == "__main__":

    while True:
        run_world(
            f"logs/{ datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}_{random.randint(0,9999)}.db")
