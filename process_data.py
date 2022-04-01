import os
from engine.logger.logger import Logger

if __name__ == "__main__":

    path = 'logs/'
    files = os.listdir(path)

    for f in files:
        if "db" in f:
            logger = Logger(path + f)
            logger.database.all()

