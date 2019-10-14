# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm


class DecryptResult:
    """The result of a decrypt operation.

    :param bytes decrypted_bytes: The decrypted bytes
    """

    def __init__(self, decrypted_bytes):
        # type: (bytes) -> None
        self.decrypted_bytes = decrypted_bytes


class EncryptResult:
    """The result of an encrypt operation.

    :param str key_id: The encryption key's Key Vault identifier
    :param algorithm: The encryption algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.EncryptionAlgorithm
    :param bytes ciphertext: The encrypted bytes
    """

    def __init__(self, key_id, algorithm, ciphertext):
        # type: (str, EncryptionAlgorithm, bytes) -> None
        self.key_id = key_id
        self.algorithm = algorithm
        self.ciphertext = ciphertext


class SignResult:
    """The result of a sign operation.

    :param str key_id: The signing key's Key Vault identifier
    :param algorithm: The signature algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.SignatureAlgorithm
    :param bytes signature:
    """

    def __init__(self, key_id, algorithm, signature):
        # type: (str, SignatureAlgorithm, bytes) -> None
        self.key_id = key_id
        self.algorithm = algorithm
        self.signature = signature


class VerifyResult:
    """The result of a verify operation.

    :param bool result: Whether the signature is valid
    """

    def __init__(self, result):
        self.result = result


class UnwrapKeyResult:
    """The result of an unwrap key operation.

    :param bytes unwrapped_bytes: The unwrapped key's bytes
    """

    def __init__(self, unwrapped_bytes):
        self.unwrapped_bytes = unwrapped_bytes


class WrapKeyResult:
    """The result of a wrap key operation.

    :param str key_id: The wrapping key's Key Vault identifier
    :param algorithm: The key wrap algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.KeyWrapAlgorithm
    :param bytes encrypted_key: The encrypted key bytes
    """

    def __init__(self, key_id, algorithm, encrypted_key):
        # type: (str, KeyWrapAlgorithm, bytes) -> None
        self.key_id = key_id
        self.algorithm = algorithm
        self.encrypted_key = encrypted_key
