# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Fakes for container create tests.

The fakes stand in for the part of the SDK that sends requests to the service.
They keep the request they receive and return a prepared reply, so a test can
check what would have been sent and what the caller gets back, without a network.
"""

import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from common.async_test_helpers import run_async

from azure.core.utils import CaseInsensitiveDict
from azure.cosmos import PartitionKey
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._client_context import CosmosClientContext
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError


def _created_container_response() -> BackendResponse:
    """Return a "201 Created" reply with the new container's body and a request charge header."""
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"c1","_rid":"rid1"}',
    )


class _FakeBackend(CosmosBackend):
    """Fake that keeps the request it receives and returns a prepared reply."""

    name = "rust"

    def __init__(self, response=None):
        """Store the reply to return. By default, a "201 Created" container reply."""
        self.response = response or _created_container_response()
        self.prepared = None

    def execute(self, prepared, *, deadline=None):
        """Keep the request and return the prepared reply."""
        self.prepared = prepared
        return self.response


class _AsyncFakeBackend(AsyncCosmosBackend):
    """Async version of ``_FakeBackend``.

    It extends the real ``AsyncCosmosBackend`` and replaces only ``execute``, so
    tests still run the SDK's real code for everything else.
    """

    name = "rust"

    def __init__(self, response=None):
        """Store the reply to return. By default, a "201 Created" container reply."""
        self.response = response or _created_container_response()
        self.prepared = None

    async def execute(self, prepared, *, deadline=None):
        """Keep the request and return the prepared reply."""
        self.prepared = prepared
        return self.response


def make_container_create_case(is_async):
    """Set up a database object whose ``create_container`` calls go to a fake.

    Tests run once with a sync client and once with an async client, because the
    two clients build their requests in separate code that could drift apart.

    Returns the setup for one test case:
    - ``database``: the database to call ``create_container`` on.
    - ``backend``: the fake. ``backend.execute`` is a mock, so a test can check
      how many requests were sent and what they contained.
    - ``connection``: ``CreateContainer`` and ``_set_container_properties_cache``
      are mocks, so a test can check whether they were called.
    - ``client_context``: the context the database uses to send requests.
    """
    backend = _AsyncFakeBackend() if is_async else _FakeBackend()
    mock_type = AsyncMock if is_async else MagicMock
    backend.execute = mock_type(wraps=backend.execute)
    headers = CaseInsensitiveDict({"x-ms-request-charge": "5.25"})
    properties = CosmosDict({"id": "c1", "_rid": "rid1"}, response_headers=headers)
    connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        CreateContainer=mock_type(return_value=properties),
        _set_container_properties_cache=MagicMock(),
    )
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    client_context = CosmosClientContext(backend)
    return SimpleNamespace(
        database=proxy_type(connection, "db1", _client_context=client_context),
        connection=connection,
        backend=backend,
        client_context=client_context,
    )


def _call_container_create(case, *args, method="create_container", **kwargs):
    """Call the named create method on the database and wait for it if the client is async.

    The method name is an argument because plain create and get-or-create share
    almost all of their rules, so most tests here run against both.
    """
    # Some tests replace connection._backend after setup. Point the database at
    # the replacement so the call uses it.
    if case.client_context.adapter is not case.connection._backend:
        case.client_context = CosmosClientContext(case.connection._backend)
        case.database._client_context = case.client_context
    result = getattr(case.database, method)(*args, **kwargs)
    return run_async(result) if inspect.isawaitable(result) else result


def make_container_get_or_create_case(case, missing):
    """Extend the setup from ``make_container_create_case`` to cover both outcomes of get-or-create.

    Adds ``missing`` and ``existing_properties`` to the setup and returns it.

    Each test runs twice: once where the container already exists (one request)
    and once where it does not (two requests). The method must return the
    same shape either way.

    The existing container is given a different partition key path and a
    different time to live from what the tests ask for. That lets a test
    check that the existing container is returned unchanged, not overwritten
    with the caller's arguments.

    When the container is missing, the fake first replies "404 Not Found" and
    then "201 Created", the same order the real service would reply in.
    """
    case.missing = missing
    case.existing_properties = CosmosDict(
        {
            "id": "c1",
            "_rid": "rid1",
            "partitionKey": {"paths": ["/original"]},
            "defaultTtl": 10,
        },
        response_headers=CaseInsensitiveDict({"x-ms-request-charge": "2"}),
    )
    mock_type = (
        AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    )
    if case.missing:
        case.connection.ReadContainer = mock_type(
            side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
        )
        case.backend.execute.side_effect = [
            BackendResponse(
                status_code=404,
                headers=CaseInsensitiveDict(),
                body=b'{"message":"missing"}',
            ),
            _created_container_response(),
        ]
    else:
        case.connection.ReadContainer = mock_type(return_value=case.existing_properties)
        case.backend.execute.side_effect = [
            BackendResponse(
                status_code=200,
                headers=case.existing_properties.get_response_headers(),
                body=json.dumps(case.existing_properties).encode(),
            ),
        ]
    return case


def _call_get_or_create(case, **kwargs):
    """Call ``create_container_if_not_exists`` with a fixed name and partition key."""
    return _call_container_create(
        case,
        "c1",
        PartitionKey(path="/pk"),
        method="create_container_if_not_exists",
        **kwargs
    )
