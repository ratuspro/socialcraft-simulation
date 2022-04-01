from abc import abstractmethod, ABC
from typing import Dict, Any


class Entity(ABC):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.__attributes: Dict[str, Any] = {}
        self.__name = name

    @abstractmethod
    def tick(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self.__name

    @property
    def attributes(self) -> Dict[str, Any]:
        return self.__attributes

    def add_attribute(self, label: str, value: Any) -> None:
        self.__attributes[label] = value
