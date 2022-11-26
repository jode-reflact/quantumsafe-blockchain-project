from dataclasses import dataclass
from .transaction import Transaction


@dataclass
class Block:
    index: int
    timestamp: float
    nonce: int
    previous_hash: str
    transactions: list[Transaction.__dict__]
