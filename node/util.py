import hashlib
import json
import os
from typing import List

from node.transaction.confirmed_transaction_model import ConfirmedTransaction


DIFFICULTY = os.getenv("DIFFICULTY", 4)
DIFFICULTY = int(DIFFICULTY)


def validate_pow(transactions: List[ConfirmedTransaction], previous_hash, nonce):
    transactions_without_signature = [tx.get_representation_without_signature() for tx in transactions]
    guess = (str(transactions_without_signature) + str(previous_hash) + str(nonce)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    if guess_hash[:DIFFICULTY] == "0" * DIFFICULTY:
        return

    raise Exception(f"Proof of work not valid.")


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
