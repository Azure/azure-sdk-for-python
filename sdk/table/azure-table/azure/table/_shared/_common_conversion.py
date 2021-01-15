# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import hashlib
import hmac
from io import (SEEK_SET)
import six
from azure.table._shared.parser import _str


from ._error import (
    _ERROR_VALUE_SHOULD_BE_BYTES_OR_STREAM,
    _ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM,
)


def _to_str(value):
    return _str(value) if value is not None else None


def _int_to_str(value):
    return str(int(value)) if value is not None else None


def _bool_to_str(value):
    if value is None:
        return None

    if isinstance(value, bool):
        if value:  # pylint: disable=R1705
            return 'true'
        else:
            return 'false'

    return str(value)


def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def _datetime_to_utc_string(value):
    # Azure expects the date value passed in to be UTC.
    # Azure will always return values as UTC.
    # If a date is passed in without timezone info, it is assumed to be UTC.
    if value is None:
        return None

    return value.strftime('%a, %d %b %Y %H:%M:%S GMT')


def _encode_base64(data):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')
    encoded = base64.b64encode(data)
    return encoded.decode('utf-8')


def _decode_base64_to_bytes(data):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')
    return base64.b64decode(data)


def _decode_base64_to_text(data):
    decoded_bytes = _decode_base64_to_bytes(data)
    return decoded_bytes.decode('utf-8')


def _sign_string(key, string_to_sign, key_is_base64=True):
    if key_is_base64:
        key = _decode_base64_to_bytes(key)
    else:
        if isinstance(key, six.text_type):
            key = key.encode('utf-8')
    if isinstance(string_to_sign, six.text_type):
        string_to_sign = string_to_sign.encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = _encode_base64(digest)
    return encoded_digest


def _get_content_md5(data):
    md5 = hashlib.md5()
    if isinstance(data, bytes):
        md5.update(data)
    elif hasattr(data, 'read'):
        pos = 0
        pos = data.tell()
        for chunk in iter(lambda: data.read(4096), b""):
            md5.update(chunk)
        try:
            data.seek(pos, SEEK_SET)
        except (AttributeError, IOError):
            raise ValueError(_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM.format('data'))
    else:
        raise ValueError(_ERROR_VALUE_SHOULD_BE_BYTES_OR_STREAM.format('data'))

    return base64.b64encode(md5.digest()).decode('utf-8')


def _lower(text):
    return text.lower()
