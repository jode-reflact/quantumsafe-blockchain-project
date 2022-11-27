import binascii

from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import DSS, pkcs1_15

from blockchain.transaction import Transaction


class ClientTransaction:
    def __init__(self, sender_address, sender_private_key, receiver_address, amount):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.receiver_address = receiver_address
        self.amount = amount

    def __getattr__(self, attr):
        return self.data[attr]

    def to_transaction(self):
        return Transaction(self.sender_address, self.receiver_address, self.amount).__dict__

    def sign_transaction(self):
        """Sign transaction with private key"""
        # private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        # signer = pkcs1_15.new(private_key)
        #
        # print("CLIENT: ", self.to_transaction())
        # transaction_hash = SHA1.new(str(self.to_transaction()).encode("utf8"))
        # return binascii.hexlify(signer.sign(transaction_hash)).decode("ascii")

        private_key = ECC.import_key(binascii.unhexlify(self.sender_private_key))
        signer = DSS.new(private_key, "fips-186-3")
        transaction_hash = SHA256.new(str(self.to_transaction()).encode("utf8"))
        signature = signer.sign(transaction_hash)

        return binascii.hexlify(signature).decode("ascii")
