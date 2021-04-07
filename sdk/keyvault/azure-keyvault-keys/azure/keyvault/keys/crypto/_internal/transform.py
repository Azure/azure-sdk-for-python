# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from abc import ABCMeta, abstractmethod
from six import with_metaclass


class CryptoTransform(with_metaclass(ABCMeta, object)):
    def __init__(self, key):
        self._key = key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._key = None

    @abstractmethod
    def transform(self, data):
        raise NotImplementedError()


class BlockCryptoTransform(CryptoTransform):
    @abstractmethod
    def block_size(self):
        raise NotImplementedError()

    @abstractmethod
    def update(self, data):
        raise NotImplementedError()

    @abstractmethod
    def finalize(self):
        raise NotImplementedError()


class AuthenticatedCryptoTransform(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def tag(self):
        raise NotImplementedError()


class SignatureTransform(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def sign(self, digest):
        raise NotImplementedError()

    @abstractmethod
    def verify(self, digest, signature):
        raise NotImplementedError()


class DigestTransform(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def update(self, data):
        raise NotImplementedError()

    @abstractmethod
    def finalize(self, data):
        raise NotImplementedError()
