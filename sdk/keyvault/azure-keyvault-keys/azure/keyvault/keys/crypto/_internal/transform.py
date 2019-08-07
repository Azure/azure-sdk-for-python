# ---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from six import with_metaclass


class CryptoTransform(with_metaclass(ABCMeta, object)):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._key = None

    @abstractmethod
    def transform(self, data):
        raise NotImplementedError()

    def dispose(self):
        return None


class BlockCryptoTransform(CryptoTransform):
    @abstractmethod
    def block_size(self):
        raise NotImplementedError()

    @abstractmethod
    def update(self, data):
        raise NotImplementedError()

    @abstractmethod
    def finalize(self, data):
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

    @abstractmethod
    def sign_message(self, message):
        raise NotImplementedError()

    @abstractmethod
    def verify_message(self, message, signature):
        raise NotImplementedError()


class DigestTransform(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def update(self, data):
        raise NotImplementedError()

    @abstractmethod
    def finalize(self, data):
        raise NotImplementedError()