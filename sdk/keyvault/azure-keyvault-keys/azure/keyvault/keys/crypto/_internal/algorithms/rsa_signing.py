# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, utils

from ..algorithm import SignatureAlgorithm
from ..transform import SignatureTransform


class RsaSignatureTransform(SignatureTransform):
    def __init__(self, key, padding_function, hash_algorithm):
        self._key = key
        self._padding_function = padding_function
        self._hash_algorithm = hash_algorithm

    def sign(self, digest):
        return self._key.sign(digest, self._padding_function(digest), self._hash_algorithm)

    def verify(self, digest, signature):
        self._key.verify(signature, digest, self._padding_function(digest), utils.Prehashed(self._hash_algorithm))


class RsaSsaPkcs1v15(SignatureAlgorithm):
    def create_signature_transform(self, key):
        return RsaSignatureTransform(key, lambda _: padding.PKCS1v15(), self._default_hash_algorithm)


class RsaSsaPss(SignatureAlgorithm):
    def create_signature_transform(self, key):
        return RsaSignatureTransform(key, self._get_padding, self._default_hash_algorithm)

    def _get_padding(self, digest):
        return padding.PSS(mgf=padding.MGF1(self._default_hash_algorithm), salt_length=len(digest))


class Ps256(RsaSsaPss):
    _name = "PS256"
    _default_hash_algorithm = hashes.SHA256()


class Ps384(RsaSsaPss):
    _name = "PS384"
    _default_hash_algorithm = hashes.SHA384()


class Ps512(RsaSsaPss):
    _name = "PS512"
    _default_hash_algorithm = hashes.SHA512()


class Rs256(RsaSsaPkcs1v15):
    _name = "RS256"
    _default_hash_algorithm = hashes.SHA256()


class Rs384(RsaSsaPkcs1v15):
    _name = "RS384"
    _default_hash_algorithm = hashes.SHA384()


class Rs512(RsaSsaPkcs1v15):
    _name = "RS512"
    _default_hash_algorithm = hashes.SHA512()


Ps256.register()
Ps384.register()
Ps512.register()
Rs256.register()
Rs384.register()
Rs512.register()
