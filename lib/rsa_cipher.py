import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from lib.cipher import Cipher


class RsaCipher(Cipher):
    def get_key_pair(self):

        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()

        private_key = binascii.hexlify(private_key.exportKey(format="DER")).decode("ascii")
        public_key = binascii.hexlify(public_key.exportKey(format="DER")).decode("ascii")

        return private_key, public_key

    def sign(self, private_key: str, message: str):

        private_key = RSA.importKey(binascii.unhexlify(private_key))
        signer = pkcs1_15.new(private_key)
        message_hash = SHA256.new(message.encode("utf8"))
        print("Message to sign")
        print(message)
        print("Message hash")
        print(message_hash.__str__())
        signature = signer.sign(message_hash)

        return binascii.hexlify(signature).decode("ascii")

    def verify(self, public_key: bytes, message_hash: SHA256Hash, signature: str):

        verifier = pkcs1_15.new(RSA.importKey(public_key))
        print("Message hash")
        print(message_hash.__str__())
        return verifier.verify(message_hash, binascii.unhexlify(signature))