# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import (  # pylint: disable=unused-import
    cast,
    Tuple,
)
from azure.core.pipeline.policies import HttpLoggingPolicy

def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "MS-CV"
        }
    )
    return http_logging_policy

def parse_connection_str(conn_str):
    # type: (str) -> Tuple[str, str, str, str]
    if conn_str is None:
        raise ValueError(
            "Connection string is undefined."
        )
    endpoint = None
    shared_access_key = None
    for element in conn_str.split(";"):
        key, _, value = element.partition("=")
        if key.lower() == "endpoint":
            endpoint = value.rstrip("/")
        elif key.lower() == "accesskey":
            shared_access_key = value
    if not all([endpoint, shared_access_key]):
        raise ValueError(
            "Invalid connection string. You can get the connection string from your resource page in the Azure Portal. "
            "The format should be as follows: endpoint=https://<ResourceUrl>/;accesskey=<KeyValue>"
        )
    left_slash_pos = cast(str, endpoint).find("//")
    if left_slash_pos != -1:
        host = cast(str, endpoint)[left_slash_pos + 2:]
    else:
        host = str(endpoint)

    return host, str(shared_access_key)