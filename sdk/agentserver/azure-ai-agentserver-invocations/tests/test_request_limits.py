# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for request processing (timeout feature removed per spec alignment)."""
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost



# ---------------------------------------------------------------------------
# InvocationAgentServerHost no longer accepts request_timeout
# ---------------------------------------------------------------------------

def test_no_request_timeout_parameter():
    """InvocationAgentServerHost no longer accepts request_timeout."""
    with pytest.raises(TypeError):
        InvocationAgentServerHost(request_timeout=10)


# ---------------------------------------------------------------------------
# Slow invoke completes without timeout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_slow_invoke_completes():
    """Without timeout, handler runs to completion."""
    import asyncio

    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        await asyncio.sleep(0.1)
        return Response(content=b"done")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    assert resp.status_code == 200
    assert resp.content == b"done"
