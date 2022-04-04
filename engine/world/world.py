
from typing import Dict, List, Optional, Any

import matplotlib.pyplot as plt
import networkx as nx

from utils.dependency_manager import DependencyManager
from ..logger import Logger
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
    def __init__(self) -> None:
        self.__entities: List[Entity] = []
        self.__locations: List[Location] = []
        self.__entity_details: Dict[Entity, EntityDetails] = {}
        self.__locations_graph: nx.Graph = nx.Graph()
        self.__time: int = 0
        self.__logger : Logger = DependencyManager.instance().get_logger()

    # Entity Management
    @property
    def entities(self) -> List[Entity]:
        return self.__entities

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

    def change_entity_attribute(
        self, actor: Entity, target: Entity, label: str, value: Any
    ) -> None:
        actor_location = self.get_entity_location(actor)
        target_location = self.get_entity_location(target)

        if target_location is None:
            raise Exception(
                "Trying to change entity label before placing it in the world"
            )

        if actor_location is None:
            raise Exception(
                "Actor trying to change entity label not yet placed in the world"
            )

        if target_location != actor_location:
            raise Exception(
                "Trying to change entity when actor is not in the same location..."
            )

        target.add_attribute(label, value)

    def get_entity_attribute(self, actor: Entity, target: Entity, label: str) -> Any:
        actor_location = self.get_entity_location(actor)
        target_location = self.get_entity_location(target)

        if target_location is None:
            raise Exception(
                "Trying to get entity attribute before placing it in the world"
            )

        if actor_location is None:
            raise Exception(
                "Actor trying to get entity attribute not yet placed in the world"
            )

        if target_location != actor_location:
            raise Exception(
                "Trying to get entity when actor is not in the same location..."
            )

        if label in target.attributes:
            return target.attributes[label]
        else:
            return None

    # Location Management

    @property
    def locations(self) -> List[Location]:
        return self.__locations

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

        self.__logger.register_entry(self.time, Logger.A_ENTITYENTERSLOCATION, entity, {"destination":location.name})

    def get_entity_location(self, entity: Entity) -> Optional[Location]:
        if entity not in self.__entities:
            raise Exception("Getting location of entity not yet registered...")

        if entity not in self.__entity_details:
            raise Exception("Getting location of entity not yet placed...")

        return self.__entity_details[entity].location

    def get_path_to(self, origin: Location, destination: Location) -> List[Location]:
        path = nx.astar_path(self.__locations_graph, origin, destination)
        return path

    def move_entity_to_location(self, entity: Entity, destination: Location) -> None:
        entity_location = self.get_entity_location(entity)

        if entity_location is None:
            raise Exception("Trying to move entity before placing it in the world")

        if destination not in self.__locations_graph.adj[entity_location]:
            raise Exception("Trying to move to location not adjacent")

        time = self.get_time_since_last_movement(entity)

        if time < entity_location.min_time_inside:
            raise Exception(
                "Attempting to move before spending the minimum time inside a location"
            )

        self.__entity_details[entity].location = destination
        self.__entity_details[entity].reset_timer()

        self.__logger.register_entry(self.time, Logger.A_ENTITYENTERSLOCATION, entity, {"destination":destination.name})

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

    # Entity Management

    def get_entities_at_location(
        self, perceiver: Entity, location: Location
    ) -> List[Entity]:

        actor_location = self.get_entity_location(perceiver)

        if actor_location is None:
            raise Exception("Actor trying to perceive before placing it in the world")

        if actor_location != location:
            raise Exception("Trying to perceive location not currently in.")

        entities = []

        for entity, details in self.__entity_details.items():
            if details.location == location:
                entities.append(entity)

        return entities

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

        entities_per_location = {}
        for entity, details in self.__entity_details.items():
            if details.location not in entities_per_location:
                entities_per_location[details.location] = [entity]
            else:
                entities_per_location[details.location].append(entity)

        for entity in self.__entities:
            self.__entity_details[entity].time_since_last_movement += 1
            entity.tick()
