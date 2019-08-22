# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import codecs
from base64 import b64encode, b64decode

from cryptography.hazmat.primitives.asymmetric import utils


def _bytes_to_int(b):
    if not b or not isinstance(b, bytes):
        raise ValueError("b must be non-empty byte string")

    return int(codecs.encode(b, "hex"), 16)


def _int_to_bytes(i):
    h = hex(i)
    if len(h) > 1 and h[0:2] == "0x":
        h = h[2:]

    # need to strip L in python 2.x
    h = h.strip("L")

    if len(h) % 2:
        h = "0" + h
    return codecs.decode(h, "hex")


def _bstr_to_b64url(bstr):
    """Serialize bytes into base-64 string.
    :param str: Object to be serialized.
    :rtype: str
    """
    encoded = b64encode(bstr).decode()
    return encoded.strip("=").replace("+", "-").replace("/", "_")


def _str_to_b64url(s):
    """Serialize str into base-64 string.
    :param str: Object to be serialized.
    :rtype: str
    """
    return _bstr_to_b64url(s.encode(encoding="utf8"))


def _b64_to_bstr(b64str):
    """Deserialize base64 encoded string into string.
    :param str b64str: response string to be deserialized.
    :rtype: bytearray
    :raises: TypeError if string format invalid.
    """
    padding = "=" * (3 - (len(b64str) + 3) % 4)
    b64str = b64str + padding
    encoded = b64str.replace("-", "+").replace("_", "/")
    return b64decode(encoded)


def _b64_to_str(b64str):
    """Deserialize base64 encoded string into string.
    :param str b64str: response string to be deserialized.
    :rtype: str
    :raises: TypeError if string format invalid.
    """
    return _b64_to_bstr(b64str).decode("utf8")


def _int_to_bigendian_8_bytes(i):
    b = _int_to_bytes(i)

    if len(b) > 8:
        raise ValueError("the specified integer is to large to be represented by 8 bytes")

    if len(b) < 8:
        b = (b"\0" * (8 - len(b))) + b

    return b


def encode_key_vault_ecdsa_signature(signature):
    """
    ASN.1 DER encode a Key Vault ECDSA signature.

    Key Vault returns ECDSA signatures as the concatenated bytes of two equal-size integers. ``cryptography`` expects
    ECDSA signatures be ASN.1 DER encoded.

    :param bytes signature: ECDSA signature returned by Key Vault
    :return: signature encoded for use by ``cryptography``
    """
    mid = len(signature) // 2
    r = _bytes_to_int(signature[:mid])
    s = _bytes_to_int(signature[mid:])
    return utils.encode_dss_signature(r, s)
