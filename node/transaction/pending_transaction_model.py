from collections import OrderedDict

from node.database import db
from node.transaction.base_transaction_model import BaseTransaction


class PendingTransaction(db.Model, BaseTransaction):
    __tablename__ = "pending_transactions"
    timestamp = db.Column(db.String, primary_key=True)
    sender = db.Column(db.String)
    receiver = db.Column(db.String)
    amount = db.Column(db.String)
    signature = db.Column(db.String)
    receivedAt = db.Column(db.String)
    cached_representation = db.Column(db.String)

    def __init__(self, timestamp, sender, receiver, amount, signature, receivedAt):
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature
        self.receivedAt = receivedAt
        self.cached_representation = PendingTransaction.build_str_representation(
            sender=sender,
            receiver=receiver,
            amount=amount,
            timestamp=timestamp,
            signature=signature,
        )

    @staticmethod
    def from_json(json):
        if "receivedAt" in json:
            return PendingTransaction(
            timestamp=json["timestamp"],
            sender=json["sender"],
            receiver=json["receiver"],
            amount= str(json["amount"]),
            signature=json["signature"],
            receivedAt=json["receivedAt"]
            )
        else:
            return PendingTransaction(
                timestamp=json["timestamp"],
                sender=json["sender"],
                receiver=json["receiver"],
                amount= str(json["amount"]),
                signature=json["signature"],
            )

    @staticmethod
    def build_str_representation(sender: str, receiver: str, amount: str, timestamp: str, signature: str) -> str:
        return str(OrderedDict({
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": timestamp,
            "signature": signature
        }))
