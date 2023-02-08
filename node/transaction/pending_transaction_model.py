from node.database import db
from node.transaction.base_transaction_model import BaseTransaction


class PendingTransaction(db.Model, BaseTransaction):
    __tablename__ = "pending_transactions"
    timestamp = db.Column(db.String, primary_key=True)
    sender = db.Column(db.String)
    receiver = db.Column(db.String)
    amount = db.Column(db.String)
    signature = db.Column(db.String)

    # TODO: Implement from_json and replace in TransactionService
