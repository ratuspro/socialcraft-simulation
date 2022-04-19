from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from engine.logger.logger import Logger
from tinydb import Query
from typing import Dict, Any, List, Set, Tuple
from datetime import datetime
import random
import csv
import statistics

@dataclass
class LogEntry:
    tick: int
    type: str
    subtype: str
    properties: Dict[str, Any]

class Metric(ABC):
    @abstractmethod
    def new_entry(self, new_entry: LogEntry) -> None:
        pass
    
    @abstractmethod
    def stats(self) -> Dict[str, float]:
        pass

class LocationsVisited(Metric):
    def __init__(self, agents: Set[str] ) -> None:
        self.__agents_names = agents
        self.__agents_locations_visited: Dict[str, Set[str]] = {}
    
    def new_entry(self, new_entry: LogEntry) -> None:
        if new_entry.type == "WORLD_EVENT" and new_entry.subtype == "ENTITY_ENTERS_LOCATION":
            if new_entry.properties['entity'] not in self.__agents_names:
                return
            if new_entry.properties['entity'] not in self.__agents_locations_visited:
                self.__agents_locations_visited[new_entry.properties['entity']] = {new_entry.properties['destination']}
            else:
                self.__agents_locations_visited[new_entry.properties['entity']].add(new_entry.properties['destination'])
        
    def stats(self) -> Dict[str, float]:
        values = [len(locations) for locations in self.__agents_locations_visited.values()] 
        return {'locations_visited_mean': statistics.mean(values), 'locations_visited_sd': statistics.stdev(values)}


class Trips(Metric):
    def __init__(self, agents: Set[str] ) -> None:
        self.__agents_names = agents
        self.__agents_trips: Dict[str, int] = {}
    
    def new_entry(self, new_entry: LogEntry) -> None:
        if new_entry.type == "WORLD_EVENT" and new_entry.subtype == "ENTITY_ENTERS_LOCATION":
            if new_entry.properties['entity'] not in self.__agents_names:
                return
            if new_entry.properties['entity'] not in self.__agents_trips:
                self.__agents_trips[new_entry.properties['entity']] = 1
            else:
                self.__agents_trips[new_entry.properties['entity']] += 1
        
    def stats(self) -> Dict[str, float]:
        values = [trips for trips in self.__agents_trips.values()] 
        return {'trips_mean': statistics.mean(values), 'trips_sd': statistics.stdev(values)}

class BedsUsed(Metric):
    def __init__(self, agents: Set[str] ) -> None:
        self.__agents_names = agents
        self.__agents_beds_used: Dict[str, Set[str]] = {}
    
    def new_entry(self, new_entry: LogEntry) -> None:
        if new_entry.type == "WORLD_EVENT" and new_entry.subtype == "PRACTICE_STARTS" and new_entry.properties['practice_label'] == "Sleep":
            if new_entry.properties['entity'] not in self.__agents_names:
                return
            if new_entry.properties['entity'] not in self.__agents_beds_used:
                self.__agents_beds_used[new_entry.properties['entity']] = {new_entry.properties['bed']}
            else:
                self.__agents_beds_used[new_entry.properties['entity']].add(new_entry.properties['bed'])
        
    def stats(self) -> Dict[str, float]:
        values = [len(beds) for beds in self.__agents_beds_used.values()] 
        return {'beds_used_mean': statistics.mean(values), 'beds_used_sd': statistics.stdev(values)}

class TimeSleeping(Metric):
    def __init__(self, agents: Set[str] ) -> None:
        self.__agents_names = agents
        self.__agents_time_sleeping: Dict[str, float] = {}
        self.__agent_last_sleeping_start: Dict[str, int] = {}
    
    def new_entry(self, new_entry: LogEntry) -> None:
        if new_entry.type == "WORLD_EVENT" and new_entry.subtype == "PRACTICE_STARTS" and new_entry.properties['practice_label'] == "Sleep":
            
            if new_entry.properties['entity'] not in self.__agents_names:
                return
            
            self.__agent_last_sleeping_start[new_entry.properties['entity']] = new_entry.tick


        if new_entry.type == "WORLD_EVENT" and new_entry.subtype == "PRACTICE_ENDS" and new_entry.properties['practice_label'] == "Sleep":
            if new_entry.properties['entity'] not in self.__agents_time_sleeping:
                self.__agents_time_sleeping[new_entry.properties['entity']] = new_entry.tick - self.__agent_last_sleeping_start[new_entry.properties['entity']]
            else:
                self.__agents_time_sleeping[new_entry.properties['entity']] += new_entry.tick - self.__agent_last_sleeping_start[new_entry.properties['entity']]
        
    def stats(self) -> Dict[str, float]:
        values = [sleeping_time for sleeping_time in self.__agents_time_sleeping.values()] 
        return {'time_sleeping_mean': statistics.mean(values), 'time_sleeping_sd': statistics.stdev(values)}


