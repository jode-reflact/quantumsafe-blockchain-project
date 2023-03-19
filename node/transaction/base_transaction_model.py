from collections import OrderedDict
import binascii
from Crypto.Hash import SHA256

from node.transaction.cipher import cipher


class BaseTransaction:

    def __init__(self, timestamp, sender, receiver, amount, signature, receivedAt):
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature
        self.receivedAt = receivedAt

    def __repr__(self):
        return f"Transaction(\
            timestamp={self.timestamp}, \
            amount={self.amount}, \
            sender={self.sender}, \
            receiver={self.receiver}, \
            signature={self.signature}, \
            receivedAt={self.receivedAt})"

    def verify(self):
        """
        Verifies that the signature corresponds to the transaction.
        Throws an ValueError if transaction is not authentic.
        """
        transaction_hash = SHA256.new(str(self.get_representation_without_signature()).encode("utf8"))
        cipher.verify(public_key=binascii.unhexlify(self.sender),
                      message_hash=transaction_hash,
                      signature=self.signature)

    def get_representation_without_receivedAt(self):
        """Transaction Representation without receivedAt.
        Used to mine and verify proof of work nonce.
        Received At cannot be used because its not filled at mining

        Returns:
            _type_: _description_
        """
        return OrderedDict(
            {
                "sender": self.sender,
                "receiver": self.receiver,
                "amount": self.amount,
                "timestamp": self.timestamp,
                "signature": self.signature
            }
        )

    def get_representation_without_signature(self):
        """Transaction Representation without receivedAt.
        Used to mine and verify proof of work nonce.
        Received At is not used because its not needed for mining

        Returns:
            _type_: _description_
        """
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
            "receivedAt": self.receivedAt
        }
