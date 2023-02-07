import hashlib
import json

from node.database import db
from node.block.block_model import Block

DIFFICULTY = 3


class Chain(db.Model):
    __tablename__ = "chains"
    index = db.Column(db.Integer, primary_key=True)
    blocks = db.relationship("Block", backref="chains", cascade="all, delete-orphan")

    def __init__(self, blocks):
        self.blocks = blocks

    @property
    def length(self):
        return len(self.blocks)

    @staticmethod
    def from_json(json):
        return Chain(
            blocks=[Block.from_json(b_json) for b_json in json["blocks"]]
        )

    def to_dict(self):
        return {
            "index": self.index,
            "blocks": [block.to_dict() for block in self.blocks]
        }

    def validate(self):
        """
        Determine if a given blockchain is valid
        :return: None
        :raise: ValueError if any transaction signature is not valid
        :raise: Exception if chain is not valid
        """
        last_block = self.blocks[0]
        index = 1

        while index < self.length:
            current_block = self.blocks[index]

            if current_block.previous_hash != self.hash(last_block):
                raise Exception(f"Previous Hash of Block {index} is not valid.")

            # validate transactions signatures
            # omit last transaction of block since it is the reward transaction
            transactions = current_block.transactions[:-1]

            for t in transactions:
                t.verify()

            # validate proof of work
            Chain.validate_pow(transactions, current_block.previous_hash, current_block.nonce)

            last_block = current_block
            index += 1

    @staticmethod
    def validate_pow(transactions, previous_hash, nonce):
        guess = (str(transactions) + str(previous_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        if guess_hash[:DIFFICULTY] == "0" * DIFFICULTY:
            return

        raise Exception(f"Proof of work not valid.")

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode()

        bin_hash = hashlib.sha256(block_string)
        hex_hash = bin_hash.hexdigest()

        return hex_hash
