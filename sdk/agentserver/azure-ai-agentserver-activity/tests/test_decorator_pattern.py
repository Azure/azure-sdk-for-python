# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the decorator-based activity handler pattern."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost


@pytest.mark.asyncio
async def test_decorator_registers_handler():
    """Verify that @app.activity() wires up the bridge handler."""
    app = ActivityAgentServerHost(configure_observability=None)

    @app.activity("message")
    async def on_message(context, state):
        pass

    # After decorating, _handler should be set to the bridge
    assert app._handler is not None


@pytest.mark.asyncio
async def test_error_decorator_registers_handler():
    """Verify that @app.error wires up the bridge handler."""
    app = ActivityAgentServerHost(configure_observability=None)

    @app.error
    async def on_error(context, error):
        pass

    assert app._handler is not None
