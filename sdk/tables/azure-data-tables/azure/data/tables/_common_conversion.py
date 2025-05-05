# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import hashlib
import hmac
from datetime import timezone
from urllib.parse import ParseResult
from typing import Optional, Tuple, List


def _to_str(value):
    return str(value) if value is not None else None


def _to_utc_datetime(value):
    try:
        value = value.astimezone(timezone.utc)
    except ValueError:
        # Before Python 3.8, this raised for a naive datetime.
        pass
    try:
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode_base64(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    encoded = base64.b64encode(data)
    return encoded.decode("utf-8")


def _decode_base64_to_bytes(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64decode(data)


def _sign_string(key, string_to_sign, key_is_base64=True):
    if key_is_base64:
        key = _decode_base64_to_bytes(key)
    else:
        if isinstance(key, str):
            key = key.encode("utf-8")
    if isinstance(string_to_sign, str):
        string_to_sign = string_to_sign.encode("utf-8")
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = _encode_base64(digest)
    return encoded_digest


def _is_cosmos_endpoint(url):
    if ".table.cosmosdb." in url.hostname:
        return True
    if ".table.cosmos." in url.hostname:
        return True
    if url.hostname == "localhost" and url.port != 10002:
        return True
    return False


def _transform_patch_to_cosmos_post(request):
    request.method = "POST"
    request.headers["X-HTTP-Method"] = "MERGE"


def _get_account(parsed_url: ParseResult) -> Tuple[List[str], Optional[str]]:
    if ".core." in parsed_url.netloc or ".cosmos." in parsed_url.netloc:
        account = parsed_url.netloc.split(".table.core.")
        if "cosmos" in parsed_url.netloc:
            account = parsed_url.netloc.split(".table.cosmos.")
        account_name = account[0] if len(account) > 1 else None
    else:
        path_account_name = parsed_url.path.split("/")
        if len(path_account_name) > 1:
            account_name = path_account_name[1]
            account = [account_name, parsed_url.netloc]
        else:
            # If format doesn't fit Azurite, default to standard parsing
            account = parsed_url.netloc.split(".table.core.")
            account_name = account[0] if len(account) > 1 else None
    return account, account_name
