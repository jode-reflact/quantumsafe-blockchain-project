import hashlib
import json
import os
from collections import OrderedDict
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from sqlalchemy.orm import Session
import binascii
import random
from typing import List

from Crypto.Hash import SHA256

import requests
from node.block.block_model import Block

from node.transaction.pending_transaction_model import PendingTransaction

MINING_REWARD = 1
MINING_SENDER = "THE BLOCKCHAIN"

class Miner(object):
    DIFFICULTY = None
    BLOCK_SIZE = None
    session = None

    def __init__(self, session: Session, DIFFICULTY, BLOCK_SIZE = None):
        self.session = session
        self.DIFFICULTY = DIFFICULTY
        self.BLOCK_SIZE = BLOCK_SIZE
        print("Miner init")
        self.mine()

    def mine(self):
        print("Start Mining")
        nonce, transactions = self.proof_of_work()
        print("Nounce", nonce)
    
    def proof_of_work(self):
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4
        zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof
        :return: <int>
        """
        nonce = 0
        transactions = self.get_transactions_for_next_block()
        while self.valid_proof(transactions, self.get_last_block_hash(), nonce) is False:
            nonce = random.randint(0, 100000000)
            transactions = self.get_transactions_for_next_block()

        return nonce, transactions

    def valid_proof(self, transactions, last_hash, nonce):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the
        proof_of_work function.
        """

        transactions_without_signature = self.get_transactions_without_signature(transactions)
        guess = (str(transactions_without_signature) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:self.DIFFICULTY] == "0" * self.DIFFICULTY

    def get_last_block_hash(self):
        last_block = self.session.query(Block).order_by(None).order_by(Block.timestamp.desc()).limit(1).all()
        if len(last_block) == 0:
            return ''
        return last_block[0].hash()
    def get_transactions_for_next_block(self):
        if self.BLOCK_SIZE is not None:
            return self.session.query(PendingTransaction).limit(self.BLOCK_SIZE).all()
        else:
            return self.session.query(PendingTransaction).all()
    def get_transactions_without_signature(self, transactions: List[PendingTransaction]):
        return [tx.get_representation_without_signature() for tx in transactions]