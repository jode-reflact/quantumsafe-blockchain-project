from enum import Enum
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA, ECC
from client.transaction import ClientTransaction
import requests
import time
import random
import binascii

class EncryptionTypes(Enum):
    RSA = "rsa"
    ECC = "ecc"

def generate_transaction_json(sender_address: str, sender_private_key: str, receiver_address: str,
                              amount: int):
    transaction = ClientTransaction(
        sender_address, sender_private_key, receiver_address, amount
    )
    signature = transaction.sign_transaction()
    transaction_json = {
        "sender": sender_address,
        "receiver": receiver_address,
        "amount": amount,
        "signature": signature
    }

    return transaction_json

def submit_transaction(transaction_json, target_node):
    response = requests.post(f"http://{target_node}/transactions/receive",
                             json=transaction_json,
                             headers={"Access-Control-Allow-Origin": "*"})

    if response.status_code != 201:
        raise ValueError("ERROR: {}".format(response.status_code))

    return True

def generate_sender_receiver_pair(encryption_type: EncryptionTypes):
    if encryption_type == EncryptionTypes.RSA:
        sender_random_gen = Crypto.Random.new().read
        sender_private_key = RSA.generate(1024, sender_random_gen)

        sender_private_key_der = sender_private_key.exportKey(format="DER")
        sender_public_key_der = sender_private_key.publickey().exportKey(format="DER")

        sender_private_key_ascii = binascii.hexlify(sender_private_key_der).decode("ascii")
        sender_public_key_ascii = binascii.hexlify(sender_public_key_der).decode("ascii")

        receiver_random_gen = Crypto.Random.new().read
        receiver_private_key = RSA.generate(1024, receiver_random_gen)

        receiver_private_key_der = receiver_private_key.exportKey(format="DER")
        receiver_public_key_der = receiver_private_key.publickey().exportKey(format="DER")

        receiver_private_key_ascii = binascii.hexlify(receiver_private_key_der).decode("ascii")
        receiver_public_key_ascii = binascii.hexlify(receiver_public_key_der).decode("ascii")

        return sender_public_key_ascii, sender_private_key_ascii, receiver_public_key_ascii

    if encryption_type == EncryptionTypes.ECC:
        sender_key = ECC.generate(curve='P-256')
        sender_private_key_ascii = binascii.hexlify(sender_key.export_key(format='DER'))\
            .decode("ascii")
        sender_public_key_ascii = binascii.hexlify(sender_key.public_key().export_key(format='DER'))\
            .decode("ascii")

        receiver_key = ECC.generate(curve='P-256')
        receiver_public_key_ascii = binascii.hexlify(receiver_key.public_key().export_key(format='DER'))\
            .decode("ascii")

        return sender_public_key_ascii, sender_private_key_ascii, receiver_public_key_ascii

if __name__ == '__main__':
    sender_address, sender_private_key, receiver_address = generate_sender_receiver_pair(EncryptionTypes.ECC)

    time_needed_seconds = 0.0
    counter = 0

    for i in range(1000):
        transaction = generate_transaction_json(sender_address, sender_private_key, receiver_address, random.randint(1, 10000))
        start_time = time.time()
        submit_transaction(transaction, "127.0.0.1:5000")
        time_needed_seconds += time.time() - start_time
        counter += 1

    print("Sent and verified {} transactions in {} seconds".format(counter, time_needed_seconds))
