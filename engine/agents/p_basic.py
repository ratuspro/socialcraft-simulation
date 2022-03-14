from .practice import Practice


class Sleep(Practice):
    def __init__(self, owner: Agent, world: World) -> None:
        super().__init__(owner, world, "Sleep")

    @abstractmethod
    def tick(self) -> None:
        pass

    @abstractmethod
    def enter(self) -> None:
        Logger.instance().on_practice_starts(self._owner, self.__practice_label)

    @abstractmethod
    def exit(self) -> None:
        Logger.instance().on_practice_ends(self._owner, self.__practice_label)

    @abstractmethod
    def has_ended(self) -> bool:
        pass