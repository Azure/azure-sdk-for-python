# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from itertools import product

import pytest

from rest_client import MockRestClient
from utils import SYNC_TRANSPORTS, HTTP_REQUESTS, create_http_request

from azure.core.exceptions import IncompleteReadError


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_sync_transport_short_read_download_stream(port, transport, requesttype):
    client = MockRestClient(port, transport=transport())
    request = create_http_request(requesttype, "GET", "/errors/short-data")
    with pytest.raises(IncompleteReadError):
        response = client.send_request(request, stream=True)
        data = response.iter_bytes()
        content = b""
        for d in data:
            content += d
