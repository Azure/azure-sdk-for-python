# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime
from typing import Optional, Tuple, Dict, Any


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


def get_key_filter(*args: Optional[str], **kwargs: Any) -> Tuple[Optional[str], Dict[str, Any]]:
    key_filter = None
    if len(args) > 0:
        key_filter = args[0]
        if "key_filter" in kwargs:
            raise TypeError(
                "AzureAppConfigurationClient.list_configuration_settings() got multiple values for argument "
                "'key_filter'"
            )
    return key_filter or kwargs.pop("key_filter", None), kwargs


def get_label_filter(*args: Optional[str], **kwargs: Any) -> Tuple[Optional[str], Dict[str, Any]]:
    label_filter = None
    if len(args) > 1:
        label_filter = args[1]
        if "label_filter" in kwargs:
            raise TypeError(
                "AzureAppConfigurationClient.list_configuration_settings() got multiple values for argument "
                "'label_filter'"
            )
    return label_filter or kwargs.pop("label_filter", None), kwargs
