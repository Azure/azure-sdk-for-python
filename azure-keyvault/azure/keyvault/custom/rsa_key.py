#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import codecs
import json
import cryptography
import uuid
from ..models import JsonWebKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers, \
    generate_private_key, rsa_crt_dmp1, rsa_crt_dmq1, rsa_crt_iqmp, RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from .internal import _int_to_bytes, _bytes_to_int


def _default_encryption_padding():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None)


def _default_signature_padding():
    return padding.PKCS1v15()


def _default_signature_algorithm():
    return hashes.SHA256()

class RsaKey(object):
    PUBLIC_KEY_DEFAULT_OPS = ['encrypt', 'wrapKey', 'verify']
    PRIVATE_KEY_DEFAULT_OPS = ['encrypt', 'decrypt', 'wrapKey', 'unwrapKey', 'verify', 'sign']

    def __init__(self):
        self.kid = None
        self.kty = None
        self.key_ops = None
        self._rsa_impl = None

    @property
    def n(self):
        return _int_to_bytes(self._public_key_material().n)

    @property
    def e(self):
        return _int_to_bytes(self._public_key_material().e)

    @property
    def q(self):
        return _int_to_bytes(self._private_key_material().q) if self.is_private_key() else None

    @property
    def b(self):
        return _int_to_bytes(self._private_key_material().b) if self.is_private_key() else None

    @property
    def d(self):
        return _int_to_bytes(self._private_key_material().d) if self.is_private_key() else None

    @property
    def dq(self):
        return _int_to_bytes(self._private_key_material().dmq1) if self.is_private_key() else None

    @property
    def dp(self):
        return _int_to_bytes(self._private_key_material().dmp1) if self.is_private_key() else None

    @property
    def qi(self):
        return _int_to_bytes(self._private_key_material().iqmp) if self.is_private_key() else None

    @property
    def private_key(self):
        return self._rsa_impl if self.is_private_key() else None

    @property
    def public_key(self):
        return self._rsa_impl.public_key() if self.is_private_key() else self._rsa_impl

    @staticmethod
    def generate(kid=None, kty='RSA', size=2048, e=65537):
        key = RsaKey()
        key.kid = kid or str(uuid.uuid4())
        key.kty = kty
        key.key_ops = RsaKey.PRIVATE_KEY_DEFAULT_OPS
        key._rsa_impl = generate_private_key(public_exponent=e, key_size=size, backend=cryptography.hazmat.backends.default_backend())

        # set the appropriate callbacks for retrieving the public and private key material
        key._private_key_material = key._rsa_impl.private_numbers
        key._public_key_material = key._rsa_impl.public_key().public_numbers

        return key

    @staticmethod
    def from_jwk_str(s):
        jwk_dict = json.loads(s)
        jwk = JsonWebKey.from_dict(jwk_dict)
        return RsaKey.from_jwk(jwk)

    @staticmethod
    def from_jwk(jwk):
        if not isinstance(jwk, JsonWebKey):
            raise TypeError('The specified jwk must be a JsonWebKey')

        if jwk.kty != 'RSA' and jwk.kty != 'RSA-HSM':
            raise ValueError('The specified jwk must have a key type of "RSA" or "RSA-HSM"')

        if not jwk.n or not jwk.e:
            raise ValueError('Invalid RSA jwk, both n and e must be have values')

        rsa_key = RsaKey()
        rsa_key.kid = jwk.kid
        rsa_key.kty = jwk.kty
        rsa_key.key_ops = jwk.key_ops

        pub = RSAPublicNumbers(n=_bytes_to_int(jwk.n), e=_bytes_to_int(jwk.e))

        # if the private key values are specified construct a private key
        # only the secret primes and private exponent are needed as other fields can be calculated
        if jwk.p and jwk.q and jwk.d:
            # convert the values of p, q, and d from bytes to int
            p = _bytes_to_int(jwk.p)
            q = _bytes_to_int(jwk.q)
            d = _bytes_to_int(jwk.d)

            # convert or compute the remaining private key numbers
            dmp1 = _bytes_to_int(jwk.dp) if jwk.dp else rsa_crt_dmp1(private_exponent=d, p=p)
            dmq1 = _bytes_to_int(jwk.dq) if jwk.dq else rsa_crt_dmq1(private_exponent=d, p=q)
            iqmp = _bytes_to_int(jwk.qi) if jwk.qi else rsa_crt_iqmp(p=p, q=q)

            # create the private key from the jwk key values
            priv = RSAPrivateNumbers(p=p, q=q, d=d, dmp1=dmp1, dmq1=dmq1, iqmp=iqmp, public_numbers=pub)
            key_impl = priv.private_key(cryptography.hazmat.backends.default_backend())

        # if the necessary private key values are not specified create the public key
        else:
            key_impl = pub.public_key(cryptography.hazmat.backends.default_backend())

        rsa_key._rsa_impl = key_impl

        return rsa_key

    def to_jwk(self, include_private=False):
        jwk = JsonWebKey(kid=self.kid,
                         kty=self.kty,
                         key_ops=self.key_ops if include_private else RsaKey.PUBLIC_KEY_DEFAULT_OPS,
                         n=self.n,
                         e=self.e)

        if include_private:
            jwk.q = self.q
            jwk.p = self.p
            jwk.d = self.d
            jwk.dq = self.dq
            jwk.dp = self.dp
            jwk.qi = self.qi

        return jwk

    def encrypt(self, plaintext, padding=_default_encryption_padding()):
        return self.public_key.encrypt(plaintext, padding)

    def decrypt(self, ciphertext, padding=_default_encryption_padding()):
        if not self.is_private_key():
            raise NotImplementedError('The current RsaKey contains no private key material and does not support decrypt')

        return self.private_key.decrypt(ciphertext, padding)

    def sign(self, data, padding=_default_signature_padding(), algorithm=_default_signature_algorithm()):
        if not self.is_private_key():
            raise NotImplementedError('The current RsaKey contains no private key material and does not support sign')

        return self.private_key.sign(data, padding, algorithm)

    def verify(self, signature, data, padding=_default_signature_padding(), algorithm=_default_signature_algorithm()):
        return self.public_key.verify(signature, data, padding, algorithm)

    def is_private_key(self):
        return isinstance(self._rsa_impl, RSAPrivateKey)

    def _public_key_material(self):
        self.public_key.public_numbers()

    def _private_key_material(self):
        self.private_key.private_numbers() if self.private_key else None




