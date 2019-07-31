# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

EncryptResult = namedtuple("EncryptResult", ["key_id", "algorithm", "ciphertext", "authentication_tag"])
SignResult = namedtuple("SignResult", ["key_id", "algorithm", "signature"])
WrapKeyResult = namedtuple("WrapKeyResult", ["key_id", "algorithm", "encrypted_key"])

from .client import CryptographyClient
from .enums import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm


__all__ = [
    "CryptographyClient",
    "EncryptionAlgorithm",
    "EncryptResult",
    "KeyWrapAlgorithm",
    "SignatureAlgorithm",
    "SignResult",
    "WrapKeyResult",
]
