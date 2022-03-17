import random
import datetime
from typing import Any, Dict, List, Tuple, Any

from engine.entities import Object
from engine.logger import Logger, LogType
from engine.world import Location, World
from engine.agents import Agent


def create_base_agent(name: str, world: World, work: Location, home: Location) -> Agent:
    agent = Agent(name, world)

    return agent


def show_report(agent: Agent):

    logger = Logger.instance()

    entered_actions = logger.get_action(
        subject=agent, actions=[LogType.ENTERED_LOCATION]
    )

    print("")
    print(f"# Stats for {agent.name}:")
    print(f"## Number of different locations visited: {len(set([action.properties['location'] for action in entered_actions]))}")  # type: ignore
    print(f"## Number of locations visited: {len(entered_actions)}")  # type: ignore

    # Time per practice

    practices = logger.get_action(
        subject=agent, actions=[LogType.STARTED_PRACTICE, LogType.FINISHED_PRACTICE]
    )

    practice_log = []
    practices_available = set()
    for i in range(len(practices) // 2):
        practice_time = practices[i * 2 + 1].tick - practices[i * 2].tick
        practice_label = practices[i * 2 + 1].properties["label"]  # type: ignore
        practice_log.append((practice_label, practice_time))
        practices_available.add(practice_label)

    print(f"# Stats for {agent.name} practices:")
    for practice in practices_available:
        num_occurences = 0
        total_time = 0

        for log in practice_log:
            if log[0] == practice:
                num_occurences += 1
                total_time += log[1]

        print(
            f"## {practice:20} / occur: {num_occurences:5} / time: {total_time:5} / avg: {total_time/num_occurences:.5}"
        )


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

    # Create Agent 1
    agent_1 = create_base_agent(name="Agent 1", world=w1, work=workplace, home=house1)
    agent_2 = create_base_agent(name="Agent 2", world=w1, work=workplace, home=house2)

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

    show_report(agent_1)
    show_report(agent_2)
