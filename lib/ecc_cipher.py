import binascii
from Crypto.Hash import SHA256
from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

from lib.cipher import Cipher


class EccCipher(Cipher):
    def get_key_pair(self):

        private_key = ECC.generate(curve='P-256')
        public_key = private_key.public_key()

        private_key = binascii.hexlify(private_key.export_key(format='DER')).decode("ascii")
        public_key = binascii.hexlify(public_key.export_key(format='DER')).decode("ascii")

        return private_key, public_key

    def sign(self, private_key: str, message: str):

        private_key = ECC.import_key(binascii.unhexlify(private_key))
        signer = DSS.new(private_key, "fips-186-3")
        message_hash = SHA256.new(message.encode("utf8"))
        signature = signer.sign(message_hash)

        return binascii.hexlify(signature).decode("ascii")

    def verify(self, public_key: str, message_hash: SHA256Hash, signature: str):

        verifier = DSS.new(ECC.import_key(public_key), "fips-186-3")
        return verifier.verify(message_hash, binascii.unhexlify(signature))