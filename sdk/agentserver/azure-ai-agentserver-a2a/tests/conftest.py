# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for A2A protocol tests."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def client_factory():
    """Create an in-process HTTP client for an ASGI application."""

    def create(app):
        return AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        )

    return create
