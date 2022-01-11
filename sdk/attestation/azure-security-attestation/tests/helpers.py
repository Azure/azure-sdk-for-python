# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64


def pem_from_base64(base64_value, header_type):
    # type: (str, str) -> str
    pem = "-----BEGIN " + header_type + "-----\n"
    while base64_value != "":
        pem += base64_value[:64] + "\n"
        base64_value = base64_value[64:]
    pem += "-----END " + header_type + "-----\n"
    return pem


def base64url_encode(unencoded):
    # type: (bytes)->str
    base64val = base64.urlsafe_b64encode(unencoded)
    strip_trailing = base64val.split(b"=")[0]  # pick the string before the trailing =
    return strip_trailing.decode("utf-8")


def base64url_decode(encoded):
    # type: (str)->bytes
    padding_added = encoded + "=" * ((len(encoded) * -1) % 4)
    return base64.urlsafe_b64decode(padding_added.encode("utf-8"))
