# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy connection fixtures retained by container feed migration tests."""

from unittest.mock import MagicMock

from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.contracts import BackendPage
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._cosmos_client_connection import (
    CosmosClientConnection as SyncConnection,
)
from azure.cosmos._helpers._client_context import ClientLastResponseHeaders
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncConnection,
)
from azure.cosmos.documents import ConnectionPolicy


class _CapturingPagedBackend(CosmosBackend):
    """Records the paged request it was handed and yields one canned page."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body to yield and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    def execute_pages(self, prepared, *, deadline=None):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield BackendPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    def execute(self, prepared, *, deadline=None):
        """Fail immediately -- a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


class _CapturingAsyncPagedBackend(AsyncCosmosBackend):
    """Record the page request produced by asynchronous container methods."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    async def execute_pages(self, prepared, *, deadline=None):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield BackendPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    async def execute(self, prepared, *, deadline=None):
        """Fail immediately -- a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


def _new_sync_connection() -> SyncConnection:
    """Build a minimal ``SyncConnection`` with no live transport, for routing tests."""
    conn = SyncConnection.__new__(SyncConnection)
    conn._setup_complete = True
    conn._response_state = ClientLastResponseHeaders()
    conn._backend = LEGACY_BACKEND
    conn._query_compatibility_mode = SyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_executor = None
    return conn


def _new_async_connection() -> AsyncConnection:
    """Build a minimal ``AsyncConnection`` with no live transport, for routing tests."""
    conn = AsyncConnection.__new__(AsyncConnection)
    conn._setup_complete = True
    conn._response_state = ClientLastResponseHeaders()
    conn._backend = ASYNC_LEGACY_BACKEND
    conn._query_compatibility_mode = AsyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_max_concurrency = None
    return conn
