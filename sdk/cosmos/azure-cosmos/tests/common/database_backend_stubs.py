# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Database backend stand-ins shared by read, create, and delete unit tests."""

import asyncio
import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy


def _created_response() -> BackendResponse:
    """Return a successful fake database-create response."""
    # A canned "201 Created" reply from the Rust backend: the new database's body
    # plus a request-charge header, used by the fake backends below.
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"db1","_rid":"rid1"}',
    )


class _BindingAdapter(CosmosBackend):
    """Record prepared inputs and return canned replies, without native execution or I/O."""

    name = "rust"

    def __init__(self, response=None, responses=None):
        """Store the canned reply (or queue of replies) the stub will return on each ``execute`` call."""
        self.responses = list(responses or [response or _created_response()])
        self.prepared = None
        self.prepared_requests = []

    def execute(self, prepared, *, deadline=None):
        """Record the prepared request and return the next canned reply from the queue."""
        self.prepared = prepared
        self.prepared_requests.append(prepared)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


class _AsyncBindingAdapter(AsyncCosmosBackend):
    """Async stand-in Rust backend: records the request and returns the canned reply."""

    name = "rust"

    def __init__(self, response=None, responses=None):
        """Store the canned reply (or queue of replies) the async stub will return on each ``execute`` call."""
        self.prepared = None
        self.prepared_requests = []
        self.responses = list(responses or [response or _created_response()])

    async def execute(self, prepared, *, deadline=None):
        """Record the prepared request and return the next canned reply from the queue."""
        self.prepared = prepared
        self.prepared_requests.append(prepared)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


def make_database_read_case(is_async):
    """Build a Rust-backed proxy with stale properties and a forbidden legacy call."""
    response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict(
            {"x-ms-activity-id": "read-one", "x-ms-request-charge": "1.5"}
        ),
        body=b'{"id":"db1","_etag":"v1"}',
        diagnostics="activity=read-one requests=1",
    )
    backend = _AsyncBindingAdapter(response) if is_async else _BindingAdapter(response)
    mock_type = AsyncMock if is_async else MagicMock
    backend.execute = mock_type(wraps=backend.execute)
    connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        ReadDatabase=mock_type(side_effect=AssertionError("legacy read called")),
    )
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    return SimpleNamespace(
        proxy=proxy_type(connection, "db1", properties={"id": "db1", "_etag": "old"}),
        connection=connection,
        backend=backend,
    )


def _call_database_read(case, *args, **kwargs):
    """Call ``proxy.read`` and wait for it if the async proxy is under test.

    Lets one test body cover both the sync and the async proxy.
    """
    result = case.proxy.read(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result
