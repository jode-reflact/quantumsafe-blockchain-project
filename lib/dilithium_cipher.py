import binascii
import oqs
from Crypto.Hash import SHA256
from Crypto.Hash.SHA256 import SHA256Hash

from lib.cipher import Cipher


class DilithiumCipher(Cipher):
    NIST_LEVEL = "Dilithium3"

    def get_key_pair(self):

        signer = oqs.Signature(self.NIST_LEVEL)
        public_key = signer.generate_keypair()
        private_key = signer.export_secret_key()

        private_key = binascii.hexlify(private_key.exportKey(format="DER")).decode("ascii")
        public_key = binascii.hexlify(public_key.exportKey(format="DER")).decode("ascii")

        return private_key, public_key

    def sign(self, private_key: str, message: str):

        private_key = binascii.unhexlify(private_key)
        signer = oqs.Signature(self.NIST_LEVEL, private_key)
        message_hash = SHA256.new(message.encode("utf8"))
        signature = signer.sign(message_hash)

        return binascii.hexlify(signature).decode("ascii")

    def verify(self, public_key: str, message_hash: SHA256Hash, signature: str):
        verifier = oqs.Signature(self.NIST_LEVEL)
        return verifier.verify(message_hash, binascii.unhexlify(signature))