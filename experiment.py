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
from engine.agents import Agent, ContextManager, MoveToLocation, context_manager


def register_data(agents: List[Agent]):

    practices = list(agents[0].get_practices_and_weights().keys())
    features = agents[0].context.get_expanded_features()

    field_names = []
    for practice in practices:
        for feature in features:
            field_names.append(f"{practice}_{feature}_weight")
            field_names.append(f"{practice}_{feature}_bias")
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
            for practice, weights in agent.get_practices_and_weights().items():
                for weight_label, weight_values in weights.items():
                    agent_dict[f"{practice}_{weight_label}_weight"] = weight_values[0]
                    agent_dict[f"{practice}_{weight_label}_bias"] = weight_values[1]

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


def create_base_agent(
    name: str,
    world: World,
    home: Location,
) -> Agent:

    context_manager = ContextManager()

    # Define Features
    context_manager.registerScalarFeature("Time")
    context_manager.registerCategoricalFeature(
        "CurrentLocation", [location for location in world.locations], False
    )
    context_manager.registerCategoricalFeature(
        "TargetLocation", [location for location in world.locations], True
    )

    # Define Weights
    context_manager.registerScalarFeatureWeights(
        "Time", numpy.random.uniform(0, 1), numpy.random.uniform(0, 1)
    )

    for location in world.locations:
        context_manager.registerCategorialFeatureWeights(
            "CurrentLocation",
            location,
            numpy.random.uniform(0, 1),
            numpy.random.uniform(0, 1),
        )

    for location in world.locations:
        context_manager.registerCategorialFeatureWeights(
            "TargetLocation",
            location,
            numpy.random.uniform(0, 1),
            numpy.random.uniform(0, 1),
        )

    agent = Agent(name, world, context_manager)
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
