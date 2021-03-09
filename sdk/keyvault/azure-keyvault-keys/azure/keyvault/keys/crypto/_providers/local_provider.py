# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
from typing import TYPE_CHECKING

from azure.core.exceptions import AzureError

from .. import DecryptResult, EncryptResult, SignResult, UnwrapResult, VerifyResult, WrapResult
from ... import KeyOperation

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Union
    from .._internal.key import Key
    from .. import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm
    from ... import JsonWebKey

    Algorithm = Union[EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm]


class LocalCryptographyProvider(ABC):
    def __init__(self, key):
        # type: (JsonWebKey, **Any) -> None
        self._allowed_ops = frozenset(key.key_ops or [])
        self._internal_key = self._get_internal_key(key)
        self._key = key

    @abc.abstractmethod
    def _get_internal_key(self, key):
        # type: (JsonWebKey) -> Key
        pass

    @abc.abstractmethod
    def supports(self, operation, algorithm):
        # type: (KeyOperation, Algorithm) -> bool
        pass

    @property
    def key_id(self):
        # type: () -> Optional[str]
        """The full identifier of the provider's key.

        :rtype: str or None
        """
        return self._key.kid

    def _raise_if_unsupported(self, operation, algorithm):
        # type: (KeyOperation, Algorithm) -> None
        if not self.supports(operation, algorithm):
            raise NotImplementedError(
                'This key does not support the "{}" operation with algorithm "{}"'.format(operation, algorithm)
            )
        if operation not in self._allowed_ops:
            raise AzureError('This key does not allow the "{}" operation'.format(operation))

    def encrypt(self, algorithm, plaintext):
        # type: (EncryptionAlgorithm, bytes) -> EncryptResult
        self._raise_if_unsupported(KeyOperation.encrypt, algorithm)
        ciphertext = self._internal_key.encrypt(plaintext, algorithm=algorithm.value)
        return EncryptResult(key_id=self._key.kid, algorithm=algorithm, ciphertext=ciphertext)

    def decrypt(self, algorithm, ciphertext):
        # type: (EncryptionAlgorithm, bytes) -> DecryptResult
        self._raise_if_unsupported(KeyOperation.decrypt, algorithm)
        plaintext = self._internal_key.decrypt(ciphertext, iv=None, algorithm=algorithm.value)
        return DecryptResult(key_id=self._key.kid, algorithm=algorithm, plaintext=plaintext)

    def wrap_key(self, algorithm, key):
        # type: (KeyWrapAlgorithm, bytes) -> WrapResult
        self._raise_if_unsupported(KeyOperation.wrap_key, algorithm)
        encrypted_key = self._internal_key.wrap_key(key, algorithm=algorithm.value)
        return WrapResult(key_id=self._key.kid, algorithm=algorithm, encrypted_key=encrypted_key)

    def unwrap_key(self, algorithm, encrypted_key):
        # type: (KeyWrapAlgorithm, bytes) -> UnwrapResult
        self._raise_if_unsupported(KeyOperation.unwrap_key, algorithm)
        unwrapped_key = self._internal_key.unwrap_key(encrypted_key, algorithm=algorithm.value)
        return UnwrapResult(key_id=self._key.kid, algorithm=algorithm, key=unwrapped_key)

    def sign(self, algorithm, digest):
        # type: (SignatureAlgorithm, bytes) -> SignResult
        self._raise_if_unsupported(KeyOperation.sign, algorithm)
        signature = self._internal_key.sign(digest, algorithm=algorithm.value)
        return SignResult(key_id=self._key.kid, algorithm=algorithm, signature=signature)

    def verify(self, algorithm, digest, signature):
        # type: (SignatureAlgorithm, bytes, bytes) -> VerifyResult
        self._raise_if_unsupported(KeyOperation.verify, algorithm)
        is_valid = self._internal_key.verify(digest, signature, algorithm=algorithm.value)
        return VerifyResult(key_id=self._key.kid, algorithm=algorithm, is_valid=is_valid)
