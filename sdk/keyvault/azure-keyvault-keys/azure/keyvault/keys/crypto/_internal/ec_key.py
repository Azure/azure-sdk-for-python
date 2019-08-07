#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import uuid
import os
from .key import Key
from .algorithms.ecdsa import Es256, Es512, Es384, Ecdsa256

_crypto_crv_to_kv_crv = {
    'secp256r1': 'P-256',
    'secp384r1': 'P-384',
    'secp521r1': 'P-521',
    'secp256k1': 'SECP256K1'
}
_kv_crv_to_crypto_crv = {
    'P-256': 'secp256r1',
    'P-384': 'secp384r1',
    'P-521': 'secp521r1',
    'SECP256K1': 'secp256k1'
}
_curve_to_default_algo = {
    'P-256': Es256.name(),
    'P-384': Es384.name(),
    'P-521': Es512.name(),
    'SECP256K1': Ecdsa256.name(),
}


class EllipticCurveKey(Key):
    def __init__(self, kid=None, curve=None):
        self._kid = kid or str(uuid.uuid4())
        self._default_algo = _curve_to_default_algo[curve]

    @staticmethod
    def from_jwk(jwk):
        pass

    def to_jwk(self, include_privates=False):
        pass

    @property
    def kid(self):
        return self._kid

    @property
    def default_signature_algorithm(self):
        return self._default_algo

    @property
    def supported_signature_algorithms(self):
        return [self.default_signature_algorithm]

    def sign(self, digest, **kwargs):
        raise NotImplementedError()

    def verify(self, digest, signature, **kwargs):
        raise NotImplementedError()
