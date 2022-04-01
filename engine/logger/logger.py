from enum import Enum
from tinydb import TinyDB, Query
from typing import List, Dict
import json

from engine.entities.entity import Entity

class Entry:
    def __init__(self, tick: str, type: str, agent: str,  data: Dict[str, str]) -> None:
        self.__data: Dict[str, str] = data
        self.__tick: str = tick
        self.__type: str = type
        self.__agent: str = agent

    def toDocument(self) -> Dict[str, str]:
        document = {}
        document['tick'] = self.__tick
        document['type'] = self.__type
        document['agent'] = self.__agent
        document = document | self.__data
        return document

    @classmethod
    def fromDocument(cls, document: Dict[str, str]):
        return cls(document['tick'], document['type'], document['agent'], {})

class Logger:
    __filepath = ""
    _instance = None

    class EntryType(str, Enum):
        PRACTICESTARTS: str = "PRACTICE_STARTS"
        PRACTICEENDS:str = "PRACTICE_ENDS"
        ENTITYENTERSLOCATION:str = "ENTITY_ENTERS_LOCATION"
        SALIENCEVECTOR:str = "SALIENCE_VECTOR"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.__buffer = []
            cls._instance.__db = TinyDB(cls.__filepath)
        return cls._instance

    @classmethod
    def drop(cls):
        cls._instance = None

    @classmethod
    def set_file_path(cls, path):
        cls.__filepath = path

    def __init__(self) -> None:
        raise RuntimeError(
            "Cannot instanciate Logger directly. Use Logger.instance()")

    def register_entry(self, tick: int, type: EntryType, entity: Entity,  data: Dict[str, str]) -> None:
        self.__buffer.append(Entry(tick, json.dumps(type), entity.name, data))

    def commit(self) -> None:
        docs = []
        for entry in self.__buffer:
            docs.append(entry.toDocument())
        self.__db.insert_multiple(docs)        
        self.__buffer = []

    def get_all_from_agent(self, entity: str) -> List:
        entryQ = Query()
        return self.__db.search(entryQ.entity == entity)
    



