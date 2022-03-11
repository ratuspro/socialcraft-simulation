class Location:
    __name: str
    __min_time_inside: int

    def __init__(self, name: str, min_time_inside: int) -> None:
        self.__name = name
        self.__min_time_inside = min_time_inside

    @property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"Location - {self.__name}"

    @property
    def min_time_inside(self) -> int:
        return self.__min_time_inside
