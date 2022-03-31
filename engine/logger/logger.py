from pydoc import doc
from tinydb import TinyDB, Query
from typing import List, Dict


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

    @classmethod
    def instance(cls):
        if cls._instance is not None:
            cls._instance = cls.__new__(cls)
            cls._instance.__buffer = []
            cls._instance.__db = TinyDB(cls.__filepath)
        return cls._instance

    @classmethod
    def set_file_path(cls, path):
        cls.__filepath = path

    def __init__(self) -> None:
        raise RuntimeError(
            "Cannot instanciate Logger directly. Use Logger.instance()")

    def register_entry(self, tick: str, type: str, agent: str,  data: Dict[str, str]) -> None:
        self.__buffer.append(Entry(tick, type, agent, data))

    def commit(self) -> None:
        for entry in self.__buffer:
            self.__db.insert(entry.toDocument())

        self.__buffer = []

    def get_all_from_agent(self, agent: str) -> List:
        entryQ = Query()
        return self.__db.search(entryQ.agent == agent)
