# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from abc import abstractmethod

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Optional, Union
    from cryptography.hazmat.primitives import hashes

_alg_registry = {}


class Algorithm(object):
    _name = None  # type: Optional[str]

    @classmethod
    def name(cls):
        return cls._name

    @classmethod
    def register(cls):
        _alg_registry[cls._name] = cls

    @staticmethod
    def resolve(name):
        if name not in _alg_registry:
            return None
        return _alg_registry[name]()


class AsymmetricEncryptionAlgorithm(Algorithm):
    @abstractmethod
    def create_encryptor(self, key):
        raise NotImplementedError()

    @abstractmethod
    def create_decryptor(self, key):
        raise NotImplementedError()


class SymmetricEncryptionAlgorithm(Algorithm):
    @abstractmethod
    def create_encryptor(self, key, iv):
        raise NotImplementedError()

    @abstractmethod
    def create_decryptor(self, key, iv):
        raise NotImplementedError()


class AuthenticatedSymmetricEncryptionAlgorithm(Algorithm):
    @abstractmethod
    def create_encryptor(self, key, iv, auth_data, auth_tag):
        raise NotImplementedError()

    @abstractmethod
    def create_decryptor(self, key, iv, auth_data, auth_tag):
        raise NotImplementedError()


class SignatureAlgorithm(Algorithm):
    _default_hash_algorithm = None  # type: Union[hashes.SHA256, hashes.SHA384, hashes.SHA512, None]

    @property
    def default_hash_algorithm(self):
        return self._default_hash_algorithm

    @abstractmethod
    def create_signature_transform(self, key):
        raise NotImplementedError()


class HashAlgorithm(Algorithm):
    @abstractmethod
    def create_digest(self):
        raise NotImplementedError()
