from engine.logger import Logger

class DependencyManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._logger = None
        return cls._instance

    def get_logger(self) -> Logger:
        return self.__logger

    def add_logger(self, logger: Logger):
        self.__logger = logger