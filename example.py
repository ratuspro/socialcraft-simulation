from engine.entities import Time
from engine.world import World, Location
from engine.agents import Agent, Context, MoveToLocation


def weightedSalienceFunction(context: Context) -> float:
    return 1


if __name__ == "__main__":
    w1 = World()

    # Add Locations
    house1 = Location("House1", min_time_inside=0)
    house2 = Location("House2", min_time_inside=0)
    house3 = Location("House3", min_time_inside=0)
    square = Location("Square", min_time_inside=0)
    path1 = Location("Path1", min_time_inside=0)
    path2 = Location("Path2", min_time_inside=0)

    w1.register_location(house1)
    w1.register_location(house2)
    w1.register_location(house3)
    w1.register_location(square)
    w1.register_location(path1)
    w1.register_location(path2)

    w1.register_location_connection(house1, path1)
    w1.register_location_connection(house2, path2)
    w1.register_location_connection(house3, path2)
    w1.register_location_connection(path1, square)
    w1.register_location_connection(path2, square)

    # Add abstract concepts
    general_time = Time()
    w1.register_entity(general_time)

    # Create Agent 1
    agent_1 = Agent("A1")
    w1.register_entity(agent_1)
    w1.place_entity(agent_1, square)

    p1_1 = MoveToLocation(owner=agent_1, world=w1, destination=house1)
    p1_1.set_salience_function(weightedSalienceFunction)
    agent_1.add_practice(p1_1)

    p1_2 = MoveToLocation(owner=agent_1, world=w1, destination=house3)
    p1_2.set_salience_function(weightedSalienceFunction)
    agent_1.add_practice(p1_2)

    # Create Agent 2
    agent_2 = Agent("A2")
    w1.register_entity(agent_2)
    w1.place_entity(agent_2, square)

    p2_1 = MoveToLocation(owner=agent_2, world=w1, destination=house2)
    p2_1.set_salience_function(weightedSalienceFunction)
    agent_2.add_practice(p2_1)

    p2_2 = MoveToLocation(owner=agent_2, world=w1, destination=house3)
    p2_2.set_salience_function(weightedSalienceFunction)
    agent_2.add_practice(p2_2)

    # Simulate
    for i in range(24000):
        #print("")
        #print(f"Tick {i}")
        w1.tick()

        # w1.show_locations()

    # w1.show_entities()
    # w1.plot_map()
