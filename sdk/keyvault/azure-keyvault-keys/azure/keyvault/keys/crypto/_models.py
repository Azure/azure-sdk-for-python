# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm
    from typing import Any


class DecryptResult:
    """The result of a decrypt operation.

    :param str key_id: The encryption key's Key Vault identifier
    :param algorithm: The encryption algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.EncryptionAlgorithm
    :param bytes plaintext: The decrypted bytes
    """

    def __init__(self, key_id, algorithm, plaintext):
        # type: (str, EncryptionAlgorithm, bytes) -> None
        self.key_id = key_id
        self.algorithm = algorithm
        self.plaintext = plaintext


class EncryptResult:
    """The result of an encrypt operation.

    :param str key_id: The encryption key's Key Vault identifier
    :param algorithm: The encryption algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.EncryptionAlgorithm
    :param bytes ciphertext: The encrypted bytes
    :keyword bytes iv: Initialization vector for symmetric algorithms
    :keyword bytes authentication_tag: The tag to authenticate when performing decryption with an authenticated
        algorithm
    :keyword bytes additional_authenticated_data: Additional data to authenticate but not encrypt/decrypt when using an
        authenticated algorithm
    """

    def __init__(self, key_id, algorithm, ciphertext, **kwargs):
        # type: (str, EncryptionAlgorithm, bytes, **Any) -> None
        self.key_id = key_id
        self.algorithm = algorithm
        self.ciphertext = ciphertext
        self.iv = kwargs.pop("iv", None)
        self.tag = kwargs.pop("authentication_tag", None)
        self.aad = kwargs.pop("additional_authenticated_data", None)


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

    :param str key_id: The signing key's Key Vault identifier
    :param bool is_valid: Whether the signature is valid
    :param algorithm: The signature algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.SignatureAlgorithm
    """

    def __init__(self, key_id, is_valid, algorithm):
        # type: (str, bool, SignatureAlgorithm) -> None
        self.key_id = key_id
        self.is_valid = is_valid
        self.algorithm = algorithm


class UnwrapResult:
    """The result of an unwrap key operation.

    :param str key_id: Key encryption key's Key Vault identifier
    :param algorithm: The key wrap algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.KeyWrapAlgorithm
    :param bytes key: The unwrapped key
    """

    def __init__(self, key_id, algorithm, key):
        # type: (str, KeyWrapAlgorithm, bytes) -> None
        self.key_id = key_id
        self.algorithm = algorithm
        self.key = key


class WrapResult:
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
