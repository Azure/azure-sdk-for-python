# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

from unittest.mock import AsyncMock

import pytest

aiohttp = pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from aiohttp import web
from aiohttp.test_utils import TestServer as AiohttpTestServer

from azure.ai.voicelive.aio import ConnectionError, connect
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential


@pytest.fixture(params=["api-key", "Authorization"])
def credential_and_headers(request):
    if request.param == "api-key":
        return AzureKeyCredential("fake-key"), {"api-key": "fake-key"}

    credential = AsyncMock(spec=AsyncTokenCredential)
    credential.get_token.return_value = AccessToken("fake-token", 2147483647)
    return credential, {"Authorization": "Bearer fake-token"}


@pytest.fixture(params=["model", "agent"])
def connection_kwargs(request):
    if request.param == "model":
        return {"model": "gpt-4o"}
    return {"agent_name": "test-agent", "project_name": "test-project"}


@pytest.fixture
def client_sessions(monkeypatch):
    sessions = []
    original_client_session = aiohttp.ClientSession

    def create_session(*args, **kwargs):
        session = original_client_session(*args, **kwargs)
        sessions.append(session)
        return session

    monkeypatch.setattr(aiohttp, "ClientSession", create_session)
    return sessions


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("cross_origin", [False, True], ids=["same-origin", "cross-origin"])
async def test_websocket_redirects_are_rejected(
    status, cross_origin, credential_and_headers, connection_kwargs, client_sessions
):
    credential, expected_headers = credential_and_headers
    initial_requests = []
    redirected_requests = []

    async def capture_redirect(request):
        redirected_requests.append(dict(request.headers))
        return web.Response(status=403)

    target_app = web.Application()
    target_app.router.add_get("/redirected", capture_redirect)

    # Different ports provide cross-origin coverage without requiring another loopback address.
    async with AiohttpTestServer(target_app, host="127.0.0.1") as target:

        async def redirect(request):
            initial_requests.append(dict(request.headers))
            location = str(target.make_url("/redirected")) if cross_origin else "/redirected"
            return web.Response(status=status, headers={"Location": location})

        source_app = web.Application()
        source_app.router.add_get("/voice-live/realtime", redirect)
        source_app.router.add_get("/redirected", capture_redirect)

        async with AiohttpTestServer(source_app, host="127.0.0.1") as source:
            with pytest.raises(ConnectionError) as exc_info:
                async with connect(
                    credential=credential,
                    endpoint=str(source.make_url("")),
                    **connection_kwargs,
                ):
                    pytest.fail("A redirected WebSocket handshake must not succeed.")

    assert len(initial_requests) == 1
    for header, value in expected_headers.items():
        assert initial_requests[0][header] == value
    assert redirected_requests == []
    assert "WebSocket redirects are not supported." in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, aiohttp.ClientError)
    assert len(client_sessions) == 1
    assert client_sessions[0].closed


@pytest.mark.asyncio
async def test_nonredirected_websocket_handshake_succeeds(
    credential_and_headers, connection_kwargs, client_sessions
):
    credential, expected_headers = credential_and_headers
    initial_requests = []

    async def accept_websocket(request):
        initial_requests.append(dict(request.headers))
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        await websocket.close()
        return websocket

    app = web.Application()
    app.router.add_get("/voice-live/realtime", accept_websocket)

    async with AiohttpTestServer(app, host="127.0.0.1") as server:
        async with connect(
            credential=credential,
            endpoint=str(server.make_url("")),
            **connection_kwargs,
        ):
            assert len(client_sessions) == 1
            assert not client_sessions[0].closed

    assert len(initial_requests) == 1
    for header, value in expected_headers.items():
        assert initial_requests[0][header] == value
    assert client_sessions[0].closed
