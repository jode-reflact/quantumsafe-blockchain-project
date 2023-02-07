from node.database import db
from node.transaction.abstract_transaction_model import AbstractTransaction


class PendingTransaction(db.Model, AbstractTransaction):
    __tablename__ = "pending_transactions"
    timestamp = db.Column(db.String, primary_key=True)
    sender = db.Column(db.String)
    receiver = db.Column(db.String)
    amount = db.Column(db.String)
    signature = db.Column(db.String)


class ConfirmedTransaction(db.Model, AbstractTransaction):
    __tablename__ = "confirmed_transactions"
    timestamp = db.Column(db.String, primary_key=True)
    sender = db.Column(db.String)
    receiver = db.Column(db.String)
    amount = db.Column(db.String)
    signature = db.Column(db.String)

    block_index = db.Column(db.Integer, db.ForeignKey("blocks.index"))

    @staticmethod
    def from_json(json):
        return ConfirmedTransaction(
            timestamp=json["timestamp"],
            sender=json["sender"],
            receiver=json["receiver"],
            amount=json["amount"],
            signature=json["signature"],
        )