class TimeAtLeastNLocationsWithSpecificOccupancy(Metric):
    
    __min_occupants : int = 0
    __max_occupants : int = 9999999
    __min_locations : int
    __last_tick : int
    __occupancy_per_location: Dict[str, Set[str]] = {}
    __time_location_with_occupancy: int = 0
    
    def __init__(self, agents: Set[str], min_occupants: int, max_occupants: int, min_locations: int) -> None:
        self.__agents_names = agents
        self.__min_occupants = min_occupants
        self.__max_occupants = max_occupants
        self.__min_locations = min_locations
        self.__last_tick = 0
        
    def new_entry(self, new_entry: LogEntry) -> None:
        if new_entry.type == "WORLD_EVENT" and new_entry.subtype == "ENTITY_ENTERS_LOCATION":
            agent = new_entry.properties['entity']
            
            if agent not in self.__agents_names:
                return
            
            current_tick = new_entry.tick
                       
            if current_tick > self.__last_tick:
                delta = current_tick - self.__last_tick
                
                num_locations = 0
                for _, occupants in self.__occupancy_per_location.items():
                    if self.__min_occupants <= len(occupants) <= self.__max_occupants:
                        num_locations += 1
                
                if num_locations >= self.__min_locations:
                    self.__time_location_with_occupancy += delta

                    
            for _, occupants in self.__occupancy_per_location.items():
                if agent in occupants:
                    occupants.remove(agent)
            
            agent_location = new_entry.properties['destination']
            
            if agent_location not in self.__occupancy_per_location:
                self.__occupancy_per_location[agent_location] = {agent}
            else:
                self.__occupancy_per_location[agent_location].add(agent)
                           
            self.__last_tick = current_tick
                
    def stats(self) -> Dict[str, float]:
        return {f'time_atleast_{self.__min_locations}Locations_between_{self.__min_occupants}_and_{self.__max_occupants}_occupants': self.__time_location_with_occupancy}

class Agent:

    def __init__(self, name: str) -> None:
        self.practices : Dict[str, Dict] = {}
        self.name:str = name
        self.locations_visited : Set[str] = set()
        self.travels = 0
        self.beds_used : Set[str] = set()
        self.time_sleeping = 0
                            
    def __hash__(self) -> int:
        return hash(self.name)
    
if __name__ == "__main__":
    report = False
    path = 'logs/'
    files = os.listdir(path)
    output_file = f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}_{random.randint(0,9999)}.csv"
    field_names = []
    
    
    
    
    
    for f in files:
        if ".db" in f:
            
            logger = Logger(path + f)
            
            ##################################
            # Get Domains    
            ##################################        
            # > AGENTS & LOCATIONS
            agents_name = set()
            locations_name = set()
            for doc in logger.database.all():
                if doc['type'] == Logger.A_SALIENCEVECTOR:
                    agents_name.add(doc['entity'])
                if doc['type'] == Logger.A_ENTITYENTERSLOCATION:
                    locations_name.add(doc['destination'])
            
            ##################################
            # Prepare Metrics    
            ##################################      
            
            metrics : List[Metric] = []
            metrics.append(LocationsVisited(agents=agents_name))
            metrics.append(Trips(agents=agents_name))
            metrics.append(BedsUsed(agents=agents_name))
            metrics.append(TimeSleeping(agents=agents_name))
            metrics.append(TimeAtLeastNLocationsWithSpecificOccupancy(agents=agents_name, min_occupants=2,max_occupants=10, min_locations=1))
            metrics.append(TimeAtLeastNLocationsWithSpecificOccupancy(agents=agents_name, min_occupants=4,max_occupants=10, min_locations=1))
            metrics.append(TimeAtLeastNLocationsWithSpecificOccupancy(agents=agents_name, min_occupants=9,max_occupants=10, min_locations=1))
            metrics.append(TimeAtLeastNLocationsWithSpecificOccupancy(agents=agents_name, min_occupants=2,max_occupants=10, min_locations=2))
            metrics.append(TimeAtLeastNLocationsWithSpecificOccupancy(agents=agents_name, min_occupants=4,max_occupants=10, min_locations=2))
            metrics.append(TimeAtLeastNLocationsWithSpecificOccupancy(agents=agents_name, min_occupants=2,max_occupants=10, min_locations=3))

            for entry in logger.database.all():
                log = LogEntry(entry['tick'],type="WORLD_EVENT",subtype=entry['type'], properties=entry)
                
                for metric in metrics:
                    metric.new_entry(log)
                
                  
                

            
            ##################################
            # Prepare Data Structure    
            ##################################        
        
            agents: Dict[str, Agent] = {}
            for agent_name in agents_name:
                agents[agent_name] = Agent(agent_name) 
                
                
            ##################################
            # Calculate Individual Metrics
            ##################################                
                
            # Get Practice 
            Entry = Query()
            for entry in logger.database.search(Entry.type == Logger.A_SALIENCEVECTOR):
                agents[entry['entity']].practices[entry['practice_label']] = entry['practice_weight_vector']
           
           
            ##################################
            # Write to File
            ##################################
            
            values = {}
            
            agent_id = 0
            
            for _, agent in agents.items():
                prefix = f"A{agent_id}"
                
                for practice in agent.practices.values():
                    for label, weights in practice.items():    
                        values[f"{prefix}_{label}"] = weights
                        
                agent_id += 1
            
            
            results ={}
            for metric in metrics:
                results.update(metric.stats())
                            
            print(results)         
            input()    
            # Write to file
            file_exists = os.path.isfile(output_file)
               
            with open(output_file, "a", newline="") as csvfile:

                writer = csv.DictWriter(csvfile, fieldnames=values.keys())
                
                if not file_exists:
                    writer.writeheader()
                    
                writer.writerow(values)
                    
                                        


        
