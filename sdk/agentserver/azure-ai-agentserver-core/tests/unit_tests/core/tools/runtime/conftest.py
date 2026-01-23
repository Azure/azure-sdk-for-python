# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for runtime unit tests.

Common fixtures are inherited from the parent conftest.py automatically by pytest.
"""
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_foundry_tool_client():
    """Create a mock FoundryToolClient."""
    client = AsyncMock()
    client.list_tools = AsyncMock(return_value=[])
    client.list_tools_details = AsyncMock(return_value={})
    client.invoke_tool = AsyncMock(return_value={"result": "success"})
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture
def mock_user_provider(sample_user_info):
    """Create a mock UserProvider."""
    provider = AsyncMock()
    provider.get_user = AsyncMock(return_value=sample_user_info)
    return provider


@pytest.fixture
def mock_user_provider_none():
    """Create a mock UserProvider that returns None."""
    provider = AsyncMock()
    provider.get_user = AsyncMock(return_value=None)
    return provider

