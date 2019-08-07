# ---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from six import with_metaclass
from .algorithm import Algorithm


class Key(with_metaclass(ABCMeta, object)):
    _supported_encryption_algorithms = []
    _supported_key_wrap_algorithms = []
    _supported_signature_algorithms = []

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
        return None

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

    @abstractmethod
    def sign_message(self, message, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def verify_message(self, message, signature, **kwargs):
        raise NotImplementedError()

    def _get_algorithm(self, op, **kwargs):
        default_algorithm, supported_alogrithms = {
            'encrypt': (self.default_encryption_algorithm, self.supported_encryption_algorithms),
            'decrypt': (self.default_encryption_algorithm, self.supported_encryption_algorithms),
            'wrapKey': (self.default_key_wrap_algorithm, self.supported_key_wrap_algorithms),
            'unwrapKey': (self.default_key_wrap_algorithm, self.supported_key_wrap_algorithms),
            'sign': (self.default_signature_algorithm, self.supported_signature_algorithms),
            'verify': (self.default_signature_algorithm, self.supported_signature_algorithms)
        }[op]

        algorithm = kwargs.get('algorithm', default_algorithm)

        if not isinstance(algorithm, Algorithm):
            algorithm = Algorithm.resolve(algorithm)

        if not algorithm or not supported_alogrithms or algorithm.name() not in supported_alogrithms:
            raise ValueError('invalid algorithm')
