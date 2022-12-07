import sys
from configparser import ConfigParser

from .app import app

# Get the config for the Flask app
config = ConfigParser()
config.read("config.ini")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: pipenv run blockchain <PORT>")

    _, PORT = sys.argv
    PORT = int(PORT)

    app.run(
        host=config.get("BLOCKCHAIN", "host"),
        port=PORT,
        debug=config.getboolean("DEBUG", "debug"),
    )