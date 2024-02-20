# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from typing import (  # pylint: disable=unused-import
    cast,
    Tuple,
)
from azure.core.pipeline.policies import HttpLoggingPolicy, HeadersPolicy


def create_token_credential():
    # type: () -> FakeTokenCredential or DefaultAzureCredential
    from devtools_testutils import is_live

    if not is_live():
        from .fake_token_credential import FakeTokenCredential

        return FakeTokenCredential()
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential()


def async_create_token_credential():
    # type: () -> AsyncFakeTokenCredential or DefaultAzureCredential
    from devtools_testutils import is_live

    if not is_live():
        from .async_fake_token_credential import AsyncFakeTokenCredential

        return AsyncFakeTokenCredential()
    from azure.identity.aio import DefaultAzureCredential

    return DefaultAzureCredential()


def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update({"MS-CV"})
    return http_logging_policy


def get_header_policy(**kwargs):
    header_policy = HeadersPolicy(**kwargs)

    useragent = os.getenv("AZURE_USERAGENT_OVERRIDE")
    if useragent:
        header_policy.add_header("x-ms-useragent", useragent)

    return header_policy


def parse_connection_str(conn_str):
    # type: (str) -> Tuple[str, str]
    if conn_str is None:
        raise ValueError("Connection string is undefined.")
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
        host = cast(str, endpoint)[left_slash_pos + 2 :]
    else:
        host = str(endpoint)

    return host, str(shared_access_key)
