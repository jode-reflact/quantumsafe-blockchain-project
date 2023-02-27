import os
import sys
from configparser import ConfigParser
import time
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.engine import reflection

from sqlalchemy import create_engine

from node.chain.chain_model import Chain

from .miner import Miner

config = ConfigParser()
config.read("config.ini")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Not enough argument, Usage: python -m miner <PORT>")

    _, PORT = sys.argv
    PORT = int(PORT)
    DIFFICULTY = os.getenv("DIFFICULTY")
    BLOCK_SIZE = os.getenv("BLOCK_SIZE")
    USE_CACHE = os.getenv("USE_CACHE", default="False")

    DIFFICULTY = int(DIFFICULTY)
    BLOCK_SIZE = int(BLOCK_SIZE)
    USE_CACHE = (USE_CACHE == 'true')
    print("USE_CACHE", USE_CACHE)
    time.sleep(10)

    db_name = f"node_{str(PORT)}.db"
    #engine = create_engine("sqlite:////Users/jonasdeterding/VisualStudioCode/quantumsafe-blockchain-project/node/instance/" + db_name, echo=False)
    engine = create_engine("sqlite:////" + db_name, echo=False)

    insp = reflection.Inspector.from_engine(engine)

    session = Session(engine, autoflush=False)

    miner = Miner(session=session, PORT=PORT, DIFFICULTY=DIFFICULTY, BLOCK_SIZE=BLOCK_SIZE, USE_CACHE=USE_CACHE)