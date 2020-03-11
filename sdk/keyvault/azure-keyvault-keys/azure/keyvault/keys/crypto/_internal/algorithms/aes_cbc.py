# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from abc import abstractmethod

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from ..algorithm import SymmetricEncryptionAlgorithm
from ..transform import BlockCryptoTransform


class _AesCbcCryptoTransform(BlockCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcCryptoTransform, self).__init__(key)
        self._cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    def transform(self, data):
        return self.update(data) + self.finalize(data)

    @abstractmethod
    def block_size(self):
        pass


class _AesCbcDecryptor(_AesCbcCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcDecryptor, self).__init__(key, iv)
        self._ctx = self._cipher.decryptor()
        self._padder = padding.PKCS7(self.block_size).unpadder()

    def update(self, data):
        padded = self._ctx.update(data)
        return self._padder.update(padded)

    def finalize(self, data):
        padded = self._ctx.finalize()
        return self._padder.update(padded) + self._padder.finalize()

    @property
    def block_size(self):
        # return self._cipher.block_size
        raise NotImplementedError()


class _AesCbcEncryptor(_AesCbcCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcEncryptor, self).__init__(key, iv)
        self._ctx = self._cipher.encryptor()
        self._padder = padding.PKCS7(self.block_size).padder()

    def update(self, data):
        padded = self._padder.update(data)
        return self._ctx.update(padded)

    def finalize(self, data):
        padded = self._padder.finalize()
        return self._ctx.update(padded) + self._ctx.finalize()

    @property
    def block_size(self):
        # return self._cipher.block_size
        raise NotImplementedError()


class _AesCbc(SymmetricEncryptionAlgorithm):
    _key_size = 256
    _block_size = 128

    def block_size(self):
        return self._block_size

    def block_size_in_bytes(self):
        return self._block_size >> 3

    def key_size(self):
        return self._key_size

    def key_size_in_bytes(self):
        return self._key_size >> 3

    def create_encryptor(self, key, iv):
        key, iv = self._validate_input(key, iv)

        return _AesCbcEncryptor(key, iv)

    def create_decryptor(self, key, iv):
        key, iv = self._validate_input(key, iv)

        return _AesCbcDecryptor(key, iv)

    def _validate_input(self, key, iv):
        if not key:
            raise ValueError("key")
        if len(key) < self.key_size_in_bytes():
            raise ValueError("key must be at least %d bits" % self.key_size)

        if not iv:
            raise ValueError("iv")
        if not len(iv) == self.block_size_in_bytes():
            raise ValueError("iv must be %d bits" % self.block_size)

        return key[: self.key_size_in_bytes], iv


class Aes128Cbc(_AesCbc):
    _name = "A128CBC"
    _key_size = 128


class Aes192Cbc(_AesCbc):
    _name = "A192CBC"
    _key_size = 192


class Aes256Cbc(_AesCbc):
    _name = "A256CBC"
    _key_size = 256


Aes128Cbc.register()
Aes192Cbc.register()
Aes256Cbc.register()
