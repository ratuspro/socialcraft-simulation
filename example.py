import datetime
import math
import random
from typing import Dict, List

from engine.agents import Agent, Context, MoveToLocation, Sleep
from engine.entities import Object
from engine.logger import Logger, LogType
from engine.world import Location, World


def show_report(agent: Agent):

    logger = Logger.instance()

    entered_actions = logger.get_action(subject=agent, action=LogType.ENTERED_LOCATION)

    print("")
    print(f"# Stats for {agent.name}:")
    print(f"## Number of different locations visited: {len(set([action.properties['location'] for action in entered_actions]))}")  # type: ignore
    print(f"## Number of locations visited: {len(entered_actions)}")  # type: ignore
    print("")


def sigmoid(x):
    if x >= 0:
        z = math.exp(-x)
        sig = 1 / (1 + z)
        return sig
    else:
        z = math.exp(x)
        sig = z / (1 + z)
        return sig


def weightedSalienceFunction(context: Context, weights: Dict[str, float]) -> float:
    features = context.get_all_features()
    if len(features) == 0:
        return 0
    sum = 0
    for label, value in features.items():
        weight = 0
        if label in weights:
            weight = weights[label]
        sum += sigmoid(value * weight)
    return sum / len(features)


def create_random_salience_vector(features: List[str]) -> Dict[str, float]:

    dict = {}
    for feature in features:
        dict[feature] = random.random() * 2 - 1
    return dict


if __name__ == "__main__":

    logger = Logger.instance()

    w1 = World(logger)

    # Add Locations
    house1 = Location("House1", min_time_inside=10)
    house2 = Location("House2", min_time_inside=10)
    house3 = Location("House3", min_time_inside=10)
    square = Location("Square", min_time_inside=50)
    path1 = Location("Path1", min_time_inside=1)
    path2 = Location("Path2", min_time_inside=2)
    path3 = Location("Path3", min_time_inside=2)
    workplace = Location("Workplace", min_time_inside=10)

    w1.register_location(house1)
    w1.register_location(house2)
    w1.register_location(house3)
    w1.register_location(workplace)
    w1.register_location(square)
    w1.register_location(path1)
    w1.register_location(path2)
    w1.register_location(path3)

    w1.register_location_connection(house1, path1)
    w1.register_location_connection(house2, path2)
    w1.register_location_connection(house3, path2)
    w1.register_location_connection(path1, square)
    w1.register_location_connection(path2, square)
    w1.register_location_connection(path3, square)
    w1.register_location_connection(path3, workplace)

    # Create Objects
    house1_bed = Object("Bed", labels=["BED"])
    house2_bed = Object("Bed", labels=["BED"])
    house3_bed = Object("Bed", labels=["BED"])

    w1.register_entity(house1_bed)
    w1.register_entity(house2_bed)
    w1.register_entity(house3_bed)

    w1.place_entity(house1_bed, house1)
    w1.place_entity(house2_bed, house2)
    w1.place_entity(house3_bed, house3)

    # Define Feature Vector
    features = []
    features.append("TIME_OF_DAY")
    features.append(f"AT_{house1.name}")
    features.append(f"AT_{house2.name}")
    features.append(f"AT_{house3.name}")
    features.append(f"AT_{square.name}")
    features.append(f"AT_{path1.name}")
    features.append(f"AT_{path2.name}")
    features.append(f"AT_{path3.name}")
    features.append(f"AT_{workplace.name}")

    # Create Agent 1
    agent_1 = Agent("A1")
    w1.register_agent(agent_1)
    w1.place_entity(agent_1, square)

    p1_move_to_home = MoveToLocation(
        owner=agent_1, world=w1, destination=house1, label="MoveToHome"
    )
    p1_move_to_home.set_salience_function(
        lambda context: weightedSalienceFunction(
            context, create_random_salience_vector(features)
        )
    )

    agent_1.add_practice(p1_move_to_home)

    p1_move_to_work = MoveToLocation(
        owner=agent_1, world=w1, destination=workplace, label="MoveToWork"
    )
    p1_move_to_work.set_salience_function(
        lambda context: weightedSalienceFunction(
            context, create_random_salience_vector(features)
        )
    )
    agent_1.add_practice(p1_move_to_work)

    p1_sleep = Sleep(owner=agent_1, world=w1)
    p1_sleep.set_salience_function(
        lambda context: weightedSalienceFunction(
            context, create_random_salience_vector(features)
        )
    )
    agent_1.add_practice(p1_sleep)

    # Create Agent 2
    agent_2 = Agent("A2")
    w1.register_agent(agent_2)
    w1.place_entity(agent_2, square)

    p2_move_to_home = MoveToLocation(
        owner=agent_2, world=w1, destination=house2, label="MoveToHome"
    )
    p2_move_to_home.set_salience_function(
        lambda context: weightedSalienceFunction(
            context, create_random_salience_vector(features)
        )
    )
    agent_2.add_practice(p2_move_to_home)

    p2_move_to_work = MoveToLocation(
        owner=agent_2, world=w1, destination=workplace, label="MoveToWork"
    )
    p2_move_to_work.set_salience_function(
        lambda context: weightedSalienceFunction(
            context, create_random_salience_vector(features)
        )
    )
    agent_2.add_practice(p2_move_to_work)

    p2_sleep = Sleep(owner=agent_2, world=w1)
    p2_sleep.set_salience_function(
        lambda context: weightedSalienceFunction(
            context, create_random_salience_vector(features)
        )
    )
    agent_2.add_practice(p2_sleep)

    # Simulate
    NUM_TICKS = 50000
    NUM_TICKS_TO_LOG_COMMIT = 1000

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

    print(delta.total_seconds())
    print(f"Total simulation took {total_miliseconds/1000} seconds")
    print(f"Average tick took {total_miliseconds/NUM_TICKS} miliseconds")

    show_report(agent_1)
    show_report(agent_2)

    # w1.show_entities()
