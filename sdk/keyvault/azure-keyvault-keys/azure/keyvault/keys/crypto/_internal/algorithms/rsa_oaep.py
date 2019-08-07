from ..algorithm import EncryptionAlgorithm
from ..transform import CryptoTransform
from abc import ABCMeta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def _default_encryption_padding():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None)


class _RsaCryptoTransform(CryptoTransform):
    def __init__(self, key):
        self._key = key

    def dispose(self):
        self._key = None


class _RsaOaepDecryptor(_RsaCryptoTransform):
    def transform(self, data, **kwargs):
        self._key.decrypt(data, _default_encryption_padding())


class _RsaOaepEncryptor(_RsaCryptoTransform):
    def transform(self, data, **kwargs):
        self._key.encrypt(data, _default_encryption_padding())


class RsaOaep(EncryptionAlgorithm):
    _name = 'RSA-OAEP'

    def create_encryptor(self, key):
        return _RsaCryptoTransform(key)

    def create_decryptor(self, key):
        return _RsaOaepDecryptor(key)


RsaOaep.register()
