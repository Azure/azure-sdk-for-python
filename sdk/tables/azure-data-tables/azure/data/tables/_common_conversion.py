# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import hashlib
import hmac
from sys import version_info
import six


if version_info < (3,):

    def _str(value):
        if isinstance(value, unicode):  # pylint: disable=undefined-variable
            return value.encode("utf-8")

        return str(value)


else:
    _str = str


def _to_str(value):
    return _str(value) if value is not None else None


def _to_utc_datetime(value):
    try:
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode_base64(data):
    if isinstance(data, six.text_type):
        data = data.encode("utf-8")
    encoded = base64.b64encode(data)
    return encoded.decode("utf-8")


def _decode_base64_to_bytes(data):
    if isinstance(data, six.text_type):
        data = data.encode("utf-8")
    return base64.b64decode(data)


def _sign_string(key, string_to_sign, key_is_base64=True):
    if key_is_base64:
        key = _decode_base64_to_bytes(key)
    else:
        if isinstance(key, six.text_type):
            key = key.encode("utf-8")
    if isinstance(string_to_sign, six.text_type):
        string_to_sign = string_to_sign.encode("utf-8")
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = _encode_base64(digest)
    return encoded_digest
