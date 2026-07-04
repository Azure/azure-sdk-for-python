# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests that the ``{invocation_id}`` path param is sanitised before it is
reflected into the ``x-agent-invocation-id`` response header. Both
``GET /invocations/{id}`` and ``POST /invocations/{id}/cancel`` run through
the same traced endpoint, so each scenario is exercised on both routes."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationConstants

_HEADER = InvocationConstants.INVOCATION_ID_HEADER

# (method, url template) for the two endpoints that echo the id header.
_ENDPOINTS = [
    ("GET", "/invocations/{id}"),
    ("POST", "/invocations/{id}/cancel"),
]


def _is_uuid(value: str) -> bool:
    """A rejected id falls back to a freshly generated UUID, so the safe
    replacement is observable from the header alone without reaching into
    the package internals."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _build_app() -> InvocationAgentServerHost:
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        return Response(content=b"got")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        return Response(content=b"cancelled")

    return app


async def _echoed_id(method: str, url: str) -> str:
    transport = ASGITransport(app=_build_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.request(method, url)
    # Assert the request actually succeeded and the header is present so a
    # failure points at the real cause rather than a bare KeyError.
    assert resp.status_code == 200, f"unexpected status {resp.status_code} for {method} {url}"
    assert _HEADER in resp.headers, f"{_HEADER} missing from response headers"
    return resp.headers[_HEADER]


@pytest.mark.asyncio
@pytest.mark.parametrize("method,template", _ENDPOINTS)
async def test_invalid_char_id_not_reflected_in_header(method, template):
    """A path id with characters outside the id allow-list is replaced by a
    safe fallback rather than echoed back verbatim."""
    echoed = await _echoed_id(method, template.format(id="bad~id"))
    assert echoed != "bad~id"
    assert _is_uuid(echoed)


@pytest.mark.asyncio
@pytest.mark.parametrize("method,template", _ENDPOINTS)
async def test_overlong_id_not_reflected_in_header(method, template):
    """An over-length path id is dropped in favour of the safe fallback."""
    long_id = "a" * 300
    echoed = await _echoed_id(method, template.format(id=long_id))
    assert echoed != long_id
    assert _is_uuid(echoed)


@pytest.mark.asyncio
@pytest.mark.parametrize("method,template", _ENDPOINTS)
async def test_valid_id_passes_through_unchanged(method, template):
    """A well-formed path id is preserved so lookups keep working."""
    echoed = await _echoed_id(method, template.format(id="valid-id_123.abc"))
    assert echoed == "valid-id_123.abc"
