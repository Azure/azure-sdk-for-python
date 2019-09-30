# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime
import re
from azure.core import MatchConditions

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

def escape_and_tostr(value):
    if value is None:
        return None
    if value == [None]:
        return None
    value = escape_reserved(value)
    return ','.join(value)

def quote_etag(etag):
    if not etag or etag == "*":
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'

def prep_if_match(etag, match_condition):
    # type: (str, MatchConditions) -> str
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None

def prep_if_none_match(etag, match_condition):
    # type: (str, MatchConditions) -> str
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None

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
