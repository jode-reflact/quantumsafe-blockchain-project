import hashlib
import json


DIFFICULTY = 3


def validate_pow(transactions, previous_hash, nonce):
    guess = (str(transactions) + str(previous_hash) + str(nonce)).encode()
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
