import hashlib
import json
from collections import OrderedDict
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from typing import List
import binascii
import random

from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import pkcs1_15, DSS

import requests

import oqs

MINING_REWARD = 1
MINING_SENDER = "THE BLOCKCHAIN"


class Blockchain(object):
    DIFFICULTY = 6

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace("-", "")
        self.add_block(0, "00")

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

    def add_block(self, nonce: int, previous_hash: str):
        """
        Adds a new block to the chain
        :param nonce: <int> Nonce of the block
        :param previous_hash: <str> Hash of the previous block
        :return: <Block.__dict__> The added block in dict format
        """
        block = {
            "index": len(self.chain),
            "timestamp": time(),
            "transactions": self.pending_transactions,
            "nonce": nonce,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.pending_transactions = []

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
        while self.valid_proof(self.get_pending_transactions_without_signature(), last_hash, nonce) is False:
            # lieber random zahl nehmen
            # welche obere grenze?
            nonce = random.randint(0, 100000000)
            #nonce += 1

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
    def verify_transaction_signature(parsed_sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        sender_address = binascii.unhexlify(parsed_sender_address)

        # create copy of transaction without its "signature"
        transaction = OrderedDict({
            "sender": transaction["sender"],
            "receiver": transaction["receiver"],
            "amount": transaction["amount"],
            "timestamp": transaction["timestamp"]
        })

        #################################
        ##### RSA
        # public_key = RSA.importKey(sender_address)
        # verifier = pkcs1_15.new(public_key)
        # transaction_hash = SHA1.new(str(transaction).encode("utf8"))

        ######################
        ###### DILITHIUM ####
        #
        dilithium_algo = "Dilithium2"
        verifier = oqs.Signature(dilithium_algo)
        public_key = sender_address
        transaction_hash = SHA256.new(str(transaction).encode("utf8"))
        #return verifier.verify(transaction_hash, binascii.unhexlify(signature), public_key)
        return verifier.verify(str(transaction_hash.hexdigest()).encode("utf8"), binascii.unhexlify(signature), public_key)

        ########################
        ## ECC
        # public_key = ECC.import_key(sender_address)
        # verifier = DSS.new(public_key, "fips-186-3")
        # transaction_hash = SHA256.new(str(transaction).encode("utf8"))

        # return verifier.verify(transaction_hash, binascii.unhexlify(signature))

    def submit_transaction(self, sender_address, receiver_address, amount, signature, timestamp):
        """Add a transaction to transactions array if the signature verified"""
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
                self.verify_transaction_signature(sender_address, signature, ta)
                self.pending_transactions.append(ta)
                self.distribute_transaction(sender_address, receiver_address, amount, signature,timestamp)
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
            transaction_elements = ["sender", "receiver", "amount",  "timestamp"]
            transactions = [
                OrderedDict((k, transaction[k]) for k in transaction_elements)
                for transaction in transactions
            ]

            if not self.valid_proof(transactions,
                                    current_block["previous_hash"],
                                    current_block["nonce"]):
                print("given chain not valid")
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
            self.pending_transactions = []
            return True

        return False

    def get_pending_transactions_without_signature(self):
        return list(map(lambda t: OrderedDict({
            "sender": t["sender"],
            "receiver": t["receiver"],
            "amount": t["amount"],
            "timestamp": t["timestamp"]
        }), self.pending_transactions))
