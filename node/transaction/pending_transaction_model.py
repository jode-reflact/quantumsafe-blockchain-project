from node.database import db
from node.transaction.base_transaction_model import BaseTransaction


class PendingTransaction(db.Model, BaseTransaction):
    __tablename__ = "pending_transactions"
    timestamp = db.Column(db.String, primary_key=True)
    sender = db.Column(db.String)
    receiver = db.Column(db.String)
    amount = db.Column(db.String)
    signature = db.Column(db.String)

    @staticmethod
    def from_json(json):
        return PendingTransaction(
            timestamp=json["timestamp"],
            sender=json["sender"],
            receiver=json["receiver"],
            amount=json["amount"],
            signature=json["signature"],
        )
