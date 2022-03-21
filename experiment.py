from cProfile import run
from concurrent.futures import thread
from contextlib import contextmanager
from contextvars import Context
import _thread
from matplotlib.style import context
import numpy
import datetime
import csv
from typing import List
import os
from engine.logger import Logger, LogType
from engine.world import Location, World
from engine.agents import Agent, ContextRegistry, MoveToLocation, WeightVector


def register_data(agents: List[Agent]):

    field_names = []

    # Get all (practice, weight)
    for practice, weights in agents[0].get_practice_and_weights().items():

        for feature_label, _ in weights.get_scalar_features().items():
            field_names.append(f"{practice.label}_{feature_label}_weight")
            field_names.append(f"{practice.label}_{feature_label}_bias")
        for feature_label, _ in weights.get_categorical_features().items():
            field_names.append(
                f"{practice.label}_{feature_label[0]}_{feature_label[1]}_weight"
            )
            field_names.append(
                f"{practice.label}_{feature_label[0]}_{feature_label[1]}_bias"
            )

        field_names.append("distance_travelled")
        field_names.append("number_places_visited")
        field_names.append("number_of_destination")

    filename = "data.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=field_names)

        if not file_exists:
            writer.writeheader()

        for agent in agents:
            agent_dict = {}

            # Practice Weight Vector
            for practice, weights in agent.get_practice_and_weights().items():
                for (
                    feature_label,
                    feature_weight,
                ) in weights.get_scalar_features().items():
                    agent_dict[
                        f"{practice.label}_{feature_label}_weight"
                    ] = feature_weight.weight
                    agent_dict[
                        f"{practice.label}_{feature_label}_bias"
                    ] = feature_weight.bias
                for (
                    feature_label,
                    feature_weight,
                ) in weights.get_categorical_features().items():
                    agent_dict[
                        f"{practice.label}_{feature_label[0]}_{feature_label[1]}_weight"
                    ] = feature_weight.weight
                    agent_dict[
                        f"{practice.label}_{feature_label[0]}_{feature_label[1]}_bias"
                    ] = feature_weight.bias

            entered_actions = Logger.instance().get_action(
                subject=agent, actions=[LogType.ENTERED_LOCATION]
            )

            practice_start_action = Logger.instance().get_action(
                subject=agent, actions=[LogType.STARTED_PRACTICE]
            )

            agent_dict["distance_travelled"] = len(set([action.properties["location"] for action in entered_actions]))  # type: ignore
            agent_dict["number_places_visited"] = len(entered_actions)

            moveToLocationPractices = filter(lambda action: action.properties["label"] == "MoveToLocation", practice_start_action)  # type: ignore

            agent_dict["number_of_destination"] = len(set([action.properties["destination"] for action in moveToLocationPractices]))  # type: ignore
            writer.writerow(agent_dict)


def create_random_weight_vector(context_registry: ContextRegistry) -> WeightVector:
    weight_vector = context_registry.createEmptyWeightVector()

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

    return weight_vector


def create_base_agent(
    name: str,
    world: World,
    home: Location,
) -> Agent:

    context_registry = ContextRegistry()

    # Define Features
    context_registry.registerScalarFeature("Time")
    context_registry.registerCategoricalFeature(
        "CurrentLocation", [location for location in world.locations]
    )
    context_registry.registerCategoricalFeature(
        "TargetLocation", [location for location in world.locations]
    )

    agent = Agent(name, world)
    agent.add_weight_vector(
        MoveToLocation, create_random_weight_vector(context_registry)
    )
    world.register_entity(agent)
    world.place_entity(agent, home)
    return agent


def run_world():

    logger = Logger.instance()
    logger.new_run()

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

    # Create Agent 1
    agent_1 = create_base_agent(name="Agent 1", world=w1, home=house1)
    agent_2 = create_base_agent(name="Agent 2", world=w1, home=house2)
    agent_3 = create_base_agent(name="Agent 3", world=w1, home=house3)
    agent_4 = create_base_agent(name="Agent 4", world=w1, home=house4)
    agent_5 = create_base_agent(name="Agent 5", world=w1, home=house1)
    agent_6 = create_base_agent(name="Agent 6", world=w1, home=house1)
    agent_7 = create_base_agent(name="Agent 7", world=w1, home=house2)
    agent_8 = create_base_agent(name="Agent 8", world=w1, home=house3)
    agent_9 = create_base_agent(name="Agent 9", world=w1, home=house3)

    # w1.plot_map()

    # Simulate
    NUM_TICKS = 24000
    NUM_TICKS_TO_LOG_COMMIT = 10000

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

    register_data(
        [
            agent_1,
            agent_2,
            agent_3,
            agent_4,
            agent_5,
            agent_6,
            agent_7,
            agent_8,
            agent_9,
        ],
    )


if __name__ == "__main__":

    while True:
        run_world()
