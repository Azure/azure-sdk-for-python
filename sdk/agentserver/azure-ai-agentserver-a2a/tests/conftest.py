# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for A2A protocol tests."""

import os

os.environ["OTEL_INSTRUMENTATION_A2A_SDK_ENABLED"] = "false"

import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from a2a.server.request_handlers import DefaultRequestHandler

from azure.ai.agentserver.a2a import A2AAgentServerHost


@pytest_asyncio.fixture
async def client_factory():
    """Create an in-process HTTP client for an ASGI application."""

    clients = []
    hosts = {}

    def create(app):
        client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        )
        clients.append(client)
        if isinstance(app, A2AAgentServerHost):
            hosts[id(app)] = app
        return client

    try:
        yield create
    finally:
        for client in reversed(clients):
            await client.aclose()
        for host in reversed(list(hosts.values())):
            handler = host.request_handler
            if isinstance(handler, DefaultRequestHandler) and host._owned_request_handler is None:
                await handler.aclose()
            await host._dispatch_shutdown()
