# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, Mock
from urllib.parse import urlparse

import pytest
import requests
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import AioHttpTransport, RequestsTransport
from azure.communication.callautomation import CallAutomationClient
from azure.communication.callautomation.aio import CallAutomationClient as AsyncCallAutomationClient
from azure.communication.callautomation._recording_url_validator import validate_recording_url

from unittest_helpers import mock_response

ENDPOINT = "https://example.communication.azure.com"
VALID_URL = "https://x.asm.skype.com/recording?sig=a%2Fb%3D&part=1"
BYPASS_URL = "https://127.0.0.1:8443\\@x.asm.skype.com/recording"
OPERATIONS = ("download_recording", "delete_recording")
INVALID_URLS = [
    BYPASS_URL,
    "https://127.0.0.1:8443\\\\@x.asm.skype.com/recording",
    "https://user:password@x.asm.skype.com/recording",
    "https://127.0.0.1:8443/recording",
    "https://x.asm.skype.com.attacker.example/recording",
    "https://asm.skype.com/recording",
    "http://x.asm.skype.com/recording",
    "//x.asm.skype.com/recording",
    "https://x.asm.skype.com:/recording",
    "https://x.asm.skype.com:invalid/recording",
    "https://x.asm.skype.com:65536/recording",
    "https://%78.asm.skype.com/recording",
    "https://bad_host.asm.skype.com/recording",
    "https://x..asm.skype.com/recording",
    "https://[x.asm.skype.com]/recording",
    "https://\u212a.asm.skype.com/recording",
] + [f"https://x.asm.skype.com/record{chr(code)}ing" for code in (*range(33), 127, 133)]


@pytest.fixture(autouse=True)
def start_proxy():
    # These tests must not start the service test proxy or make network requests.
    return


def credential(async_client=False):
    get_token = AsyncMock if async_client else Mock
    return Mock(
        spec=["get_token"],
        get_token=get_token(return_value=AccessToken("ACS-CALLAUTOMATION-CANARY-TOKEN", int(time.time()) + 3600)),
    )


@pytest.mark.parametrize("operation", OPERATIONS)
def test_rejects_backslash_before_authentication(operation):
    token = credential()
    transport = MagicMock(send=Mock(return_value=mock_response()))
    with CallAutomationClient(ENDPOINT, token, transport=transport) as client:
        with pytest.raises(ValueError):
            getattr(client, operation)(BYPASS_URL)
    token.get_token.assert_not_called()
    transport.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", OPERATIONS)
async def test_async_rejects_backslash_before_authentication(operation):
    token = credential(async_client=True)
    transport = MagicMock(send=AsyncMock(return_value=mock_response()))
    async with AsyncCallAutomationClient(ENDPOINT, token, transport=transport) as client:
        with pytest.raises(ValueError):
            await getattr(client, operation)(BYPASS_URL)
    token.get_token.assert_not_called()
    transport.send.assert_not_called()


@pytest.mark.parametrize("url", INVALID_URLS)
def test_rejects_ambiguous_or_external_url(url):
    with pytest.raises(ValueError):
        validate_recording_url(url, "recording_url")


@pytest.mark.parametrize(
    "url",
    [
        VALID_URL,
        "https://x.asyncgw.teams.microsoft.com/recording",
        "https://x.ams.gov.teams.microsoft.us/recording",
        "https://xn--bcher-kva.asm.skype.com/recording",
        "https://x.asm.skype.com:8443/recording",
        "https://x.asm.skype.com/recording%5C%40example?sig=a%2Fb%3D",
    ],
)
def test_preserves_valid_recording_url(url):
    assert validate_recording_url(url, "recording_url") == url


def test_canonicalizes_authority_without_changing_signature():
    url = "HTTPS://X.ASM.SKYPE.COM:443/Recording;param?sig=a%2Fb%3D#fragment"
    assert validate_recording_url(url, "recording_url") == (
        "https://x.asm.skype.com:443/Recording;param?sig=a%2Fb%3D#fragment"
    )


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize(
    "location",
    [
        BYPASS_URL,
        "https://attacker.example/recording",
        "//attacker.example/recording",
        "http://x.asm.skype.com/recording",
        "https://user@x.asm.skype.com/recording",
        "https://x.asm.skype.com/record\ning",
    ],
)
def test_rejects_unsafe_redirect(operation, location):
    transport = MagicMock(send=Mock(return_value=mock_response(307, {"location": location})))
    with CallAutomationClient(ENDPOINT, credential(), transport=transport) as client:
        with pytest.raises(ValueError):
            getattr(client, operation)(VALID_URL, permit_redirects=True)
    assert transport.send.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("location", [BYPASS_URL, "//attacker.example/recording", "https://x.asm.skype.com/a\tb"])
