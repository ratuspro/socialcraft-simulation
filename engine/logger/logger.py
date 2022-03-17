from enum import Enum
from datetime import datetime

from typing import Any, Dict, Optional, List, Tuple, Type

from sqlalchemy import JSON, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..entities import Entity
from ..world import Location


Base = declarative_base()


class LogType(Enum):
    ENTERED_LOCATION = "entered_location"
    STARTED_PRACTICE = "started_practice"
    FINISHED_PRACTICE = "finished_practice"
    REGISTER_SALIENCE_VECTOR = "register_valence"


class Action(Base):

    __tablename__ = "actions"

    id = Column(Integer, primary_key=True)
    tick = Column(Integer)
    action = Column(String)
    subject = Column(String)
    properties = Column(JSON, nullable=True)


class Logger:
    _instance = None
    __current_tick: int
    __database_file_name: str
    __database_session: Session
    __database_engine: Engine

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

            cls._instance.__database_file_name = (
                datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f") + ".db"
            )
            cls._instance.__database_engine = create_engine(
                f"sqlite:///{cls._instance.__database_file_name}", echo=False
            )
            Base.metadata.create_all(cls._instance.__database_engine)

            Session = sessionmaker(bind=cls._instance.__database_engine)
            cls._instance.__database_session = Session()

            cls._instance.__current_tick = 0
        return cls._instance

    def __init__(self) -> None:
        raise RuntimeError("Cannot instanciate Logger directly. Use Logger.instance()")

    def __register_action(
        self,
        tick: int,
        action: LogType,
        subject: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:

        if properties is None:
            properties = {}

        entry = Action(
            tick=tick, action=str(action), subject=subject, properties=properties
        )
        self.__database_session.add(entry)

    def new_run(self) -> None:

        self.__database_file_name = (
            datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f") + ".db"
        )
        self.__database_engine = create_engine(
            f"sqlite:///{self.__database_file_name}", echo=False
        )
        Base.metadata.create_all(self.__database_engine)

        Session = sessionmaker(bind=self.__database_engine)
        self.__database_session = Session()

        self.__current_tick = 0

    def set_tick(self, current_tick: int) -> None:
        self.__current_tick = current_tick

    def on_entity_entered(self, entity: Entity, location: Location) -> None:
        self.__register_action(
            self.__current_tick,
            LogType.ENTERED_LOCATION,
            str(entity),
            {"location": str(location)},
        )

    def on_practice_starts(
        self, entity: Entity, practice_name: str, properties: Dict[str, Any]
    ) -> None:
        self.__register_action(
            self.__current_tick,
            LogType.STARTED_PRACTICE,
            str(entity),
            {"label": practice_name} | properties,
        )

    def on_practice_ends(self, entity: Entity, practice_name: str) -> None:
        self.__register_action(
            self.__current_tick,
            LogType.FINISHED_PRACTICE,
            str(entity),
            {"label": practice_name},
        )

    def log_salience_vecotr(
        self, agent: Entity, pratice: Type, weights: Dict[str, Tuple[float, float]]
    ):
        self.__register_action(
            tick=-1,
            action=LogType.REGISTER_SALIENCE_VECTOR,
            subject=str(agent),
            properties={"practice": str(pratice), "weights": str(weights)},
        )

    def commit(self):
        self.__database_session.commit()

    def get_action(
        self,
        tick: Optional[int] = None,
        actions: Optional[List[LogType]] = None,
        subject: Optional[Entity] = None,
    ) -> List[Action]:
        query = self.__database_session.query(Action)

        if tick is not None:
            query = query.filter(Action.tick == tick)

        if actions is not None and len(actions) > 0:

            query = query.filter(
                Action.action.in_([str(logtype) for logtype in actions])
            )

        if subject is not None:
            query = query.filter(Action.subject == str(subject))

        return query.all()
