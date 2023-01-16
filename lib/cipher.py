from abc import abstractmethod, ABC

class Cipher(ABC):
    @abstractmethod
    def get_key_pair(self):
        pass

    @abstractmethod
    def sign(self, private_key: str, message: str):
        pass

    @abstractmethod
    def verify(self, public_key: str, transaction_hash: str, signature: str):
        pass