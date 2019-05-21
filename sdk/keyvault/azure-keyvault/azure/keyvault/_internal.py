#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import json
import uuid
import codecs
from base64 import b64encode, b64decode
import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers, \
    generate_private_key, rsa_crt_dmp1, rsa_crt_dmq1, rsa_crt_iqmp, RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes, constant_time, padding, hmac

from azure.keyvault.models import JsonWebKey

def _a128cbc_hs256_encrypt(key, iv, plaintext, authdata):
    if not key or not len(key) >= 32:
        raise ValueError('key must be at least 256 bits for algorithm "A128CBC-HS256"')
    if not iv or len(iv) != 16:
        raise ValueError('iv must be 128 bits for algorithm "A128CBC-HS256"')
    if not plaintext:
        raise ValueError('plaintext must be specified')
    if not authdata:
        raise ValueError('authdata must be specified')

    # get the hmac key and the aes key from the specified key
    hmac_key = key[:16]
    aes_key = key[16:32]

    # calculate the length of authdata and store as bytes
    auth_data_length = _int_to_bigendian_8_bytes(len(authdata) * 8)

    # pad the plaintext with pkcs7
    padder = padding.PKCS7(128).padder()
    plaintext = padder.update(plaintext) + padder.finalize()

    # create the cipher and encrypt the plaintext
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # get the data to hash with HMAC, hash the data and take the first 16 bytes
    hashdata = authdata + iv + ciphertext + auth_data_length
    hmac_hash = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    hmac_hash.update(hashdata)
    tag = hmac_hash.finalize()[:16]

    return ciphertext, tag


def _a128cbc_hs256_decrypt(key, iv, ciphertext, authdata, authtag):
    if not key or not len(key) >= 32:
        raise ValueError('key must be at least 256 bits for algorithm "A128CBC-HS256"')
    if not iv or len(iv) != 16:
        raise ValueError('iv must be 128 bits for algorithm "A128CBC-HS256"')
    if not ciphertext:
        raise ValueError('ciphertext must be specified')
    if not authdata:
        raise ValueError('authdata must be specified')
    if not authtag or len(authtag) != 16:
        raise ValueError('authtag must be be 128 bits for algorithm "A128CBC-HS256"')

    hmac_key = key[:16]
    aes_key = key[16:32]
    auth_data_length = _int_to_bigendian_8_bytes(len(authdata) * 8)

    # ensure the authtag is the expected length for SHA256 hash
    if not len(authtag) == 16:
        raise ValueError('invalid tag')

    hashdata = authdata + iv + ciphertext + auth_data_length
    hmac_hash = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    hmac_hash.update(hashdata)
    tag = hmac_hash.finalize()[:16]

    if not constant_time.bytes_eq(tag, authtag):
        raise ValueError('"ciphertext" is not authentic')

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # unpad the decrypted plaintext
    padder = padding.PKCS7(128).unpadder()
    plaintext = padder.update(plaintext) + padder.finalize()

    return plaintext


def _bytes_to_int(b):
    if not b or not isinstance(b, bytes):
        raise ValueError('b must be non-empty byte string')

    return int(codecs.encode(b, 'hex'), 16)


def _int_to_bytes(i):
    h = hex(i)
    if len(h) > 1 and h[0:2] == '0x':
        h = h[2:]

    # need to strip L in python 2.x
    h = h.strip('L')

    if len(h) % 2:
        h = '0' + h
    return codecs.decode(h, 'hex')


def _bstr_to_b64url(bstr, **kwargs):
    """Serialize bytes into base-64 string.
    :param str: Object to be serialized.
    :rtype: str
    """
    encoded = b64encode(bstr).decode()
    return encoded.strip('=').replace('+', '-').replace('/', '_')


def _str_to_b64url(s, **kwargs):
    """Serialize str into base-64 string.
    :param str: Object to be serialized.
    :rtype: str
    """
    return _bstr_to_b64url(s.encode(encoding='utf8'))


def _b64_to_bstr(b64str):
    """Deserialize base64 encoded string into string.
    :param str b64str: response string to be deserialized.
    :rtype: bytearray
    :raises: TypeError if string format invalid.
    """
    padding = '=' * (3 - (len(b64str) + 3) % 4)
    b64str = b64str + padding
    encoded = b64str.replace('-', '+').replace('_', '/')
    return b64decode(encoded)


def _b64_to_str(b64str):
    """Deserialize base64 encoded string into string.
    :param str b64str: response string to be deserialized.
    :rtype: str
    :raises: TypeError if string format invalid.
    """
    return _b64_to_bstr(b64str).decode('utf8')


