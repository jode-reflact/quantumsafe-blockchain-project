import hashlib
import json
import os
from typing import List

from node.transaction.confirmed_transaction_model import ConfirmedTransaction


DIFFICULTY = os.getenv("DIFFICULTY", 4)
DIFFICULTY = int(DIFFICULTY)

USE_CACHE = os.getenv("USE_CACHE", default="False")
USE_CACHE = (USE_CACHE == 'true') | (USE_CACHE == 'True')

def validate_pow(transactions: List[ConfirmedTransaction], previous_hash, nonce):
    guess = (get_transactions_string(transactions) + str(previous_hash) + str(nonce)).encode()
    print("Guess", guess)
    guess_hash = hashlib.sha256(guess).hexdigest()

    if guess_hash[:DIFFICULTY] == "0" * DIFFICULTY:
        return

    raise Exception(f"Proof of work not valid.")

def get_transactions_string(transactions: List[ConfirmedTransaction]):
        if USE_CACHE:
            return str([str(tx.get_representation_without_receivedAt()) for tx in transactions])
        else:
            return str([tx.get_representation_without_receivedAt() for tx in transactions])

def hash_block(block):
    """
    Creates a SHA-256 hash of a Block
    :param block: <dict> Block
    :return: <str>
    """
    block_string = json.dumps(block, sort_keys=True).encode()

    bin_hash = hashlib.sha256(block_string)
    hex_hash = bin_hash.hexdigest()

    return hex_hash
