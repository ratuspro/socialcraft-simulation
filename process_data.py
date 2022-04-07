from distutils.log import Log
import os
from engine.logger.logger import Logger
from tinydb import Query
from typing import Dict, Any, List, Set
from datetime import datetime
import random
import csv
import statistics


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
            # > AGENTS
            agents_name = set()
            locations_name = set()
            for doc in logger.database.all():
                if doc['type'] == Logger.A_SALIENCEVECTOR:
                    agents_name.add(doc['entity'])
                if doc['type'] == Logger.A_ENTITYENTERSLOCATION:
                    locations_name.add(doc['destination'])
            
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

            ##################################
            # Calculate Group Metrics
            ##################################
            # > Location Distribution
            occupants : Dict [str, Set[str]] = {}
            for location in locations_name:
                occupants[location] = set()
                
            agent_location : Dict[str, str] = {}
                
            # Number of ticks with at least one location with 2 agents (=N//N)
            ticks_1location_min2agents = 0 
            # Number of ticks with at least one location with 4 agents (=N//2)
            ticks_1location_min4agents = 0
            # Number of ticks with at least one location with 9 agents (=N//1)
            ticks_1location_min9agents = 0
            # Number of ticks with at least two location with 2 agents (=N//N)
            ticks_2location_min2agents = 0
            # Number of ticks with at least two location with 4 agents (=N//2)
            ticks_2location_min4agents = 0
            # Number of ticks with at least three location with 2 agents (=N//N)
            ticks_3location_min2agents = 0
            
            previous_tick = 0                        
            for entry in logger.database.search((Entry.type == Logger.A_ENTITYENTERSLOCATION)):
                if entry['entity'] in agents_name:
                    agent_name = entry['entity']
                    agent_new_location = entry['destination']
                    if entry['tick'] > previous_tick:
                        delta = entry['tick'] - previous_tick
                        loc_with2agents = 0
                        loc_with4agents = 0
                        loc_with9agents = 0
                        for loc_name, loc_occupants in occupants.items():
                            if len(loc_occupants) >= 2:
                                loc_with2agents+=1
                            if len(loc_occupants) >= 4:
                                loc_with4agents+=1
                            if len(loc_occupants) >= 9:
                                loc_with9agents+=1
                        
                        if loc_with2agents >= 1:
                            ticks_1location_min2agents +=1
                        if loc_with2agents >= 2:
                            ticks_2location_min2agents +=1
                        if loc_with2agents >= 3:
                            ticks_3location_min2agents +=1
                        
                        if loc_with4agents >= 1:
                            ticks_1location_min4agents +=1
                        if loc_with4agents >= 2:
                            ticks_2location_min4agents +=1
                            
                        if loc_with9agents >= 1:
                            ticks_1location_min9agents +=1  
                    
                        previous_tick = entry['tick']
                
                    if agent_name in agent_location:
                        occupants[agent_location[agent_name]].remove(agent_name)

                    occupants[agent_new_location].add(agent_name)
                    agent_location[agent_name] = agent_new_location           
           
           
           
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
            
                    
            values['locations_visited_avg'] =  statistics.mean([len(ag.locations_visited) for ag in agents.values()])
            values['locations_visited_sd'] =   statistics.stdev([len(ag.locations_visited) for ag in agents.values()])
            
            values['travels_avg'] = statistics.mean([ag.travels for ag in agents.values()])
            values['travels_sd'] = statistics.stdev([ag.travels for ag in agents.values()])
            values['beds_used_avg'] = statistics.mean([len(ag.beds_used) for ag in agents.values()])
            values['beds_used_sd'] = statistics.stdev([len(ag.beds_used) for ag in agents.values()])
            values['time_sleeping_avg'] = statistics.mean([ag.time_sleeping for ag in agents.values()])
            values['time_sleeping_sd'] = statistics.stdev([ag.time_sleeping for ag in agents.values()])
            values['time_alo_1loc_min2agents'] = ticks_1location_min2agents/ 24000
            values['time_alo_1loc_min4agents'] = ticks_1location_min4agents/ 24000
            values['time_alo_1loc_min9agents'] = ticks_1location_min9agents/ 24000
            values['time_alo_2loc_min2agents'] = ticks_2location_min2agents/ 24000
            values['time_alo_2loc_min4agents'] = ticks_2location_min4agents/ 24000
            values['time_alo_3loc_min2agents'] = ticks_3location_min2agents/ 24000
                                
            # Write to file
            file_exists = os.path.isfile(output_file)
               
            with open(output_file, "a", newline="") as csvfile:

                writer = csv.DictWriter(csvfile, fieldnames=values.keys())
                
                if not file_exists:
                    writer.writeheader()
                    
                writer.writerow(values)
                    
                                        


        
