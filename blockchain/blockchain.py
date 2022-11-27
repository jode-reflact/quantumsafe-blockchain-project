import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from typing import List
import binascii

from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import pkcs1_15, DSS

import requests

from .block import Block
from .transaction import Transaction

MINING_REWARD = 1
MINING_SENDER = "THE BLOCKCHAIN"


class Blockchain(object):
    DIFFICULTY = 2

    def __init__(self):
        self.chain: List[Block.__dict__] = []
        self.pending_transactions: List[Transaction.__dict__] = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace("-", "")
        self.add_block(0, "00")

    @property
    def last_block(self) -> Block.__dict__:
        return self.chain[-1]

    @property
    def get_difficulty(self) -> int:
        return self.DIFFICULTY

    def add_block(self, nonce: int, previous_hash: str):
        """
        Adds a new block to the chain
        :param nonce: <int> Nonce of the block
        :param previous_hash: <str> Hash of the previous block
        :return: <Block.__dict__> The added block in dict format
        """
        block = Block(
            index=len(self.chain),
            nonce=nonce,
            timestamp=time(),
            transactions=self.pending_transactions,
            previous_hash=previous_hash
        )

        # Reset the current list of transactions
        self.pending_transactions = []

        self.chain.append(block.__dict__)
        return block.__dict__

    def add_transaction(self, sender: str, receiver: str, amount: int):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param receiver: <str> Address of the receiver
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        ta = Transaction(sender, receiver, amount)
        self.pending_transactions.append(ta.__dict__)

        return self.last_block["index"] + 1

    @staticmethod
    def hash(block: Block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        print(block)
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        return hex_hash

    @staticmethod
    def valid_proof(pending_transactions, last_hash, nonce, difficulty=DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the
        proof_of_work function.
        """
        guess = (str(pending_transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:difficulty] == "0" * difficulty

    def proof_of_work(self) -> int:
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4
        zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof
        :return: <int>
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.pending_transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

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

    @staticmethod
    def verify_transaction_signature(parsed_sender_address, signature,
                                     transaction: Transaction.__dict__):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        sender_address = binascii.unhexlify(parsed_sender_address)

        # public_key = RSA.importKey(sender_address)
        # verifier = pkcs1_15.new(public_key)
        # transaction_hash = SHA1.new(str(transaction).encode("utf8"))

        public_key = ECC.import_key(sender_address)
        verifier = DSS.new(public_key, "fips-186-3")
        transaction_hash = SHA256.new(str(transaction).encode("utf8"))

        return verifier.verify(transaction_hash, binascii.unhexlify(signature))

    def submit_transaction(self, sender_address, receiver_address, amount, signature):
        """Add a transaction to transactions array if the signature verified"""
        ta = Transaction(sender_address, receiver_address, amount).__dict__

        if sender_address == MINING_SENDER:
            self.pending_transactions.append(ta)
            return len(self.chain) + 1
        else:
            try:
                self.verify_transaction_signature(sender_address, signature, ta)
                self.add_transaction(sender_address, receiver_address, amount)
                return True
            except ValueError:
                print("Signature not valid!")
                return False

    def valid_chain(self, chain: List[Block]) -> bool:
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]

            if current_block.previous_hash != self.hash(last_block):
                return False

            if not self.valid_proof(current_block.transactions,
                                    current_block.previous_hash,
                                    current_block.nonce):
                return False

            last_block = current_block
            current_index += 1

        return True

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
            return True

        return False
