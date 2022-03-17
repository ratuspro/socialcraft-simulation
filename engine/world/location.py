from tkinter.font import BOLD


class Location:
    def __init__(self, name: str, min_time_inside: int, is_path: bool) -> None:
        self.__name: str = name
        self.__min_time_inside: int = min_time_inside
        self.__is_path: bool = is_path

    @property
    def name(self) -> str:
        return self.__name

    @property
    def is_path(self) -> bool:
        return self.__is_path

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"Location - {self.__name}"

    @property
    def min_time_inside(self) -> int:
        return self.__min_time_inside
