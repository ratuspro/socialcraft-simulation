from abc import abstractmethod, ABC


class Entity(ABC):
    @abstractmethod
    def tick(self) -> None:
        pass
