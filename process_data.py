import os
from engine.logger.logger import Logger
from tinydb import Query
from typing import Dict, Any, List, Set
from datetime import datetime
import random
import csv

### Metrics
## Number of Distinct Locations Visited
## Number of Travels
## Number of Different Beds Used
## Time Sleeping


class Agent:

    def __init__(self, name: str) -> None:
        self.practices : Dict[str, Dict] = {}
        self.name:str = name
        self.locations_visited : Set[str] = set()
        self.travels = 0
        self.beds_used : Set[str] = set()
        self.time_sleeping = 0
        
    @property
    def fields(self) -> List[str]:
        fields = []
        for practice_fields in self.practices.values():
            fields.extend(list(practice_fields.keys()))
        fields.append("locations_visited")
        fields.append("travels")
        fields.append("beds_used")
        fields.append("time_sleeping")
        return fields
    
    @property
    def values(self) -> Dict[str, str]:
        values = {}        
        for practice_values in self.practices.values():
            values = values | practice_values
                        
        values["locations_visited"] = len(self.locations_visited)
        values["travels"] = self.travels
        values["beds_used"] =  len(self.beds_used)
        values["time_sleeping"] = self.time_sleeping
        return values
                    
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
   
            # Get Domains            
            agents_name = set()
            for doc in logger.database.all():
                if doc['type'] == Logger.A_SALIENCEVECTOR:
                    agents_name.add(doc['entity'])

            if report:
                print("Agents:")
                for agent in agents_name:
                    print(f"> {agent}")
                
            agents: Dict[str, Agent] = {}
            for agent_name in agents_name:
                agents[agent_name] =Agent(agent_name) 
                
            # Get Practice 
            Entry = Query()
            for entry in logger.database.search(Entry.type == Logger.A_SALIENCEVECTOR):
                agents[entry['entity']].practices[entry['practice_label']] = entry['practice_weight_vector']

            # Calculate location based metrics
            for entry in logger.database.search(Entry.type == Logger.A_ENTITYENTERSLOCATION):
                if entry['entity'] in agents_name:
                    agents[entry['entity']].locations_visited.add(entry['destination'])
                    agents[entry['entity']].travels += 1
                    
            # Calculate sleep metrics
            for agent_name in agents_name:
                sleeping_practices = logger.database.search((Entry.entity == agent_name) & ((Entry.type == Logger.A_PRACTICESTARTS) | (Entry.type == Logger.A_PRACTICEENDS)) & (Entry.practice_label == 'Sleep') )
                for i in range(0, len(sleeping_practices) // 2):
                    agents[agent_name].time_sleeping += sleeping_practices[i * 2 + 1]['tick'] - sleeping_practices[i * 2]['tick']
                    agents[agent_name].beds_used.add(sleeping_practices[i * 2]['bed'])
                    
                    
            # Write to file
            file_exists = os.path.isfile(output_file)
            
            if not file_exists:
                field_names = agents[list(agents.keys())[0]].fields
                
            with open(output_file, "a", newline="") as csvfile:

                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                if not file_exists:
                    writer.writeheader()
                    
                for agent in agents.values():
                    writer.writerow(agent.values)
                    
                                        


        
