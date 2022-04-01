from enum import Enum
from tinydb import TinyDB, Query
from typing import List, Dict
import json

from engine.entities.entity import Entity

class Entry:
    def __init__(self, tick: str, type: str, entity: str,  data: Dict[str, str]) -> None:
        self.__data: Dict[str, str] = data
        self.__tick: str = tick
        self.__type: str = type
        self.__entity: str = entity

    def toDocument(self) -> Dict[str, str]:
        document = {}
        document['tick'] = self.__tick
        document['type'] = self.__type
        document['entity'] = self.__entity
        document = document | self.__data
        return document

    @classmethod
    def fromDocument(cls, document: Dict[str, str]):
        return cls(document['tick'], document['type'], document['entity'], {})

class Logger:
    _instance = None

    class EntryType(str, Enum):
        PRACTICESTARTS: str = "PRACTICE_STARTS"
        PRACTICEENDS:str = "PRACTICE_ENDS"
        ENTITYENTERSLOCATION:str = "ENTITY_ENTERS_LOCATION"
        SALIENCEVECTOR:str = "SALIENCE_VECTOR"

    def __init__(self, filepath:str) -> None:
        self.__buffer = []
        self.__db = TinyDB(filepath)

    def register_entry(self, tick: int, type: EntryType, entity: Entity, data: Dict[str, str]) -> None:
        self.__buffer.append(Entry(tick, json.dumps(type), entity.name, data))

    def commit(self) -> None:
        docs = []
        for entry in self.__buffer:
            docs.append(entry.toDocument())
        self.__db.insert_multiple(docs)        
        self.__buffer = []

    @property
    def database(self) -> TinyDB:
        return self.__db
