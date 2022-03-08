from abc import abstractmethod, ABC
from typing import List
import networkx as nx
import matplotlib.pyplot as plt


class Updatable(ABC):
    @abstractmethod
    def tick(self) -> None:
        pass


class Location:
    __name: str

    def __init__(self, name: str) -> None:
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.__name


class World:

    __updatables: List[Updatable]
    __locations: List[Location]
    __locations_graph: nx.Graph

    def __init__(self) -> None:
        self.__updatables = []
        self.__locations = []
        self.__locations_graph = nx.Graph()

    def register_updatable(self, updatable: Updatable) -> None:
        if updatable in self.__updatables:
            raise Exception("Trying to register updatable already registered!")

        self.__updatables.append(updatable)

    def unregister_updatable(self, updatable: Updatable) -> None:
        if updatable not in self.__updatables:
            raise Exception("Trying to unregister updatable not registered!")

        self.__updatables.append(updatable)

    def show_updatables(self) -> None:
        for updatable in self.__updatables:
            print(updatable)

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

    def show_locations(self) -> None:
        for location in self.__locations:
            print(location)

    def plot_map(self) -> None:
        nx.draw(self.__locations_graph, with_labels=True)
        plt.show()

    def tick(self):
        for updatable in self.__updatables:
            updatable.tick()
