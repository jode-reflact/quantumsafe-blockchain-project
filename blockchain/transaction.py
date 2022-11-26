from dataclasses import dataclass


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
