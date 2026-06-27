# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests that the ``{invocation_id}`` path param is sanitised before it is
reflected into the ``x-agent-invocation-id`` response header."""
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationConstants
from azure.ai.agentserver.invocations._invocation import _MAX_ID_LENGTH, _VALID_ID_RE

_HEADER = InvocationConstants.INVOCATION_ID_HEADER


def _build_app() -> InvocationAgentServerHost:
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        return Response(content=b"got")

    return app


async def _echoed_id(path_id: str) -> str:
    transport = ASGITransport(app=_build_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get(f"/invocations/{path_id}")
    return resp.headers[_HEADER]


@pytest.mark.asyncio
async def test_invalid_char_id_not_reflected_in_header():
    """A path id with characters outside the id allow-list is replaced by a
    safe fallback rather than echoed back verbatim."""
    echoed = await _echoed_id("bad~id")
    assert echoed != "bad~id"
    assert _VALID_ID_RE.match(echoed)


@pytest.mark.asyncio
async def test_overlong_id_not_reflected_in_header():
    """An over-length path id does not bypass the ``_MAX_ID_LENGTH`` cap."""
    echoed = await _echoed_id("a" * (_MAX_ID_LENGTH + 50))
    assert len(echoed) <= _MAX_ID_LENGTH
    assert _VALID_ID_RE.match(echoed)


@pytest.mark.asyncio
async def test_valid_id_passes_through_unchanged():
    """A well-formed path id is preserved so lookups keep working."""
    echoed = await _echoed_id("valid-id_123.abc")
    assert echoed == "valid-id_123.abc"
