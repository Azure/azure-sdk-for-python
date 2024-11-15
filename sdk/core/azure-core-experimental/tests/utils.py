# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import types
import io
import xml.etree.ElementTree as ET

import urllib3
import httpx

############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.pipeline._tools import is_rest

HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]

SYNC_TRANSPORTS = []
ASYNC_TRANSPORTS = []

from azure.core.experimental.transport import Urllib3Transport

SYNC_TRANSPORTS.append(Urllib3Transport)


from azure.core.experimental.transport import (
    HttpXTransport,
    AsyncHttpXTransport,
)

# SYNC_TRANSPORTS.append(HttpXTransport)
# ASYNC_TRANSPORTS.append(AsyncHttpXTransport)


# from azure.core.experimental.transport import PyodideTransport

# ASYNC_TRANSPORTS.append(PyodideTransport)


############################## HELPER FUNCTIONS ##############################


def create_http_request(http_request, *args, **kwargs):
    try:
        method = args[0]
    except IndexError:
        method = kwargs.pop("method")
    try:
        url = args[1]
    except IndexError:
        url = kwargs.pop("url")
    try:
        headers = args[2]
    except IndexError:
        headers = kwargs.pop("headers", None)
    try:
        files = args[3]
    except IndexError:
        files = kwargs.pop("files", None)
    try:
        data = args[4]
    except IndexError:
        data = kwargs.pop("data", None)
    if hasattr(http_request, "content"):
        return http_request(method=method, url=url, headers=headers, files=files, data=data, **kwargs)
    content = kwargs.pop("content", None)
    json = kwargs.pop("json", None)
    legacy_request = http_request(method, url, headers=headers, data=data, files=files, **kwargs)
    if content:
        if isinstance(content, ET.Element):
            legacy_request.set_xml_body(content)
        else:
            legacy_request.data = content
    if json:
        legacy_request.headers["Content-Type"] = "application/json"
        legacy_request.set_json_body(json)
    return legacy_request


def create_transport_from_connection(transport):
    if transport == Urllib3Transport:
        return Urllib3Transport(pool=urllib3.PoolManager(), pool_owner=False)
    elif transport == HttpXTransport:
        return HttpXTransport(client=httpx.Client(), client_owner=False)
    raise ValueError(f"Unexpected transport type: {transport}")


def assert_transport_connection(transport, is_closed=True):
    if isinstance(transport, Urllib3Transport):
        if is_closed:
            assert transport._pool is None
        else:
            assert transport._pool
    elif isinstance(transport, HttpXTransport):
        if is_closed:
            assert transport._client is None
        else:
            assert transport._client
    else:
        raise ValueError(f"Unexpected transport type: {transport}")


class NamedIo(io.BytesIO):
    def __init__(self, name: str, *args, **kwargs):
        super(NamedIo, self).__init__(*args, **kwargs)
        self.name = name
