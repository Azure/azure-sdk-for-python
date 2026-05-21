# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared helpers for unit-testing AIProjectClient.get_openai_client (sync and async).

These helpers build lightweight client stubs that bypass the real ``__init__`` so unit
tests can target individual branches of ``get_openai_client`` without making any
network calls.
"""

from typing import Optional
from unittest.mock import MagicMock

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

ENDPOINT = "https://myaccount.services.ai.azure.com/api/projects/myproject"
API_VERSION = "2025-01-01"

# Patch targets used by tests to swap in mocked OpenAI/AsyncOpenAI constructors
# and bearer-token providers.
SYNC_OPENAI_PATCH = "azure.ai.projects._patch.OpenAI"
ASYNC_OPENAI_PATCH = "azure.ai.projects.aio._patch.AsyncOpenAI"
SYNC_TOKEN_PROVIDER_PATCH = "azure.ai.projects._patch.get_bearer_token_provider"
ASYNC_TOKEN_PROVIDER_PATCH = "azure.ai.projects.aio._patch.get_bearer_token_provider"


def make_sync_client(
    allow_preview: bool = True,
    console_logging: bool = False,
    custom_user_agent: Optional[str] = None,
) -> AIProjectClient:
    """Return a minimal sync AIProjectClient stub suitable for unit-testing get_openai_client."""
    client = AIProjectClient.__new__(AIProjectClient)
    client._config = MagicMock()
    client._config.endpoint = ENDPOINT
    client._config.allow_preview = allow_preview
    client._config.api_version = API_VERSION
    client._config.credential = MagicMock()
    client._console_logging_enabled = console_logging
    client._custom_user_agent = custom_user_agent
    return client


def make_async_client(
    allow_preview: bool = True,
    console_logging: bool = False,
    custom_user_agent: Optional[str] = None,
) -> AsyncAIProjectClient:
    """Return a minimal async AIProjectClient stub suitable for unit-testing get_openai_client."""
    client = AsyncAIProjectClient.__new__(AsyncAIProjectClient)
    client._config = MagicMock()
    client._config.endpoint = ENDPOINT
    client._config.allow_preview = allow_preview
    client._config.api_version = API_VERSION
    client._config.credential = MagicMock()
    client._console_logging_enabled = console_logging
    client._custom_user_agent = custom_user_agent
    return client


def mock_openai(user_agent: str = "openai/1.0"):
    """Return ``(mock_class, mock_instance)`` where ``mock_class`` acts as the OpenAI constructor."""
    instance = MagicMock()
    instance.user_agent = user_agent
    mock_cls = MagicMock(return_value=instance)
    return mock_cls, instance
