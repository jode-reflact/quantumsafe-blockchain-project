from collections import OrderedDict
import binascii
from Crypto.Hash import SHA256

from node.database import db
from node.transaction.cipher import cipher


class AbstractTransaction():

    def __init__(self, timestamp, sender, receiver, amount, signature):
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def __repr__(self):
        return f"PendingTransaction(\
            timestamp={self.timestamp}, \
            amount={self.amount}, \
            sender={self.sender}, \
            receiver={self.receiver}, \
            signature={self.signature})"

    def verify(self):
        """
        Verifies that the signature corresponds to the transaction.
        Throws an ValueError if transaction is not authentic.
        """
        transaction_hash = SHA256.new(str(self.get_representation_without_signature()).encode("utf8"))
        cipher.verify(public_key=binascii.unhexlify(self.sender),
                      message_hash=transaction_hash,
                      signature=self.signature)

    def get_representation_without_signature(self):
        return OrderedDict(
            {
                "sender": self.sender,
                "receiver": self.receiver,
                "amount": self.amount,
                "timestamp": self.timestamp,
            }
        )

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }
