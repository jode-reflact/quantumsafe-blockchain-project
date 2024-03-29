from collections import OrderedDict
from typing import List
from Crypto.Hash import SHA256
from sqlalchemy.orm import Mapped
from node.database import db
from node.transaction.confirmed_transaction_model import ConfirmedTransaction
from node.util import validate_pow


class Block(db.Model):
    __tablename__ = "blocks"
    index = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String)
    nonce = db.Column(db.Integer)
    previous_hash = db.Column(db.String)
    transactions: Mapped[List[ConfirmedTransaction]] = db.relationship("ConfirmedTransaction", backref="blocks", cascade="all, delete-orphan")

    chain_index = db.Column(db.Integer, db.ForeignKey("chains.index"))

    @staticmethod
    def from_json(json):
        return Block(
            index=json["index"],
            timestamp=json["timestamp"],
            nonce=json["nonce"],
            previous_hash=json["previous_hash"],
            transactions=[
                ConfirmedTransaction.from_json(t_json) for t_json in json["transactions"]
            ]
        )

    def __init__(self, index, timestamp, nonce, previous_hash, transactions):
        self.index = index
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.transactions = transactions

    def __repr__(self):
        return f"Block( \
            index={self.index}, \
            timestamp={self.timestamp}, \
            nonce={self.nonce}, \
            previous_hash={self.previous_hash}, \
            transaction={self.transactions} \
            )"

    def validate(self):

        # validate transactions signatures
        # omit last transaction of block since it is the reward transaction
        transactions = self.transactions[:-1]
        validate_pow(transactions,
                     self.previous_hash,
                     self.nonce)
        for t in transactions:
            t.verify()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "transactions": [t.to_dict() for t in self.transactions],
        }
    def hash(self):
        return SHA256.new(str(self.to_dict()).encode("utf8")).hexdigest()
