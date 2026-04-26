# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from unittest import mock
from socket import timeout as SocketTimeout

import httpx
from urllib3.util import connection as urllib_connection
from urllib3.response import HTTPResponse as UrllibResponse
from urllib3.connection import HTTPConnection as UrllibConnection

from corehttp.rest import HttpRequest
from corehttp.transport.requests import RequestsTransport
from corehttp.transport.httpx import HttpXTransport
from corehttp.runtime.pipeline import Pipeline
from corehttp.exceptions import ServiceResponseError, ServiceResponseTimeoutError, ServiceRequestTimeoutError


class MockRequestsSession:
    def __init__(self):
        self.request = mock.Mock(side_effect=RuntimeError("request sent"))

    def close(self):
        pass


def _make_httpx_client_mock():
    client = mock.create_autospec(httpx.Client, instance=True)
    client.request.side_effect = RuntimeError("request sent")
    return client


def test_requests_transport_rejects_unknown_kwargs():
    session = MockRequestsSession()
    transport = RequestsTransport(session=session, session_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(TypeError, match=r"RequestsTransport\.send\(\) got an unexpected keyword argument 'query_filter'"):
        transport.send(request, query_filter="PartitionKey eq 'pk001'")

    session.request.assert_not_called()


def test_requests_transport_consumes_supported_kwargs():
    session = MockRequestsSession()
    transport = RequestsTransport(session=session, session_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(RuntimeError, match="request sent"):
        transport.send(
            request,
            stream=True,
            connection_timeout=1,
            read_timeout=2,
            connection_verify=False,
            connection_cert="cert.pem",
        )

    kwargs = session.request.call_args.kwargs
    assert kwargs["stream"] is True
    assert kwargs["timeout"] == (1, 2)
    assert kwargs["verify"] is False
    assert kwargs["cert"] == "cert.pem"
    assert "read_timeout" not in kwargs
    assert "connection_timeout" not in kwargs
    assert "connection_verify" not in kwargs
    assert "connection_cert" not in kwargs


def test_httpx_transport_rejects_unknown_kwargs():
    client = _make_httpx_client_mock()
    transport = HttpXTransport(client=client, client_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(TypeError, match=r"HttpXTransport\.send\(\) got an unexpected keyword argument 'query_filter'"):
        transport.send(request, query_filter="PartitionKey eq 'pk001'")

    client.request.assert_not_called()


@pytest.mark.parametrize("tls_kwarg", ["connection_verify", "connection_cert"])
def test_httpx_transport_rejects_per_request_tls_kwargs(tls_kwarg):
    client = _make_httpx_client_mock()
    transport = HttpXTransport(client=client, client_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(TypeError, match=f"HttpXTransport.send\\(\\) got an unexpected keyword argument '{tls_kwarg}'"):
        transport.send(request, **{tls_kwarg: "cert.pem"})

    client.request.assert_not_called()


def test_httpx_transport_consumes_supported_kwargs():
    client = _make_httpx_client_mock()
    transport = HttpXTransport(client=client, client_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(RuntimeError, match="request sent"):
        transport.send(
            request,
            connection_timeout=1,
            read_timeout=2,
        )

    kwargs = client.request.call_args.kwargs
    assert kwargs["timeout"].connect == 1
    assert kwargs["timeout"].read == 2
    assert "connection_timeout" not in kwargs
    assert "read_timeout" not in kwargs


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
