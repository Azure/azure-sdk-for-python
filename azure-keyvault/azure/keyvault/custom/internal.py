#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import hmac
import hashlib
import json
import codecs
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def _const_time_compare(bstr_1, bstr_2):
    eq = len(bstr_1) == len(bstr_2)

    for i in range(min(len(bstr_1), len(bstr_2))):
        eq &= bstr_1[i] == bstr_2[i]

    return eq



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

    # pad the data so it is a multiple of blocksize
    # pkcs7 padding dictates the pad bytes are the value of the number of pad bytes added
    padlen = 16 - len(plaintext) % 16
    padval = _int_to_bytes(padlen)
    plaintext += padval * padlen

    # create the cipher and encrypt the plaintext
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # get the data to hash with HMAC, hash the data and take the first 16 bytes
    hashdata = authdata + iv + ciphertext + auth_data_length
    tag = hmac.new(key=hmac_key, msg=hashdata, digestmod=hashlib.sha256).digest()[:16]

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

    hmac_key = key[:16]
    aes_key = key[16:32]
    auth_data_length = _int_to_bigendian_8_bytes(len(authdata) * 8)

    # ensure the authtag is the expected length for SHA256 hash
    if not len(authtag) == 16:
        raise ValueError('invalid tag')

    hashdata = authdata + iv + ciphertext + auth_data_length
    tag = hmac.new(key=hmac_key, msg=hashdata, digestmod=hashlib.sha256).digest()[:16]

    if not _const_time_compare(tag, authtag):
        raise ValueError('"ciphertext" is not authentic')

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # remove the pad bytes (for pkcs7 the # of pad bytes == the value of the last byte)
    padlen = plaintext[-1]
    plaintext = plaintext[:-1 * padlen]

    return plaintext


def _bytes_to_int(b):
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
    """Serialize str into base-64 string.
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
    :rtype: bytearray
    :raises: TypeError if string format invalid.
    """
    return _b64_to_bstr(b64str).decode('utf8')


def _int_to_bigendian_8_bytes(i):
    b = _int_to_bytes(i)

    if len(b) < 8:
        b = (b'\0' * (8 - len(b))) + b

    return b


class JoseObject(object):

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


class JoseHeader(JoseObject):

    def to_compact_header(self):
        return _str_to_b64url(json.dumps(self.__dict__))


class JweHeader(JoseHeader):
    def __init__(self, alg=None, kid=None, enc=None):
        self.alg = alg
        self.kid = kid
        self.enc = enc

    @staticmethod
    def from_compact_header(compact):
        header = JweHeader()
        header.__dict__ = json.loads(_b64_to_str(compact))
        return header


class JweObject(JoseObject):
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


class JwsHeader(JoseHeader):
    def __init__(self):
        self.alg = None
        self.kid = None
        self.at = None
        self.ts = None
        self.p = None
        self.typ = None

    @staticmethod
    def from_compact_header(compact):
        header = JwsHeader()
        header.__dict__ = json.loads(_b64_to_str(compact))
        return header


class JwsObject(JoseObject):
    def __init__(self):
        self.protected = None
        self.payload = None
        self.signature = None

    def to_flattened_jws(self):
        if not (self.protected, self.payload, self.signature):
            raise ValueError('JWS is not complete.')

        return json.dumps(self.__dict__)
