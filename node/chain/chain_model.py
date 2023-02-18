from functools import reduce
from typing import List
from node.database import db
from node.block.block_model import Block
from sqlalchemy.orm import Mapped


class Chain(db.Model):
    __tablename__ = "chains"
    index: Mapped[int] = db.Column(db.Integer, primary_key=True)
    blocks: Mapped[List[Block]] = db.relationship("Block", backref="chains", cascade="all, delete-orphan")

    def __init__(self, blocks):
        self.blocks = blocks

    @property
    def length(self):
        return len(self.blocks)

    @property
    def transaction_count(self):
        transaction_count = 0
        for block in self.blocks:
            # subtract the block reward transaction
            transactions_without_reward = list(filter(lambda t: t["sender"] != "THE BLOCKCHAIN", block.transactions))
            transaction_count = transaction_count + len(transactions_without_reward)
        return transaction_count

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
        # Since our first block (with index 0) is the genesis block,
        # we start with validating the second block (with index 1).
        while index < self.length:
            current_block = self.blocks[index]

            if current_block.previous_hash != last_block.hash():
                raise Exception(f"Previous Hash of Block {index} is not valid.")

            current_block.validate()

            last_block = current_block
            index += 1