def _int_to_bigendian_8_bytes(i):
    b = _int_to_bytes(i)

    if len(b) > 8:
        raise ValueError('the specified integer is to large to be represented by 8 bytes')

    if len(b) < 8:
        b = (b'\0' * (8 - len(b))) + b

    return b


class _JoseObject(object):

    def deserialize(self, s):
        d = json.loads(s)
        self.__dict__ = d
        return self

    def deserialize_b64(self, s):
        self.deserialize(_b64_to_str(s))
        return self

    def serialize(self):
        return json.dumps(self.__dict__)

    def serialize_b64url(self):
        return _str_to_b64url(self.serialize())


class _JoseHeader(_JoseObject):

    def to_compact_header(self):
        return _str_to_b64url(json.dumps(self.__dict__))


class _JweHeader(_JoseHeader):
    def __init__(self, alg=None, kid=None, enc=None):
        self.alg = alg
        self.kid = kid
        self.enc = enc

    @staticmethod
    def from_compact_header(compact):
        header = _JweHeader()
        header.__dict__ = json.loads(_b64_to_str(compact))
        return header


class _JweObject(_JoseObject):
    def __init__(self):
        self.protected = None
        self.encrypted_key = None
        self.iv = None
        self.ciphertext = None
        self.tag = None

    def to_flattened_jwe(self):
        if not (self.protected, self.encrypted_key, self.iv, self.ciphertext, self.tag):
            raise ValueError('JWE is not complete.')

        return json.dumps(self.__dict__)


class _JwsHeader(_JoseHeader):
    def __init__(self):
        self.alg = None
        self.kid = None
        self.at = None
        self.ts = None
        self.p = None
        self.typ = None

    @staticmethod
    def from_compact_header(compact):
        header = _JwsHeader()
        header.__dict__ = json.loads(_b64_to_str(compact))
        return header


class _JwsObject(_JoseObject):
    def __init__(self):
        self.protected = None
        self.payload = None
        self.signature = None

    def to_flattened_jws(self):
        if not (self.protected, self.payload, self.signature):
            raise ValueError('JWS is not complete.')

        return json.dumps(self.__dict__)



def _default_encryption_padding():
    return asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None)


def _default_signature_padding():
    return asym_padding.PKCS1v15()


def _default_signature_algorithm():
    return hashes.SHA256()


class _RsaKey(object):
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
    def p(self):
        return _int_to_bytes(self._private_key_material().p) if self.is_private_key() else None

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
        key = _RsaKey()
        key.kid = kid or str(uuid.uuid4())
        key.kty = kty
        key.key_ops = _RsaKey.PRIVATE_KEY_DEFAULT_OPS
        key._rsa_impl = generate_private_key(public_exponent=e,
                                             key_size=size,
                                             backend=cryptography.hazmat.backends.default_backend())
        return key

    @staticmethod
    def from_jwk_str(s):
        jwk_dict = json.loads(s)
        jwk = JsonWebKey.from_dict(jwk_dict)
        return _RsaKey.from_jwk(jwk)

    @staticmethod
    def from_jwk(jwk):
        if not isinstance(jwk, JsonWebKey):
            raise TypeError('The specified jwk must be a JsonWebKey')

        if jwk.kty != 'RSA' and jwk.kty != 'RSA-HSM':
            raise ValueError('The specified jwk must have a key type of "RSA" or "RSA-HSM"')

        if not jwk.n or not jwk.e:
            raise ValueError('Invalid RSA jwk, both n and e must be have values')

        rsa_key = _RsaKey()
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
            dmq1 = _bytes_to_int(jwk.dq) if jwk.dq else rsa_crt_dmq1(private_exponent=d, q=q)
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
                         key_ops=self.key_ops if include_private else _RsaKey.PUBLIC_KEY_DEFAULT_OPS,
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
            raise NotImplementedError('The current RsaKey does not support decrypt')

        return self.private_key.decrypt(ciphertext, padding)

    def sign(self, data, padding=_default_signature_padding(), algorithm=_default_signature_algorithm()):
        if not self.is_private_key():
            raise NotImplementedError('The current RsaKey does not support sign')

        return self.private_key.sign(data, padding, algorithm)

    def verify(self, signature, data, padding=_default_signature_padding(), algorithm=_default_signature_algorithm()):
        return self.public_key.verify(signature, data, padding, algorithm)

    def is_private_key(self):
        return isinstance(self._rsa_impl, RSAPrivateKey)

    def _public_key_material(self):
        return self.public_key.public_numbers()

    def _private_key_material(self):
        return self.private_key.private_numbers() if self.private_key else None
