# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from unittest import mock
from socket import timeout as SocketTimeout

from urllib3.util import connection as urllib_connection
from urllib3.response import HTTPResponse as UrllibResponse
from urllib3.connection import HTTPConnection as UrllibConnection

from corehttp.rest import HttpRequest
from corehttp.transport.requests import RequestsTransport
from corehttp.runtime.pipeline import Pipeline
from corehttp.exceptions import ServiceResponseError, ServiceResponseTimeoutError, ServiceRequestTimeoutError


def test_already_close_with_with(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    # This is now closed, new requests should fail
    with pytest.raises(ValueError) as err:
        transport.send(request)
    assert "HTTP transport has already been closed." in str(err)


def test_already_close_manually(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    transport.send(request)
    transport.close()

    # This is now closed, new requests should fail
    with pytest.raises(ValueError) as err:
        transport.send(request)
    assert "HTTP transport has already been closed." in str(err)


def test_close_too_soon_works_fine(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    transport.close()  # Never opened, should work fine
    result = transport.send(request)

    assert result  # No exception is good enough here


def test_requests_timeout_response(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", f"http://localhost:{port}/basic/string")

    with mock.patch.object(UrllibConnection, "getresponse", side_effect=SocketTimeout) as mock_method:
        with pytest.raises(ServiceResponseTimeoutError) as err:
            transport.send(request, read_timeout=0.0001)

        with pytest.raises(ServiceResponseError) as err:
            transport.send(request, read_timeout=0.0001)

        stream_request = HttpRequest("GET", f"http://localhost:{port}/streams/basic")
        with pytest.raises(ServiceResponseTimeoutError) as err:
            transport.send(stream_request, stream=True, read_timeout=0.0001)

    stream_resp = transport.send(stream_request, stream=True)
    with mock.patch.object(UrllibResponse, "_handle_chunk", side_effect=SocketTimeout) as mock_method:
        with pytest.raises(ServiceResponseTimeoutError) as err:
            stream_resp.read()


def test_requests_timeout_request(caplog, port):
    transport = RequestsTransport()

    request = HttpRequest("GET", f"http://localhost:{port}/basic/string")

    with mock.patch.object(urllib_connection, "create_connection", side_effect=SocketTimeout) as mock_method:
        with pytest.raises(ServiceRequestTimeoutError) as err:
            transport.send(request, connection_timeout=0.0001)

        with pytest.raises(ServiceRequestTimeoutError) as err:
            transport.send(request, connection_timeout=0.0001)

        stream_request = HttpRequest("GET", f"http://localhost:{port}/streams/basic")
        with pytest.raises(ServiceRequestTimeoutError) as err:
            transport.send(stream_request, stream=True, connection_timeout=0.0001)
