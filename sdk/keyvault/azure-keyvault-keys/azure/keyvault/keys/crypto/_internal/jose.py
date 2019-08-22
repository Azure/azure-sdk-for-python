# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import os
from ._internal import _str_to_b64url, _b64_to_str
from .symmetric_key import SymmetricKey
from .key import Key


def protect(plaintext, kek=None, alg=None, cek=None, enc=None):  # pylint:disable=unused-argument
    # if neither the kek or the cek is specified raise an error
    if not kek and not cek:
        raise ValueError(
            "Either kek must be specified for key encryption sharing, "
            "or cek must be specified for direct encryption key sharing"
        )

    # key encryption key can be any key (symmetric or asymmetric)
    if kek and not isinstance(kek, Key):
        raise TypeError("The specified kek must be a valid Key")

    # only symmetric keys are valid for the content encryption key
    if cek and not isinstance(cek, SymmetricKey):
        raise TypeError("The specified cek must be a valid SymmetricKey")

    # create the cek if not specified
    cek = cek or SymmetricKey()

    # kid is the kek id if were using key encryption sharing else it's the cek id for direct sharing
    kid = kek.kid if kek else cek.kid

    # alg is 'dir' for direct sharing otherwise use the specified alg
    # or the default key wrap algorithm if not specified
    alg = "dir" if not kek else alg or kek.default_key_wrap_algorithm

    # use the specified enc or the default encryption algorithm of the cek if not specified
    enc = enc or cek.default_encryption_algorithm

    jwe = JweObject()
    jwe.unprotected = JweHeader(alg=alg, kid=kid, enc=enc)
    jwe.iv = os.urandom(16)
    jwe.ciphertext = cek.encrypt()

    # add the encrypted key if we're using key encryption sharing
    if kek:
        jwe.encrypted_key = kek.wrap_key(key=cek)


class JoseObject(object):
    def deserialize(self, s):
        d = json.loads(s)
        self.__dict__ = d  # pylint:disable=attribute-defined-outside-init
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
        header.__dict__ = json.loads(_b64_to_str(compact))  # pylint:disable=attribute-defined-outside-init
        return header


class JweObject(JoseObject):
    def __init__(self):
        self.unprotected = None
        self.protected = None
        self.encrypted_key = None
        self.iv = None
        self.ciphertext = None
        self.tag = None

    def to_flattened_jwe(self):
        if not (self.protected, self.encrypted_key, self.iv, self.ciphertext, self.tag):
            raise ValueError("JWE is not complete.")

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
        header.__dict__ = json.loads(_b64_to_str(compact))  # pylint:disable=attribute-defined-outside-init
        return header


class JwsObject(JoseObject):
    def __init__(self):
        self.protected = None
        self.payload = None
        self.signature = None

    def to_flattened_jws(self):
        if not (self.protected, self.payload, self.signature):
            raise ValueError("JWS is not complete.")

        return json.dumps(self.__dict__)
