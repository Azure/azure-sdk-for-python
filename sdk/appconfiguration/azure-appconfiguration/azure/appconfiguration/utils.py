# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime
import re
from requests.structures import CaseInsensitiveDict


def escape_reserved(value):
    """
    Reserved characters are star(*), comma(,) and backslash(\\)
    If a reserved character is part of the value, then it must be escaped using \\{Reserved Character}.
    Non-reserved characters can also be escaped.

    """
    if value is None:
        return None
    if value == "":
        return "\0"  # '\0' will be encoded to %00 in the url.
    if isinstance(value, list):
        return [escape_reserved(s) for s in value]
    value = str(value)  # value is unicode for Python 2.7
    # precede all reserved characters with a backslash.
    # But if a * is at the beginning or the end, don't add the backslash
    return re.sub(r"((?!^)\*(?!$)|\\|,)", r"\\\1", value)


def escape_and_tolist(value):
    if value is not None:
        if isinstance(value, str):
            value = [value]
        value = escape_reserved(value)
    return value


def quote_etag(etag):
    if etag != "*" and etag is not None:
        return '"' + etag + '"'
    return etag


def prep_update_configuration_setting(key, etag=None, **kwargs):
    # type: (str, str, dict) -> CaseInsensitiveDict
    if not key:
        raise ValueError("key is mandatory to update a ConfigurationSetting")

    custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
    if etag:
        custom_headers["if-match"] = quote_etag(etag)
    elif "if-match" not in custom_headers:
        custom_headers["if-match"] = "*"

    return custom_headers


def get_endpoint_from_connection_string(connection_string):
    endpoint, _, _ = parse_connection_string(connection_string)
    return endpoint


def parse_connection_string(connection_string):
    # connection_string looks like Endpoint=https://xxxxx;Id=xxxxx;Secret=xxxx
    segments = connection_string.split(";")
    if len(segments) != 3:
        raise ValueError("Invalid connection string.")

    endpoint = ""
    id_ = ""
    secret = ""
    for segment in segments:
        segment = segment.strip()
        if segment.startswith("Endpoint"):
            endpoint = str(segment[17:])
        elif segment.startswith("Id"):
            id_ = str(segment[3:])
        elif segment.startswith("Secret"):
            secret = str(segment[7:])
        else:
            raise ValueError("Invalid connection string.")

    if not endpoint or not id_ or not secret:
        raise ValueError("Invalid connection string.")

    return endpoint, id_, secret


def get_current_utc_time():
    return str(datetime.utcnow().strftime("%b, %d %Y %H:%M:%S ")) + "GMT"
