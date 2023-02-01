import hashlib
import json
import os
from collections import OrderedDict
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import binascii
import random
from lib import RsaCipher, EccCipher, DilithiumCipher
from typing import List

from Crypto.Hash import SHA256
from flask import Flask

import requests

MINING_REWARD = 1
MINING_SENDER = "THE BLOCKCHAIN"
CHECKED_TRANSACTIONS = 0

cipher_algorithm = os.getenv("CIPHER")

if cipher_algorithm == "ecc":
    cipher = EccCipher()
elif cipher_algorithm == "rsa":
    cipher = RsaCipher()
elif cipher_algorithm == "dilithium":
    cipher = DilithiumCipher()
else:
    raise ValueError(cipher_algorithm + "is unknown")


class Blockchain(object):
    DIFFICULTY = 4
    BLOCK_SIZE = 9

    def __init__(self, app: Flask):
        self.app = app
        self.chain = []
        self.pending_transactions = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace("-", "")
        app.logger.info('before genesis block')
        self.add_block(0, "00", [])
        app.logger.info('after genesis block: ' +  self.chain.__str__())
        #self.mine()

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def get_difficulty(self) -> int:
        return self.DIFFICULTY

    def distribute_block(self):
        neighbours = self.nodes

        for node in neighbours:
            response = requests.get(f"http://{node}/nodes/resolve",
                                     headers={"Access-Control-Allow-Origin": "*"})
            if response.status_code != 200:
                raise ValueError("Other Node did not accept new block or has a longer chain!")

    def add_block(self, nonce: int, previous_hash: str, transactions: List):
        self.app.logger.info('ADD BLOCK')
        """
        Adds a new block to the chain
        :param transactions: <List> transactions to be added to this block
        :param nonce: <int> Nonce of the block
        :param previous_hash: <str> Hash of the previous block
        :return: <Block.__dict__> The added block in dict format
        """
        block = {
            "index": len(self.chain),
            "timestamp": time(),
            "transactions": transactions,
            "nonce": nonce,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }

        # Update pending transactions
        self.pending_transactions = list(
            filter(lambda t: t not in transactions, self.pending_transactions)
        )

        self.chain.append(block)
        self.distribute_block()

        return block

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

    @staticmethod
    def valid_proof(transactions, last_hash, nonce, difficulty=DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the
        proof_of_work function.
        """

        transactions_without_signature = Blockchain.get_transactions_without_signature(transactions)
        guess = (str(transactions_without_signature) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:difficulty] == "0" * difficulty

    def proof_of_work(self) -> (int, List):
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4
        zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof
        :return: <int>
        """
        nonce = 0
        transactions = self.get_transactions_for_next_block()
        while self.valid_proof(transactions, self.hash(self.last_block), nonce) is False:
            nonce = random.randint(0, 100000000)
            transactions = self.get_transactions_for_next_block()

        self.app.logger.info("nonce " + str(nonce))

        return nonce, transactions

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError("Invalid URL")

    def distribute_transaction(self, sender, receiver, amount, signature, timestamp):

        neighbours = self.nodes

        transaction = {"sender": sender, "receiver": receiver, "amount": amount, "signature": signature, "timestamp": timestamp}

        for node in neighbours:
            response = requests.post(f"http://{node}/transactions",
                                     json=transaction,
                                     headers={ "Access-Control-Allow-Origin": "*" })
            if response.status_code != 201:
                raise ValueError("Other Node did not accept transaction")

    @staticmethod
    def verify_transaction_signature(transaction, app):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        sender_address = binascii.unhexlify(transaction["sender"])
        signature = transaction["signature"]

        # create copy of transaction without its "signature"
        transaction = OrderedDict({
            "sender": transaction["sender"],
            "receiver": transaction["receiver"],
            "amount": transaction["amount"],
            "timestamp": transaction["timestamp"]
        })

        transaction_hash = SHA256.new(str(transaction).encode("utf8"))

        global CHECKED_TRANSACTIONS
        CHECKED_TRANSACTIONS = CHECKED_TRANSACTIONS + 1
        app.logger.info('Checked Transaction:' + CHECKED_TRANSACTIONS.__str__())
        return cipher.verify(public_key=sender_address,
                             message_hash=transaction_hash,
                             signature=signature)

    def submit_transaction(self, sender_address, receiver_address, amount, signature, timestamp):
        """Add a transaction to transactions array if the signature verified"""

        # TODO: check if transaction is already in chain?

        ta = OrderedDict(
            {
                "sender": sender_address,
                "receiver": receiver_address,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
            }
        )

        if ta in self.pending_transactions:
            return True

        if sender_address == MINING_SENDER:
            self.pending_transactions.append(ta)
            return len(self.chain) + 1
        else:
            try:
                self.verify_transaction_signature(ta, self.app)
                self.pending_transactions.append(ta)
                self.distribute_transaction(sender_address, receiver_address, amount, signature, timestamp)
                return True
            except ValueError:
                print("Signature not valid!")
                return False

    def valid_chain(self, chain) -> bool:
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]

            if current_block["previous_hash"] != self.hash(last_block):
                return False

            transactions = current_block["transactions"][:-1]

            # validate signature of each transaction
            try:
                for ta in transactions:
                    self.verify_transaction_signature(ta, self.app)
            except ValueError:
                print("given chain not valid: at least one transaction signature is invalid")
                return False

            # validate proof of work
            if not self.valid_proof(transactions,
                                    current_block["previous_hash"],
                                    current_block["nonce"]):
                print("given chain not valid: proof of work is invalid")
                return False

            last_block = current_block
            current_index += 1

        return True

    def update_pending_transactions(self):
        pending_transactions_copy = self.pending_transactions
        self.pending_transactions = []

        confirmed_transactions = []

        for index in range(1, len(self.chain)):
            block = self.chain[index]
            # reward should not be considered
            transactions = block["transactions"][:-1]

            confirmed_transactions.extend(transactions)

        # remove confirmed transactions from pending transactions
        self.pending_transactions = [t for t in pending_transactions_copy if t not in confirmed_transactions]

    def resolve_conflicts(self) -> bool:
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            self.update_pending_transactions()
            return True

        return False

    def generate_block_by_nounce(self, last_block, nonce, transactions: List):
        # We must receive a reward for finding the proof.
        reward_transaction = OrderedDict(
            {
                "sender": MINING_SENDER,
                "receiver": self.node_id,
                "amount": MINING_REWARD,
                "timestamp": time(),
                "signature": "",
            }
        )
        transactions.append(reward_transaction)

        # Forge the new Block by adding it to the chain
        previous_hash = self.hash(last_block)
        block = self.add_block(nonce, previous_hash, transactions)

        return {
            "message": "New Block Forged",
            "block_number": block["index"],
            "transactions": block["transactions"],
            "nonce": block["nonce"],
            "previous_hash": block["previous_hash"],
        }

    def get_transactions_for_next_block(self):
        return self.pending_transactions[:self.BLOCK_SIZE]

    @staticmethod
    def get_transactions_without_signature(transactions):
        return list(map(lambda t: OrderedDict({
            "sender": t["sender"],
            "receiver": t["receiver"],
            "amount": t["amount"],
            "timestamp": t["timestamp"]
        }), transactions))


