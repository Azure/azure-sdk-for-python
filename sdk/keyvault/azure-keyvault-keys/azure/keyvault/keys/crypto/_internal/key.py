# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from abc import ABCMeta, abstractmethod
from six import with_metaclass
from .algorithm import Algorithm

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, FrozenSet

class Key(with_metaclass(ABCMeta, object)):
    _supported_encryption_algorithms = frozenset([])  # type: FrozenSet[Any]
    _supported_key_wrap_algorithms = frozenset([])  # type: FrozenSet[Any]
    _supported_signature_algorithms = frozenset([])  # type: FrozenSet[Any]

    def __init__(self):
        self._kid = None

    @property
    def default_encryption_algorithm(self):
        return None

    @property
    def default_key_wrap_algorithm(self):
        return None

    @property
    def default_signature_algorithm(self):
        return None

    @property
    def supported_encryption_algorithms(self):
        return self._supported_encryption_algorithms

    @property
    def supported_key_wrap_algorithms(self):
        return self._supported_key_wrap_algorithms

    @property
    def supported_signature_algorithms(self):
        return self._supported_signature_algorithms

    @property
    def kid(self):
        return self._kid

    @abstractmethod
    def is_private_key(self):
        pass

    @abstractmethod
    def decrypt(self, cipher_text, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def encrypt(self, plain_text, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def wrap_key(self, key, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def unwrap_key(self, encrypted_key, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def sign(self, digest, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def verify(self, digest, signature, **kwargs):
        raise NotImplementedError()

    def _get_algorithm(self, op, **kwargs):
        default_algorithm, supported_algorithms = {
            "encrypt": (self.default_encryption_algorithm, self.supported_encryption_algorithms),
            "decrypt": (self.default_encryption_algorithm, self.supported_encryption_algorithms),
            "wrapKey": (self.default_key_wrap_algorithm, self.supported_key_wrap_algorithms),
            "unwrapKey": (self.default_key_wrap_algorithm, self.supported_key_wrap_algorithms),
            "sign": (self.default_signature_algorithm, self.supported_signature_algorithms),
            "verify": (self.default_signature_algorithm, self.supported_signature_algorithms),
        }[op]

        algorithm = kwargs.get("algorithm", default_algorithm)

        if not isinstance(algorithm, Algorithm):
            algorithm = Algorithm.resolve(algorithm)

        if not algorithm or not supported_algorithms or algorithm.name() not in supported_algorithms:
            raise ValueError("unsupported algorithm '{}'".format(algorithm))

        return algorithm
