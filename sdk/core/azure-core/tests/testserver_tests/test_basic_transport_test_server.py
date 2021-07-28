# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from six.moves.http_client import HTTPConnection
from azure.core.pipeline.transport import HttpRequest, RequestsTransport
from azure.core.pipeline.transport._base import HttpClientTransportResponse
from azure.core.pipeline import Pipeline
import logging
import pytest


def test_http_client_response(port):
    # Create a core request
    request = HttpRequest("GET", "http://localhost:{}".format(port))

    # Fake a transport based on http.client
    conn = HTTPConnection("localhost", port)
    conn.request("GET", "/get")
    r1 = conn.getresponse()

    response = HttpClientTransportResponse(request, r1)

    # Don't assume too much in those assert, since we reach a real server
    assert response.internal_response is r1
    assert response.reason is not None
    assert isinstance(response.status_code, int)
    assert len(response.headers.keys()) != 0
    assert len(response.text()) != 0
    assert "content-type" in response.headers
    assert "Content-Type" in response.headers


def test_timeout(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.transport"):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=100)

    assert "Tuple timeout setting is deprecated" not in caplog.text


def test_tuple_timeout(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.transport"):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=(100, 100))

    assert "Tuple timeout setting is deprecated" in caplog.text


def test_conflict_timeout(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    with pytest.raises(ValueError):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=(100, 100), read_timeout = 100)
