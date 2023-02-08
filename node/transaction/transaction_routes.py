from flask.blueprints import Blueprint
from flask import request, jsonify

from node.transaction.pending_transaction_model import PendingTransaction
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
    req = request.get_json()

    try:
        transaction = PendingTransaction.from_json(req)
        TransactionService.add_transaction(transaction)
    except KeyError:
        response = {"message": "incomplete transaction"}
        return jsonify(response), 400

    return '', 204
