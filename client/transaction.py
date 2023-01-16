import binascii
from collections import OrderedDict
import time

from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import DSS, pkcs1_15

import oqs


class ClientTransaction:
    def __init__(self, sender_address, sender_private_key, receiver_address, amount):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.receiver_address = receiver_address
        self.amount = amount
        self.timestamp = str(time.time())

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict(
            {
                "sender": self.sender_address,
                "receiver": self.receiver_address,
                "amount": self.amount,
                "timestamp": self.timestamp
            }
        )
