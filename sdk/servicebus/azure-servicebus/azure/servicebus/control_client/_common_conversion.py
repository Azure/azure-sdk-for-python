# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import base64
import hashlib
import hmac
import sys

from ._common_models import _unicode_type


def _encode_base64(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    encoded = base64.b64encode(data)
    return encoded.decode('utf-8')


def _decode_base64_to_bytes(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    return base64.b64decode(data)


def _decode_base64_to_text(data):
    decoded_bytes = _decode_base64_to_bytes(data)
    return decoded_bytes.decode('utf-8')


if sys.version_info < (3,):
    def _str(value):
        if isinstance(value, _unicode_type):
            return value.encode('utf-8')

        return str(value)
else:
    _str = str


def _str_or_none(value):
    if value is None:
        return None

    return _str(value)


def _int_or_none(value):
    if value is None:
        return None

    return str(int(value))


def _bool_or_none(value):
    if value is None:
        return None

    if isinstance(value, bool):
        if value:
            return 'true'
        return 'false'

    return str(value)


def _lower(text):
    return text.lower()


def _sign_string(key, string_to_sign, key_is_base64=True):
    if key_is_base64:
        key = _decode_base64_to_bytes(key)
    else:
        if isinstance(key, _unicode_type):
            key = key.encode('utf-8')
    if isinstance(string_to_sign, _unicode_type):
        string_to_sign = string_to_sign.encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = _encode_base64(digest)
    return encoded_digest