async def test_async_rejects_unsafe_redirect(operation, location):
    transport = MagicMock(send=AsyncMock(return_value=mock_response(307, {"location": location})))
    async with AsyncCallAutomationClient(ENDPOINT, credential(async_client=True), transport=transport) as client:
        with pytest.raises(ValueError):
            await getattr(client, operation)(VALID_URL, permit_redirects=True)
    assert transport.send.call_count == 1


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("location", ["/next?sig=a%2Fb", "https://other.asm.skype.com/next?sig=a%2Fb"])
def test_preserves_allowed_redirects(operation, location):
    urls = []

    def send(request, **kwargs):
        urls.append(request.url)
        return mock_response(307, {"location": location}) if len(urls) == 1 else mock_response()

    with CallAutomationClient(ENDPOINT, credential(), transport=MagicMock(send=send)) as client:
        getattr(client, operation)(VALID_URL)
    expected = "https://x.asm.skype.com" + location if location.startswith("/") else location
    assert urls == [VALID_URL, expected]


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("location", ["/next?sig=a%2Fb", "https://other.asm.skype.com/next?sig=a%2Fb"])
async def test_async_preserves_allowed_redirects(operation, location):
    urls = []

    async def send(request, **kwargs):
        urls.append(request.url)
        return mock_response(307, {"location": location}) if len(urls) == 1 else mock_response()

    transport = MagicMock(send=AsyncMock(side_effect=send))
    async with AsyncCallAutomationClient(ENDPOINT, credential(async_client=True), transport=transport) as client:
        await getattr(client, operation)(VALID_URL)
    expected = "https://x.asm.skype.com" + location if location.startswith("/") else location
    assert urls == [VALID_URL, expected]


class CaptureAdapter(requests.adapters.BaseAdapter):
    def __init__(self, redirect_url=None):
        self.requests = []
        self.redirect_url = redirect_url

    def send(self, request, **kwargs):
        self.requests.append(request)
        if self.redirect_url and len(self.requests) == 1:
            response = requests.Response()
            response.status_code = 307
            response.headers["location"] = self.redirect_url
            response.raw = BytesIO(b"")
            response._content = b""
            response.request = request
            response.url = request.url
            return response
        raise AssertionError("No network request should be made")

    def close(self):
        pass


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("url", INVALID_URLS)
def test_requests_transport_rejects_invalid_url(operation, url):
    adapter = CaptureAdapter()
    token = credential()
    with requests.Session() as session:
        session.mount("https://", adapter)
        with CallAutomationClient(ENDPOINT, token, transport=RequestsTransport(session=session)) as client:
            with pytest.raises(ValueError):
                getattr(client, operation)(url)
    assert adapter.requests == []
    token.get_token.assert_not_called()


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("location", [BYPASS_URL, "https://attacker.example/recording"])
def test_requests_transport_rejects_unsafe_redirect(operation, location):
    adapter = CaptureAdapter(redirect_url=location)
    with requests.Session() as session:
        session.mount("https://", adapter)
        with CallAutomationClient(ENDPOINT, credential(), transport=RequestsTransport(session=session)) as client:
            with pytest.raises(ValueError):
                getattr(client, operation)(VALID_URL)
    assert len(adapter.requests) == 1
    assert adapter.requests[0].url == VALID_URL


@pytest.mark.parametrize("operation", OPERATIONS)
def test_requests_transport_uses_validated_destination(operation):
    adapter = CaptureAdapter()
    with requests.Session() as session:
        session.mount("https://", adapter)
        with CallAutomationClient(ENDPOINT, credential(), transport=RequestsTransport(session=session)) as client:
            with pytest.raises(AssertionError, match="No network request"):
                getattr(client, operation)(VALID_URL)
    assert len(adapter.requests) == 1
    assert adapter.requests[0].url == VALID_URL
    assert adapter.requests[0].headers["Authorization"] == "Bearer ACS-CALLAUTOMATION-CANARY-TOKEN"
    assert urlparse(adapter.requests[0].url).hostname == "x.asm.skype.com"


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("url", INVALID_URLS + [VALID_URL])
async def test_aiohttp_transport_destination(operation, url):
    import aiohttp

    destinations = []
    trace = aiohttp.TraceConfig()

    async def on_request_start(session, context, params):
        destinations.append(params)
        raise AssertionError("Stop before network I/O")

    trace.on_request_start.append(on_request_start)
    token = credential(async_client=True)
    async with aiohttp.ClientSession(trace_configs=[trace]) as session:
        transport = AioHttpTransport(session=session, session_owner=False)
        async with AsyncCallAutomationClient(ENDPOINT, token, transport=transport) as client:
            if url != VALID_URL:
                with pytest.raises(ValueError):
                    await getattr(client, operation)(url)
                assert destinations == []
                token.get_token.assert_not_called()
            else:
                with pytest.raises(AssertionError, match="Stop before network"):
                    await getattr(client, operation)(url)
                assert len(destinations) == 1
                assert destinations[0].url.host == "x.asm.skype.com"
                assert destinations[0].headers["Authorization"] == "Bearer ACS-CALLAUTOMATION-CANARY-TOKEN"
