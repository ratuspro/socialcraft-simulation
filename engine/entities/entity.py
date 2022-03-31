from abc import abstractmethod, ABC
from typing import Dict, Any


class Entity(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.__attributes: Dict[str, Any] = {}

    @abstractmethod
    def tick(self) -> None:
        pass

    @property
    def attributes(self) -> Dict[str, Any]:
        return self.__attributes

    def add_attribute(self, label: str, value: Any) -> None:
        self.__attributes[label] = value
