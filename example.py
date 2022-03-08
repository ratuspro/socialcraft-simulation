from engine.entities import Time
from engine.world import World, Location
from engine.agents import Agent

if __name__ == "__main__":
    world = World()

    # Add abstract concepts
    general_time = Time()

    # Add agents
    agent_1 = Agent("A1")
    agent_2 = Agent("A2")
    agent_3 = Agent("A3")
    agent_4 = Agent("A4")

    world.register_updatable(general_time)
    world.register_updatable(agent_1)
    world.register_updatable(agent_2)
    world.register_updatable(agent_3)
    world.register_updatable(agent_4)

    # Add Locations
    house1 = Location("House1")
    house2 = Location("House2")
    house3 = Location("House3")
    square = Location("Square")
    path1 = Location("Path1")
    path2 = Location("Path2")

    world.register_location(house1)
    world.register_location(house2)
    world.register_location(house3)
    world.register_location(square)
    world.register_location(path1)
    world.register_location(path2)

    world.register_location_connection(house1, path1)
    world.register_location_connection(house2, path2)
    world.register_location_connection(house3, path2)
    world.register_location_connection(path1, square)
    world.register_location_connection(path2, square)

    for i in range(10):
        print("# New Tick:")
        world.tick()

        print("## Updatables:")
        world.show_updatables()
        
        print("## Locations:")
        world.show_locations()

    world.plot_map()
