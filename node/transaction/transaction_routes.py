from flask.blueprints import Blueprint
from flask import request, jsonify

from node.transaction.transaction_service import TransactionService


transactions = Blueprint("transaction", __name__)


@transactions.route('/', methods=["GET"])
def get_pending_transactions():
    transactions = TransactionService.get_pending_transactions()
    serializable_transactions = list(
        map(lambda t: t.to_dict(), transactions)
    )

    response = {"transactions": serializable_transactions}

    return jsonify(response), 200


@transactions.route('/', methods=["POST"])
def receive_transaction():
    transaction = request.get_json()

    try:
        TransactionService.add_transaction(sender=transaction["sender"],
                                           receiver=transaction["receiver"],
                                           amount=transaction["amount"],
                                           timestamp=transaction["timestamp"],
                                           signature=transaction["signature"])
    except KeyError:
        response = {"message": "incomplete transaction"}
        return jsonify(response), 400

    return '', 204
