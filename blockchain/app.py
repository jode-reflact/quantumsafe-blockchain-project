from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_executor import Executor
import time

from uuid import uuid4

from .blockchain import Blockchain, MINING_REWARD, MINING_SENDER

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['EXECUTOR_MAX_WORKERS'] = 1
app.config['EXECUTOR_FUTURES_MAX_LENGTH'] = 1
executor = Executor(app)

# Define blockchain Variables
blockchain = Blockchain(app)
node_identifier = str(uuid4()).replace("-", "")

@app.route("/mine", methods=["GET"])
def mine():
    mineInternal.submit_stored('mineInternal')
    return jsonify({'scheduled': True}), 200

@executor.job
def mineInternal():
    # We run the proof of work algorithm to get the next proof...
    app.logger.error('mining now')
    nonce = blockchain.proof_of_work()
    block = blockchain.generate_block_by_nounce(blockchain.last_block, nonce)

    app.logger.error('New block ' + block['block_number'].__str__())
    mine()

with app.test_request_context():
    mine()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/configure")
def configure():
    return render_template("configure.html")


@app.route("/transactions", methods=["POST"])
def receive_transaction():
    values = request.get_json()

    required = ["sender", "receiver", "amount", "signature", "timestamp"]
    if not all(k in values for k in required):
        return "Missing values", 400

    transaction_result = blockchain.submit_transaction(
        values["sender"],
        values["receiver"],
        values["amount"],
        values["signature"],
        values["timestamp"],
    )

    if not transaction_result:
        response = {"message": "Invalid Transaction!"}
        return jsonify(response), 406
    else:
        response = {
            "message": "Transaction will be added to Block " + str(transaction_result)
        }
        return jsonify(response), 201


@app.route("/transactions/get", methods=["GET"])
def get_transactions():
    transactions = blockchain.pending_transactions

    response = {"transactions": transactions}
    return jsonify(response), 200


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = request.form
    nodes = values.get("nodes").replace(" ", "").split(",")

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {"message": "Our chain was replaced", "new_chain": blockchain.chain}
        # was replaced, restart mining
        return jsonify(response), 200

    response = {"message": "Our chain is authoritative", "chain": blockchain.chain}
    return jsonify(response), 201



@app.route("/nodes/get", methods=["GET"])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {"nodes": nodes}
    return jsonify(response), 200