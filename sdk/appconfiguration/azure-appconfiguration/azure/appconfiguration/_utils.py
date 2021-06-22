# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime
from typing import Optional, Tuple
from azure.core import MatchConditions


def quote_etag(etag):
    # type: (Optional[str]) -> Optional[str]
    if not etag or etag == "*":
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'


def prep_if_match(etag, match_condition):
    # type: (Optional[str], Optional[MatchConditions]) -> Optional[str]
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None


def prep_if_none_match(etag, match_condition):
    # type: (Optional[str], Optional[MatchConditions]) -> Optional[str]
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None


def get_endpoint_from_connection_string(connection_string):
    # type: (str) -> str
    base_url, _, _ = parse_connection_string(connection_string)
    return base_url


def parse_connection_string(connection_string):
    # type: (str) -> Tuple[str, str, str]
    # connection_string looks like Endpoint=https://xxxxx;Id=xxxxx;Secret=xxxx
    segments = connection_string.split(";")
    if len(segments) != 3:
        raise ValueError("Invalid connection string.")

    base_url = ""
    id_ = ""
    secret = ""
    for segment in segments:
        segment = segment.strip()
        if segment.startswith("Endpoint"):
            base_url = str(segment[17:])
        elif segment.startswith("Id"):
            id_ = str(segment[3:])
        elif segment.startswith("Secret"):
            secret = str(segment[7:])
        else:
            raise ValueError("Invalid connection string.")

    if not base_url or not id_ or not secret:
        raise ValueError("Invalid connection string.")

    return base_url, id_, secret


def get_current_utc_time():
    # type: () -> str
    return str(datetime.utcnow().strftime("%b, %d %Y %H:%M:%S.%f ")) + "GMT"
