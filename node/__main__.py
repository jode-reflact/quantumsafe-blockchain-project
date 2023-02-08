from flask import Flask
import os.path
import sys
from configparser import ConfigParser

from node.chain.chain_routes import chain
from node.database import db
from node.node.node_routes import nodes
from node.transaction.pending_transaction_routes import transactions


# Get the config for the Flask app
config = ConfigParser()
config.read("config.ini")


def create_app():
    app = Flask(__name__)
    # app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + db_name
    db.init_app(app)
    app.register_blueprint(transactions, url_prefix="/transactions")
    app.register_blueprint(nodes, url_prefix="/nodes")
    app.register_blueprint(chain, url_prefix="/chain")
    return app


def setup_database(app):
    with app.app_context():
        # reset db each run
        db.drop_all()
        db.create_all()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: pipenv run blockchain <PORT>")

    _, PORT = sys.argv
    PORT = int(PORT)

    db_name = f"node_{str(PORT)}.db"

    app = create_app()

    # absolute_db_path = os.path.join(os.getcwd(), "node", "instance", db_name)
    # if not os.path.isfile(absolute_db_path):
    setup_database(app)

    app.run(
        host=config.get("BLOCKCHAIN", "host"),
        port=PORT,
        debug=config.getboolean("DEBUG", "debug"),
    )
