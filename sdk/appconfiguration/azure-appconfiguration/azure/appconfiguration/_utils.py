# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from azure.core import MatchConditions


def quote_etag(etag: Optional[str]) -> Optional[str]:
    if not etag or etag == "*":
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'


def prep_if_match(etag: Optional[str], match_condition: Optional[MatchConditions]) -> Optional[str]:
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None


def prep_if_none_match(etag: Optional[str], match_condition: Optional[MatchConditions]) -> Optional[str]:
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None


def parse_connection_string(connection_string: str) -> Tuple[str, str, str]:
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


def get_current_utc_time() -> str:
    return str(datetime.utcnow().strftime("%b, %d %Y %H:%M:%S.%f ")) + "GMT"


def get_key_filter(*args, **kwargs) -> Tuple[Optional[str], Dict[str, Any]]:
    key_filter = None
    if len(args) > 0:
        key_filter = args[0]
        if "key_filter" in kwargs:
            raise TypeError(
                "AzureAppConfigurationClient.list_configuration_settings() got multiple values for argument "
                "'key_filter'"
            )
    return key_filter or kwargs.pop("key_filter", None), kwargs


def get_label_filter(*args, **kwargs) -> Tuple[Optional[str], Dict[str, Any]]:
    label_filter = None
    if len(args) > 1:
        label_filter = args[1]
        if "label_filter" in kwargs:
            raise TypeError(
                "AzureAppConfigurationClient.list_configuration_settings() got multiple values for argument "
                "'label_filter'"
            )
    return label_filter or kwargs.pop("label_filter", None), kwargs
