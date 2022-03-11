from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx

from ..agents import Agent, Context
from ..entities import Entity
from .location import Location


class EntityDetails:
    location: Optional[Location]
    time_since_last_movement: int

    def __init__(self) -> None:
        self.location = None
        self.time_since_last_movement = 0

    def reset_timer(self) -> None:
        self.time_since_last_movement = 0


class World:
    __agents: List[Agent]
    __entities: List[Entity]
    __locations: List[Location]
    __locations_graph: nx.Graph
    __entity_details: Dict[Entity, EntityDetails]
    __time: int

    def __init__(self, logger) -> None:
        self.__entities = []
        self.__agents = []
        self.__locations = []
        self.__entity_details = {}
        self.__locations_graph = nx.Graph()
        self.__time = 0
        self.__logger = logger

    # Agent Management

    def register_agent(self, agent: Agent) -> None:

        if agent in self.__agents:
            raise Exception("Trying to register agent already registered!")

        self.register_entity(agent)
        self.__agents.append(agent)

    def unregister_agent(self, agent: Agent) -> None:
        if agent not in self.__agents:
            raise Exception("Trying to unregister agent not registered!")

        self.unregister_entity(agent)
        self.__agents.remove(agent)

    # Entity Management

    def register_entity(self, entity: Entity) -> None:
        if entity in self.__entities:
            raise Exception("Trying to register entity already registered!")

        self.__entities.append(entity)
        self.__entity_details[entity] = EntityDetails()

    def unregister_entity(self, entity: Entity) -> None:
        if entity not in self.__entities:
            raise Exception("Trying to unregister entity not registered!")

        self.__entities.remove(entity)
        self.__entity_details.pop(entity)

    def show_entities(self) -> None:
        for entity in self.__entities:
            print(entity)

    def get_time_since_last_movement(self, entity: Entity) -> int:
        return self.__entity_details[entity].time_since_last_movement

    # Location Management

    def register_location(self, location: Location) -> None:
        if location in self.__locations:
            raise Exception("Trying to register location already registered!")

        self.__locations.append(location)
        self.__locations_graph.add_node(location)

    def unregister_location(self, location: Location) -> None:
        if location not in self.__locations:
            raise Exception("Trying to unregister location not registered!")

        self.__locations.append(location)
        self.__locations_graph.remove_node(location)

    def register_location_connection(
        self, locationS: Location, locationT: Location
    ) -> None:
        if locationS not in self.__locations:
            raise Exception(
                f"Trying to connect location {locationS} not previously registered!"
            )

        if locationT not in self.__locations:
            raise Exception(
                f"Trying to connect location {locationT} not previously registered!"
            )

        self.__locations_graph.add_edge(locationS, locationT)

    def unregister_location_connection(
        self, locationS: Location, locationT: Location
    ) -> None:

        if not self.__locations_graph.has_edge(locationS, locationT):
            raise Exception(
                f"Trying to disconnect locations {locationS} and {locationT} not previously connect!"
            )

        self.__locations_graph.remove_edge(locationS, locationT)

    # Movement

    def place_entity(self, entity: Entity, location: Location) -> None:
        if entity not in self.__entities:
            raise Exception("Placing entity not yet registered...")

        if location not in self.__locations:
            raise Exception("Placing entity on location not yet registered...")

        self.__entity_details[entity].location = location
        self.__entity_details[entity].reset_timer()

        self.__logger.on_entity_entered(entity, location)

    def get_entity_location(self, entity: Entity) -> Location | None:
        if entity not in self.__entities:
            raise Exception("Getting location of entity not yet registered...")

        if entity not in self.__entity_details:
            raise Exception("Getting location of entity not yet placed...")

        return self.__entity_details[entity].location

    def get_path_to(self, origin: Location, destination: Location) -> List[Location]:
        path = nx.astar_path(self.__locations_graph, origin, destination)
        return path

    def move_entity_to_location(self, entity: Entity, destination: Location) -> None:
        agent_location = self.get_entity_location(entity)

        if agent_location is None:
            raise Exception("Trying to move entity before placing it in the world")

        if destination not in self.__locations_graph.adj[agent_location]:
            raise Exception("Trying to move to location not adjacent")

        time = self.get_time_since_last_movement(entity)

        if time < agent_location.min_time_inside:
            raise Exception(
                "Attempting to move before spending the minimum time inside a location"
            )

        self.__entity_details[entity].location = destination
        self.__entity_details[entity].reset_timer()

        self.__logger.on_entity_entered(entity, destination)

    def show_locations(self) -> None:

        location_entities = {}
        for location in self.__locations:
            location_entities[location] = []

        for entity, entity_etails in self.__entity_details.items():
            location_entities[entity_etails.location].append(entity)

        for location in self.__locations:
            print(location)
            entities_string = "".join(
                [str(f"{entity}, ") for entity in location_entities[location]]
            ).removesuffix(", ")
            print(f" ^-> Entities [{entities_string}]")

    # Utilities

    def plot_map(self) -> None:
        nx.draw(self.__locations_graph, with_labels=True)
        plt.show()

    # Time Management

    @property
    def time(self) -> int:
        return self.__time

    def tick(self):
        self.__time += 1

        for agent in self.__agents:
            location = self.get_entity_location(agent)

            context = Context()
            context.add_feature("TIME_OF_DAY", self.__time % 24000)

            if location is not None:
                context.add_feature(f"AT_{location.name}", 1)

            agent.set_context(context)

        for entity in self.__entities:
            self.__entity_details[entity].time_since_last_movement += 1
            entity.tick()
