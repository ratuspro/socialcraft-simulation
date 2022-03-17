import random
import datetime
from typing import Any

from engine.entities import Object
from engine.logger import Logger, LogType
from engine.world import Location, World
from engine.agents import Agent, ContextManager, MoveToLocation


def create_base_agent(
    name: str,
    world: World,
    home: Location,
    context_manager: ContextManager,
) -> Agent:
    agent = Agent(name, world, context_manager)
    world.register_entity(agent)
    world.place_entity(agent, home)

    weight_vector = {}
    possible_features = cm.get_expanded_features()

    for feature in possible_features:
        weight_vector[feature] = (random.random(), random.random())

    agent.set_weights(MoveToLocation, weight_vector)

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
        practice_label = str(practices[i * 2].properties)  # type: ignore
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
            f"## {practice:70} / occur: {num_occurences:5} / time: {total_time:5} / avg: {total_time/num_occurences:.5}"
        )


if __name__ == "__main__":

    logger = Logger.instance()

    w1 = World(logger)

    # Add Locations
    house1 = Location("House1", min_time_inside=10, is_path=False)
    house2 = Location("House2", min_time_inside=10, is_path=False)
    house3 = Location("House3", min_time_inside=10, is_path=False)
    square = Location("Square", min_time_inside=50, is_path=False)
    path1 = Location("Path1", min_time_inside=1, is_path=True)
    path2 = Location("Path2", min_time_inside=2, is_path=True)
    path3 = Location("Path3", min_time_inside=2, is_path=True)
    workplace = Location("Workplace", min_time_inside=10, is_path=False)

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

    # Define Context
    cm = ContextManager()
    cm.registerScalarFeature("Time")
    cm.registerCategoricalFeature(
        "CurrentLocation", [str(location) for location in w1.locations], False
    )
    cm.registerCategoricalFeature(
        "TargetLocation", [str(location) for location in w1.locations], True
    )

    # Create Agent 1
    agent_1 = create_base_agent(
        name="Agent 1", world=w1, home=house1, context_manager=cm
    )
    agent_2 = create_base_agent(
        name="Agent 2", world=w1, home=house2, context_manager=cm
    )

    agent_3 = create_base_agent(
        name="Agent 3", world=w1, home=house3, context_manager=cm
    )

    # Simulate
    NUM_TICKS = 24000
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

    print(f"Total simulation took {total_miliseconds/1000} seconds")
    print(f"Average tick took {total_miliseconds/NUM_TICKS} miliseconds")

    show_report(agent_1)
    show_report(agent_2)
    show_report(agent_3)
