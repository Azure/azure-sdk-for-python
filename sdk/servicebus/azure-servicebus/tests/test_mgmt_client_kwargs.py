# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Unit tests verifying that ServiceBusAdministrationClient forwards
**kwargs from __init__ to _build_pipeline (both sync and async).

Regression test for https://github.com/Azure/azure-sdk-for-python/issues/44999
"""

from unittest.mock import AsyncMock, patch, MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest

from azure.servicebus.management import ApiVersion, ServiceBusAdministrationClient


class TestServiceBusAdministrationClientKwargs:
    """Verify kwargs like connection_verify and transport reach _build_pipeline."""

    def test_sync_build_pipeline_receives_kwargs(self):
        """Sync client should forward **kwargs to _build_pipeline."""
        credential = MagicMock()
        with patch.object(
            ServiceBusAdministrationClient,
            "_build_pipeline",
            return_value=MagicMock(),
        ) as mock_build:
            ServiceBusAdministrationClient(
                "fake.servicebus.windows.net",
                credential,
                connection_verify="/path/to/ca-bundle.crt",
            )
            mock_build.assert_called_once()
            call_kwargs = mock_build.call_args.kwargs
            assert call_kwargs.get("connection_verify") == "/path/to/ca-bundle.crt"

    def test_sync_build_pipeline_receives_custom_transport(self):
        """Sync client should forward a custom transport kwarg to _build_pipeline."""
        credential = MagicMock()
        custom_transport = MagicMock()
        with patch.object(
            ServiceBusAdministrationClient,
            "_build_pipeline",
            return_value=MagicMock(),
        ) as mock_build:
            ServiceBusAdministrationClient(
                "fake.servicebus.windows.net",
                credential,
                transport=custom_transport,
            )
            mock_build.assert_called_once()
            call_kwargs = mock_build.call_args.kwargs
            assert call_kwargs.get("transport") is custom_transport

    def test_sync_v2024_05_reaches_management_request(self):
        """The public API version should reach the generated request query."""
        credential = MagicMock()
        with patch.object(ServiceBusAdministrationClient, "_build_pipeline", return_value=MagicMock()):
            client = ServiceBusAdministrationClient(
                "fake.servicebus.windows.net",
                credential,
                api_version=ApiVersion.V2024_05,
            )

        pipeline_response = MagicMock()
        pipeline_response.http_response.status_code = 200
        client._impl.entity._client._pipeline.run = MagicMock(return_value=pipeline_response)
        client._impl.entity._deserialize = MagicMock(return_value={})

        client._impl.entity.get("queue")

        request = client._impl.entity._client._pipeline.run.call_args.args[0]
        assert parse_qs(urlsplit(request.url).query)["api-version"] == [ApiVersion.V2024_05.value]


@pytest.mark.asyncio
class TestServiceBusAdministrationClientKwargsAsync:
    """Verify kwargs reach _build_pipeline on the async client."""

    async def test_async_build_pipeline_receives_kwargs(self):
        """Async client should forward **kwargs to _build_pipeline."""
        from azure.servicebus.aio.management import (
            ServiceBusAdministrationClient as AsyncClient,
        )

        credential = MagicMock()
        with patch.object(
            AsyncClient,
            "_build_pipeline",
            return_value=MagicMock(),
        ) as mock_build:
            AsyncClient(
                "fake.servicebus.windows.net",
                credential,
                connection_verify="/path/to/ca-bundle.crt",
            )
            mock_build.assert_called_once()
            call_kwargs = mock_build.call_args.kwargs
            assert call_kwargs.get("connection_verify") == "/path/to/ca-bundle.crt"

    async def test_async_build_pipeline_receives_custom_transport(self):
        """Async client should forward a custom transport kwarg to _build_pipeline."""
        from azure.servicebus.aio.management import (
            ServiceBusAdministrationClient as AsyncClient,
        )

        credential = MagicMock()
        custom_transport = MagicMock()
        with patch.object(
            AsyncClient,
            "_build_pipeline",
            return_value=MagicMock(),
        ) as mock_build:
            AsyncClient(
                "fake.servicebus.windows.net",
                credential,
                transport=custom_transport,
            )
            mock_build.assert_called_once()
            call_kwargs = mock_build.call_args.kwargs
            assert call_kwargs.get("transport") is custom_transport

    async def test_async_v2024_05_reaches_management_request(self):
        """The public API version should reach the generated async request query."""
        from azure.servicebus.aio.management import (
            ServiceBusAdministrationClient as AsyncClient,
        )

        credential = MagicMock()
        with patch.object(AsyncClient, "_build_pipeline", return_value=MagicMock()):
            client = AsyncClient(
                "fake.servicebus.windows.net",
                credential,
                api_version=ApiVersion.V2024_05,
            )

        pipeline_response = MagicMock()
        pipeline_response.http_response.status_code = 200
        client._impl.entity._client._pipeline.run = AsyncMock(return_value=pipeline_response)
        client._impl.entity._deserialize = MagicMock(return_value={})

        await client._impl.entity.get("queue")

        request = client._impl.entity._client._pipeline.run.call_args.args[0]
        assert parse_qs(urlsplit(request.url).query)["api-version"] == [ApiVersion.V2024_05.value]
