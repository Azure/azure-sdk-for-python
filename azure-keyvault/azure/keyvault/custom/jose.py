#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------
import codecs
import json
import cryptography
from ..models import JsonWebKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers, \
    generate_private_key, rsa_crt_dmp1, rsa_crt_dmq1, rsa_crt_iqmp
from base64 import b64encode, b64decode
import os
import hmac
import hashlib

def _str_to_b64(str, **kwargs):
    """Serialize str into base-64 string.
    :param str: Object to be serialized.
    :rtype: str
    """
    encoded = b64encode(str.encode('ascii')).decode('ascii')
    return encoded.strip('=').replace('+', '-').replace('/', '_')


def _b64_to_str(b64str):
    """Deserialize base64 encoded string into string.
    :param str b64str: response string to be deserialized.
    :rtype: bytearray
    :raises: TypeError if string format invalid.
    """
    padding = '=' * (3 - (len(b64str) + 3) % 4)
    b64str = b64str + padding
    encoded = b64str.replace('-', '+').replace('_', '/')
    return b64decode(encoded).decode('ascii')


class JoseHeader(object):

    def __init__(self):
        pass

    def to_compact_header(self):
        return _str_to_b64(json.dumps(self.__dict__))


class JweHeader(object):
    def __init__(self, alg=None, kek_id=None, enc=None):
        self.alg = alg
        self.kek_id = kek_id
        self.enc = enc

    @staticmethod
    def from_compact_header(compact):
        header = JweHeader()
        header.__dict__ = json.loads(_b64_to_str(compact))


class JweObject(object):
    def __init__(self):
        self.protected = None
        self.encrypted_key = None
        self.iv = None
        self.ciphertext = None
        self.tag = None

    def to_flattened_jwe(self):
        if not (self.protected, self.encrypted_key, self.iv, self.ciphertext, self.tag):
            raise ValueError('JWE is not complete.')

        json.dumps(self.__dict__)

class JwsHeader(object):
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


class JwsObject(object):
    def __init__(self):
        self.protected = None
        self.payload = None
        self.signature = None

