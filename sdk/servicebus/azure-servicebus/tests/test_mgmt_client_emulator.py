# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport

from azure.servicebus.aio.management import ServiceBusAdministrationClient as AsyncAdministrationClient
from azure.servicebus.management import ApiVersion, ServiceBusAdministrationClient


def _connection_string(host, flag):
    value = f"Endpoint=sb://{host};SharedAccessKeyName=TestPolicy;SharedAccessKey=TestKey;"
    return value if flag is None else value + f"UseDevelopmentEmulator={flag};"


def _assert_request(client, request, host, scheme):
    endpoint = f"{scheme}://{host}"
    assert client._endpoint == endpoint
    assert client._config.endpoint == endpoint
    assert client._impl._config.endpoint == endpoint
    url = urlsplit(request.url)
    assert url.scheme == scheme
    assert url.netloc == host
    assert url.path == "/test-queue"
    assert parse_qs(url.query) == {"enrich": ["false"], "api-version": [ApiVersion.V2024_05.value]}
    authorization = request.headers["Authorization"]
    assert authorization.startswith("SharedAccessSignature ")
    assert parse_qs(authorization.split(" ", 1)[1])["sr"] == [endpoint]


@pytest.mark.parametrize("host", ["127.0.0.1:5300", "localhost:5301", "[::1]:5302"])
@pytest.mark.parametrize("flag,scheme", [(None, "https"), ("false", "https"), ("true", "http")])
def test_sync_administration_request_scheme_and_signing(host, flag, scheme):
    transport = MagicMock(spec=HttpTransport)
    transport.send.side_effect = ServiceRequestError("request intercepted")
    with ServiceBusAdministrationClient.from_connection_string(
        _connection_string(host, flag), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="request intercepted"):
            client.get_queue("test-queue")
        transport.send.assert_called_once()
        _assert_request(client, transport.send.call_args.args[0], host, scheme)


@pytest.mark.asyncio
@pytest.mark.parametrize("host", ["127.0.0.1:5300", "localhost:5301", "[::1]:5302"])
@pytest.mark.parametrize("flag,scheme", [(None, "https"), ("false", "https"), ("true", "http")])
async def test_async_administration_request_scheme_and_signing(host, flag, scheme):
    transport = MagicMock(spec=AsyncHttpTransport)
    transport.send = AsyncMock(side_effect=ServiceRequestError("request intercepted"))
    async with AsyncAdministrationClient.from_connection_string(
        _connection_string(host, flag), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="request intercepted"):
            await client.get_queue("test-queue")
        transport.send.assert_awaited_once()
        _assert_request(client, transport.send.call_args.args[0], host, scheme)


@pytest.mark.parametrize("flag", [None, "false"])
def test_sync_cloud_connection_string_retains_https(flag):
    transport = MagicMock(spec=HttpTransport)
    transport.send.side_effect = ServiceRequestError("request intercepted")
    host = "example.servicebus.windows.net"
    with ServiceBusAdministrationClient.from_connection_string(
        _connection_string(host, flag), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="request intercepted"):
            client.get_queue("test-queue")
        _assert_request(client, transport.send.call_args.args[0], host, "https")


@pytest.mark.asyncio
@pytest.mark.parametrize("flag", [None, "false"])
async def test_async_cloud_connection_string_retains_https(flag):
    transport = MagicMock(spec=AsyncHttpTransport)
    transport.send = AsyncMock(side_effect=ServiceRequestError("request intercepted"))
    host = "example.servicebus.windows.net"
    async with AsyncAdministrationClient.from_connection_string(
        _connection_string(host, flag), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="request intercepted"):
            await client.get_queue("test-queue")
        _assert_request(client, transport.send.call_args.args[0], host, "https")


def test_sync_bearer_credential_rejects_http():
    credential = MagicMock()
    transport = MagicMock(spec=HttpTransport)
    with ServiceBusAdministrationClient(
        "localhost:5300", credential, use_tls=False, transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="non-https"):
            client.get_queue("test-queue")
    credential.get_token.assert_not_called()
    transport.send.assert_not_called()


@pytest.mark.asyncio
async def test_async_bearer_credential_rejects_http():
    credential = MagicMock()
    credential.get_token = AsyncMock()
    transport = MagicMock(spec=AsyncHttpTransport)
    async with AsyncAdministrationClient(
        "localhost:5300", credential, use_tls=False, transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="non-https"):
            await client.get_queue("test-queue")
    credential.get_token.assert_not_awaited()
    transport.send.assert_not_called()
