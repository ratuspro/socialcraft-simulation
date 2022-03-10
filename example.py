from engine.world import World, Location
from engine.agents import Agent, Context, MoveToLocation
from engine.logger import Logger, LogType
import datetime
import math
from typing import Dict


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
    sum = 0
    for label, value in features.items():
        sum += sigmoid(value * weights[label])
    return sum / len(features)


if __name__ == "__main__":

    logger = Logger.instance()

    w1 = World(logger)

    # Add Locations
    house1 = Location("House1", min_time_inside=0)
    house2 = Location("House2", min_time_inside=0)
    house3 = Location("House3", min_time_inside=0)
    square = Location("Square", min_time_inside=0)
    path1 = Location("Path1", min_time_inside=0)
    path2 = Location("Path2", min_time_inside=0)
    path3 = Location("Path3", min_time_inside=0)
    workplace = Location("Workplace", min_time_inside=0)

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

    # Add abstract concepts

    # Create Agent 1
    agent_1 = Agent("A1")
    w1.register_entity(agent_1)
    w1.place_entity(agent_1, square)

    p1_1 = MoveToLocation(
        owner=agent_1, world=w1, destination=house1, label="MoveToHome"
    )
    p1_1.set_salience_function(
        lambda context: weightedSalienceFunction(
            context,
            {
                "TIME_OF_DAY": 1,
                f"AT_{house1.name}": 0,
                f"AT_{house2.name}": 1,
                f"AT_{house3.name}": 1,
                f"AT_{square.name}": 1,
                f"AT_{path1.name}": 1,
                f"AT_{path2.name}": 1,
                f"AT_{path3.name}": 1,
                f"AT_{workplace.name}": 1,
            },
        )
    )
    agent_1.add_practice(p1_1)

    p1_2 = MoveToLocation(
        owner=agent_1, world=w1, destination=workplace, label="MoveToWork"
    )
    p1_2.set_salience_function(
        lambda context: weightedSalienceFunction(
            context,
            {
                "TIME_OF_DAY": 1,
                f"AT_{house1.name}": 1,
                f"AT_{house2.name}": 1,
                f"AT_{house3.name}": 1,
                f"AT_{square.name}": 1,
                f"AT_{path1.name}": 1,
                f"AT_{path2.name}": 1,
                f"AT_{path3.name}": 1,
                f"AT_{workplace.name}": 0,
            },
        )
    )
    agent_1.add_practice(p1_2)

    # Create Agent 2
    agent_2 = Agent("A2")
    w1.register_entity(agent_2)
    w1.place_entity(agent_2, square)

    p2_1 = MoveToLocation(
        owner=agent_2, world=w1, destination=house2, label="MoveToHome"
    )
    p2_1.set_salience_function(
        lambda context: weightedSalienceFunction(
            context,
            {
                "TIME_OF_DAY": 1,
                f"AT_{house1.name}": 1,
                f"AT_{house2.name}": 0,
                f"AT_{house3.name}": 1,
                f"AT_{square.name}": 1,
                f"AT_{path1.name}": 1,
                f"AT_{path2.name}": 1,
                f"AT_{path3.name}": 1,
                f"AT_{workplace.name}": 1,
            },
        )
    )
    agent_2.add_practice(p2_1)

    p2_2 = MoveToLocation(
        owner=agent_2, world=w1, destination=workplace, label="MoveToWork"
    )
    p2_2.set_salience_function(
        lambda context: weightedSalienceFunction(
            context,
            {
                "TIME_OF_DAY": 1,
                f"AT_{house1.name}": 1,
                f"AT_{house2.name}": 1,
                f"AT_{house3.name}": 1,
                f"AT_{square.name}": 1,
                f"AT_{path1.name}": 1,
                f"AT_{path2.name}": 1,
                f"AT_{path3.name}": 1,
                f"AT_{workplace.name}": 0,
            },
        )
    )
    agent_2.add_practice(p2_2)

    w1.plot_map()

    # Simulate
    NUM_TICKS = 20000
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
