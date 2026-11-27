# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Fakes for database create, read and delete tests.

The fakes stand in for the part of the SDK that sends requests to the service.
They keep each request they receive and return prepared replies, without a network.
"""

import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from common.async_test_helpers import run_async

from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy


def _created_response() -> BackendResponse:
    """Return a "201 Created" reply with the new database's body and a request charge header."""
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"db1","_rid":"rid1"}',
    )


class _FakeBackend(CosmosBackend):
    """Fake that keeps each request it receives and returns prepared replies."""

    name = "rust"

    def __init__(self, response=None, responses=None):
        """Store the replies to return.

        Pass one ``response``, or a list of ``responses`` to return in order. Once
        the list is down to its last reply, that reply is returned for every later
        call. By default, a "201 Created" database reply.
        """
        self.responses = list(responses or [response or _created_response()])
        self.prepared = None
        self.prepared_requests = []

    def execute(self, prepared, *, deadline=None):
        """Keep the request and return the next reply.

        ``prepared`` holds the latest request, and ``prepared_requests`` holds all of them.
        """
        self.prepared = prepared
        self.prepared_requests.append(prepared)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


class _AsyncFakeBackend(AsyncCosmosBackend):
    """Async version of ``_FakeBackend``."""

    name = "rust"

    def __init__(self, response=None, responses=None):
        """Store the replies to return. Works the same as ``_FakeBackend``."""
        self.prepared = None
        self.prepared_requests = []
        self.responses = list(responses or [response or _created_response()])

    async def execute(self, prepared, *, deadline=None):
        """Keep the request and return the next reply. Works the same as ``_FakeBackend``."""
        self.prepared = prepared
        self.prepared_requests.append(prepared)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


def make_database_read_case(is_async):
    """Set up a database object whose ``read`` calls go to a fake.

    Returns the setup for one test case:
    - ``proxy``: the database to call ``read`` on.
    - ``backend``: the fake. ``backend.execute`` is a mock, so a test can check
      how many requests were sent and what they contained.
    - ``connection``: ``connection.ReadDatabase`` fails the test if it is called.

    The database starts with saved properties whose ``_etag`` is ``"old"``, while
    the fake replies with ``"v1"``. Tests use this to check that a successful read
    replaces the saved properties and a failed read leaves them unchanged.
    """
    response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict(
            {"x-ms-activity-id": "read-one", "x-ms-request-charge": "1.5"}
        ),
        body=b'{"id":"db1","_etag":"v1"}',
        diagnostics="activity=read-one requests=1",
    )
    backend = _AsyncFakeBackend(response) if is_async else _FakeBackend(response)
    mock_type = AsyncMock if is_async else MagicMock
    backend.execute = mock_type(wraps=backend.execute)
    connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        ReadDatabase=mock_type(side_effect=AssertionError("ReadDatabase should not be called")),
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
    return run_async(result) if inspect.isawaitable(result) else result
