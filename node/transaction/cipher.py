import os
from lib import EccCipher, RsaCipher, DilithiumCipher

cipher_algorithm = os.getenv("CIPHER")
#cipher_algorithm = "ecc"

if cipher_algorithm == "ecc":
    cipher = EccCipher()
elif cipher_algorithm == "rsa":
    cipher = RsaCipher()
elif cipher_algorithm == "dilithium":
    cipher = DilithiumCipher()
else:
    raise ValueError(cipher_algorithm + "is unknown")