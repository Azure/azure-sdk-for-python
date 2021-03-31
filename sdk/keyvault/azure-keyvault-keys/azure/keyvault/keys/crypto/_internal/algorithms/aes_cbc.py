# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from ..algorithm import SymmetricEncryptionAlgorithm
from ..transform import BlockCryptoTransform


_CBC_BLOCK_SIZE = 128


class _AesCbcCryptoTransform(BlockCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcCryptoTransform, self).__init__(key)
        self._cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    def transform(self, data):
        return self.update(data) + self.finalize()
    
    def block_size(self):
        return _CBC_BLOCK_SIZE


class _AesCbcDecryptor(_AesCbcCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcDecryptor, self).__init__(key, iv)
        self._ctx = self._cipher.decryptor()
        self._padder = padding.ANSIX923(_CBC_BLOCK_SIZE).unpadder()  # TODO: Update this to zero-padding

    def update(self, data):
        decrypted = self._ctx.update(data) + self._ctx.finalize()
        return self._padder.update(decrypted)

    def finalize(self):
        return self._padder.finalize()


class _AesCbcPadDecryptor(_AesCbcCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcPadDecryptor, self).__init__(key, iv)
        self._ctx = self._cipher.decryptor()
        self._padder = padding.PKCS7(_CBC_BLOCK_SIZE).unpadder()

    def update(self, data):
        decrypted = self._ctx.update(data) + self._ctx.finalize()
        return self._padder.update(decrypted)

    def finalize(self):
        return self._padder.finalize()


class _AesCbcEncryptor(_AesCbcCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcEncryptor, self).__init__(key, iv)
        self._ctx = self._cipher.encryptor()
        self._padder = padding.ANSIX923(_CBC_BLOCK_SIZE).padder()  # TODO: Update this to zero-padding

    def update(self, data):
        padded = self._padder.update(data) + self._padder.finalize()
        return self._ctx.update(padded)

    def finalize(self):
        return self._ctx.finalize()


class _AesCbcPadEncryptor(_AesCbcCryptoTransform):
    def __init__(self, key, iv):
        super(_AesCbcPadEncryptor, self).__init__(key, iv)
        self._ctx = self._cipher.encryptor()
        self._padder = padding.PKCS7(_CBC_BLOCK_SIZE).padder()

    def update(self, data):
        padded = self._padder.update(data) + self._padder.finalize()
        return self._ctx.update(padded)

    def finalize(self):
        return self._ctx.finalize()


class _AesCbc(SymmetricEncryptionAlgorithm):
    _key_size = 256
    _block_size = _CBC_BLOCK_SIZE

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
            raise ValueError("A key is required for AES-CBC and AES-CBCPAD encryption and decryption")
        if len(key) < self.key_size_in_bytes():
            raise ValueError("key must be at least %d bits" % self.key_size)

        if not iv:
            raise ValueError("A 16-byte iv is required for AES-CBC and AES-CBCPAD encryption and decryption")
        if not len(iv) == self.block_size_in_bytes():
            raise ValueError("iv must be %d bits" % self.block_size)

        return key[: self.key_size_in_bytes()], iv


class _AesCbcPad(_AesCbc):
    def create_encryptor(self, key, iv):
        key, iv = self._validate_input(key, iv)

        return _AesCbcPadEncryptor(key, iv)

    def create_decryptor(self, key, iv):
        key, iv = self._validate_input(key, iv)

        return _AesCbcPadDecryptor(key, iv)


class Aes128Cbc(_AesCbc):
    _name = "A128CBC"
    _key_size = 128


class Aes128CbcPad(_AesCbcPad):
    _name = "A128CBCPAD"
    _key_size = 128


class Aes192Cbc(_AesCbc):
    _name = "A192CBC"
    _key_size = 192


class Aes192CbcPad(_AesCbcPad):
    _name = "A192CBCPAD"
    _key_size = 192


class Aes256Cbc(_AesCbc):
    _name = "A256CBC"
    _key_size = 256


class Aes256CbcPad(_AesCbcPad):
    _name = "A256CBCPAD"
    _key_size = 256


Aes128Cbc.register()
Aes128CbcPad.register()
Aes192Cbc.register()
Aes192CbcPad.register()
Aes256Cbc.register()
Aes256CbcPad.register()
