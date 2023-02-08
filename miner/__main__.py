import os
import sys
from configparser import ConfigParser
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from sqlalchemy import create_engine

from .miner import Miner

config = ConfigParser()
config.read("config.ini")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise Exception("Not enough argument, Usage: python -m miner <PORT> <DIFFICULTY> <BLOCK_SIZE>")

    _, PORT,DIFFICULTY, BLOCK_SIZE = sys.argv
    PORT = int(PORT)
    DIFFICULTY = int(DIFFICULTY)
    BLOCK_SIZE = int(BLOCK_SIZE)

    db_name = f"node_{str(PORT)}.db"
    engine = create_engine("sqlite:////Users/jonasdeterding/VisualStudioCode/quantumsafe-blockchain-project/node/instance/" + db_name, echo=True)

    session = Session(engine)

    miner = Miner(session,DIFFICULTY, BLOCK_SIZE)