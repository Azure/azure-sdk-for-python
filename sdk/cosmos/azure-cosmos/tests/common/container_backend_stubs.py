# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container backend stand-ins shared by maintained and temporary legacy tests."""

import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

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
    """Return a canned 201 Created reply carrying a new container body and a request-charge header."""
    # A canned "201 Created" reply: the new container's body plus a
    # request-charge header, used by the fake backends below.
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"c1","_rid":"rid1"}',
    )


class _BindingAdapter(CosmosBackend):
    """Stand-in Rust backend: records the request it was handed and returns a
    canned reply, so a test can check what would have gone on the wire."""

    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    def execute(self, prepared, *, deadline=None):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


class _AsyncBindingAdapter(AsyncCosmosBackend):
    """Async stand-in Rust backend: records the request it was handed and returns
    a canned reply.

    Subclasses the real ``AsyncCosmosBackend`` and overrides only ``execute``, so
    the routing and no-fallback logic under test is the shipping one
    rather than a copy of it that could drift.
    """

    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    async def execute(self, prepared, *, deadline=None):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


def make_container_create_case(is_async):
    """Build a container create that runs once as a sync client and once as async.

    Both clients are driven through the same tests because the sync and async
    paths build their requests through separate code and could drift apart.

    The connection is a stand-in with a recording ``CreateContainer`` for the
    legacy route and a recording cache write, so a test can prove which route ran
    and whether the new container's properties were remembered.

    No legacy implementation is imported or constructed. Temporary comparisons
    supply their own legacy backend separately.
    """
    backend = _AsyncBindingAdapter() if is_async else _BindingAdapter()
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
    if case.client_context.adapter is not case.connection._backend:
        case.client_context = CosmosClientContext(case.connection._backend)
        case.database._client_context = case.client_context
    result = getattr(case.database, method)(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def make_container_get_or_create_case(case, missing):
    """Extend the create setup to cover both outcomes of get-or-create.

    Each test runs twice: once where the container already exists and once where
    it does not. Those are two genuinely different paths -- one request or two --
    and the method has to return the same shape either way.

    The existing container is deliberately given settings that differ from what
    the tests ask for: a different partition key path and a different time to
    live. That lets a test prove the existing definition is returned untouched
    rather than quietly overwritten with the caller's arguments.

    The missing case is staged as a not-found reply followed by a created reply,
    which is the real two-step sequence.
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
