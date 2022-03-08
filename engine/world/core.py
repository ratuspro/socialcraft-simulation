from abc import abstractmethod, ABC
from shutil import ExecError
from typing import List, Dict
import networkx as nx
import matplotlib.pyplot as plt


class Entity(ABC):
    @abstractmethod
    def tick(self) -> None:
        pass


class Location:
    __name: str
    __min_time_inside: int

    def __init__(self, name: str, min_time_inside: int) -> None:
        self.__name = name
        self.__min_time_inside = min_time_inside

    @property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"Location - {self.__name}"

    def min_time_inside(self) -> int:
        return self.__min_time_inside


class World:

    __entities: List[Entity]
    __locations: List[Location]
    __locations_graph: nx.Graph
    __entity_locations: Dict[Entity, Location]

    def __init__(self) -> None:
        self.__entities = []
        self.__locations = []
        self.__entity_locations = {}
        self.__locations_graph = nx.Graph()

    def register_entity(self, entity: Entity) -> None:
        if entity in self.__entities:
            raise Exception("Trying to register entity already registered!")

        self.__entities.append(entity)

    def unregister_entity(self, entity: Entity) -> None:
        if entity not in self.__entities:
            raise Exception("Trying to unregister entity not registered!")

        self.__entities.append(entity)

    def show_entities(self) -> None:
        for entity in self.__entities:
            print(entity)

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

    def place_entity(self, entity: Entity, location: Location) -> None:
        if entity not in self.__entities:
            raise Exception("Placing entity not yet registered...")

        if location not in self.__locations:
            raise Exception("Placing entity on location not yet registered...")

        self.__entity_locations[entity] = location

    def get_entity_location(self, entity: Entity) -> Location:
        if entity not in self.__entities:
            raise Exception("Getting location of entity not yet registered...")

        if entity not in self.__entity_locations:
            raise Exception("Getting location of entity not yet placed...")

        return self.__entity_locations[entity]

    def get_path_to(self, origin: Location, destination: Location) -> List[Location]:
        path = nx.astar_path(self.__locations_graph, origin, destination)
        return path

    def move_entity_to_location(self, entity: Entity, destination: Location) -> None:
        agent_location = self.get_entity_location(entity)

        if agent_location is None:
            raise Exception("Trying to move entity before placing it in the world")

        if destination not in self.__locations_graph.adj[agent_location]:
            raise Exception("Trying to move to location not adjacent")

        self.__entity_locations[entity] = destination

    def show_locations(self) -> None:

        location_entities = {}
        for location in self.__locations:
            location_entities[location] = []

        for entity, location in self.__entity_locations.items():
            location_entities[location].append(entity)

        for location in self.__locations:
            print(location)
            entities_string = "".join(
                [str(f"{entity}, ") for entity in location_entities[location]]
            ).removesuffix(", ")
            print(f" ^-> Entities [{entities_string}]")

    def plot_map(self) -> None:
        nx.draw(self.__locations_graph, with_labels=True)
        plt.show()

    def tick(self):
        for entity in self.__entities:
            entity.tick()
