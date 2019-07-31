# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

DecryptResult = namedtuple("DecryptResult", ["decrypted_bytes"])
EncryptResult = namedtuple("EncryptResult", ["key_id", "algorithm", "ciphertext", "authentication_tag"])
SignResult = namedtuple("SignResult", ["key_id", "algorithm", "signature"])
VerifyResult = namedtuple("VerifyResult", ["result"])
UnwrapKeyResult = namedtuple("UnwrapKeyResult", ["unwrapped_bytes"])
WrapKeyResult = namedtuple("WrapKeyResult", ["key_id", "algorithm", "encrypted_key"])

from .client import CryptographyClient
from .enums import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm


__all__ = [
    "CryptographyClient",
    "DecryptResult",
    "EncryptionAlgorithm",
    "EncryptResult",
    "KeyWrapAlgorithm",
    "SignatureAlgorithm",
    "SignResult",
    "UnwrapKeyResult",
    "VerifyResult",
    "WrapKeyResult",
]
