"""Unit coverage for create-database backend routing (no network).

These lock in how ``CosmosClient.create_database`` runs on the migrated path: the
public method stays a thin delegate that names no engine, the database coordinator
builds the account-level request and routes it to the rust backend when the call
can run there and to the legacy path otherwise, and the created database comes back
the same either way. All fakes, no Cosmos account.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse, CosmosBackend
from azure.cosmos._backend.base import OP_CREATE_DATABASE, OP_TO_BINDING_METHOD
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_prep import build_create_database_prepared
from azure.cosmos._helpers.database_helper import DatabaseHelper
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._cosmos_client import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._helpers.database_helper import AsyncDatabaseHelper
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.exceptions import CosmosResourceExistsError
from azure.cosmos.offer import ThroughputProperties


def _created_response() -> BackendResponse:
    # A canned "201 Created" reply from the rust backend: the new database's body
    # plus a request-charge header, used by the fake backends below.
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"db1","_rid":"rid1"}',
    )


def test_create_database_is_registered_as_single_response_operation():
    """Create-database is wired as a single-reply operation, so it dispatches to the
    binding's ``create_database`` entry point rather than the paged query path."""
    assert OP_TO_BINDING_METHOD[OP_CREATE_DATABASE] == "create_database"


def test_create_database_prepared_request_preserves_body_and_options():
    """The request handed to the rust backend carries everything the create needs:
    the database body, account-level scope (empty container link, cross-partition
    ``"[]"`` header since there is no partition key), and every option the customer
    set -- fixed throughput, autoscale settings, throughput bucket, custom headers,
    and the timeout deadline."""
    autoscale = '{"maxThroughput":4000}'
    prepared = build_create_database_prepared(
        {"id": "db1"},
        {
            "offerThroughput": 400,
            "autoUpgradePolicy": autoscale,
            "throughputBucket": 7,
            "initialHeaders": {"x-custom": "value"},
        },
        kwargs={"timeout": 3.5},
    )

    assert prepared.op == OP_CREATE_DATABASE
    assert prepared.container_link == ""
    assert prepared.partition_key_header == "[]"
    assert json.loads(prepared.body_bytes) == {"id": "db1"}
    assert prepared.headers["offerThroughput"] == 400
    assert prepared.headers["autoUpgradePolicy"] == autoscale
    assert prepared.headers["throughputBucket"] == 7
    assert prepared.headers["initialHeaders"] == {"x-custom": "value"}
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5


@pytest.mark.parametrize(
    "database,error_message",
    [
        ({"id": "bad/"}, "Id contains illegal chars."),
        ({"id": "bad "}, "Id ends with a space or newline."),
        ({"id": 1}, "Id type must be a string."),
    ],
)
def test_create_database_prepared_preserves_legacy_id_validation(database, error_message):
    """A bad database id (illegal characters, a trailing space, or a non-string) is
    rejected while building the request -- before anything is sent -- exactly as the
    legacy path rejected it, so the customer gets the same clear error."""
    with pytest.raises((TypeError, ValueError), match=error_message):
        build_create_database_prepared(database, {})


class _RustBackend(CosmosBackend):
    """Stand-in rust backend: records the request it was handed and returns a canned
    reply, so a test can check what would have gone on the wire without a network."""
    name = "rust"

    def __init__(self, response=None):
        self.response = response or _created_response()
        self.prepared = None

    def execute(self, prepared):
        self.prepared = prepared
        return self.response


def test_sync_helper_routes_to_rust_and_parses_response():
    """On a rust-backed client the coordinator runs the create through the backend,
    returns the created database, records the response headers on the connection, and
    fires ``response_hook`` once with the headers and the created database."""
    connection = SimpleNamespace(last_response_headers={})
    backend = _RustBackend()
    hooks = []

    result = DatabaseHelper(connection, backend).create_database(
        {"id": "db1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["id"] == "db1"
    assert backend.prepared.op == OP_CREATE_DATABASE
    assert backend.prepared.headers["offerThroughput"] == 400
    assert connection.last_response_headers["x-ms-request-charge"] == "5.25"
    assert hooks[0][1] == {"id": "db1", "_rid": "rid1"}


def test_sync_helper_keeps_legacy_create_database_behind_boundary():
    """With no rust backend (the core-python client) the coordinator runs the legacy
    ``CreateDatabase`` call directly, passing the database, options, and any extra
    kwargs straight through -- the legacy engine stays behind the same boundary."""
    connection = SimpleNamespace(
        CreateDatabase=MagicMock(return_value={"id": "db1"}),
        last_response_headers={},
    )
    result = DatabaseHelper(connection, None).create_database(
        {"id": "db1"},
        {"offerThroughput": 400},
        kwargs={"custom": "value"},
    )

    assert result == {"id": "db1"}
    connection.CreateDatabase.assert_called_once_with(
        database={"id": "db1"},
        options={"offerThroughput": 400},
        custom="value",
    )


def test_sync_helper_uses_legacy_when_read_timeout_is_requested():
    """When the caller sets a per-call ``read_timeout``, the create skips the rust
    path (which can't honor that timeout yet) and runs the legacy call instead, which
    does honor it -- so the customer's ``read_timeout`` is never silently dropped. The
    rust backend is never touched (its recorded request stays ``None``)."""
    connection = SimpleNamespace(
        CreateDatabase=MagicMock(return_value={"id": "db1"}),
        last_response_headers={},
    )
    backend = _RustBackend()

    result = DatabaseHelper(connection, backend).create_database(
        {"id": "db1"},
        {Constants.Kwargs.READ_TIMEOUT: 2},
        kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
    )

    assert result == {"id": "db1"}
    assert backend.prepared is None
    connection.CreateDatabase.assert_called_once()


def test_sync_helper_maps_conflict_to_resource_exists():
    """A 409 from the backend (the database id is already taken) surfaces as
    ``CosmosResourceExistsError`` -- the same typed error a customer catches to handle
    "this database already exists"."""
    backend = _RustBackend(
        BackendResponse(
            status_code=409,
            headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
            body=b'{"message":"database exists"}',
        )
    )
    with pytest.raises(CosmosResourceExistsError):
        DatabaseHelper(SimpleNamespace(last_response_headers={}), backend).create_database(
            {"id": "db1"},
            {},
        )


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in rust backend: records the request and returns the canned reply."""
    name = "rust"

    def __init__(self):
        self.prepared = None

    async def execute(self, prepared):
        self.prepared = prepared
        return _created_response()


def test_async_helper_routes_to_rust():
    """Async twin of the rust-route test: the create runs through the async backend
    and returns the created database. The async ``response_hook`` receives the
    response headers only (not the database body), matching the async contract."""
    async def run():
        connection = SimpleNamespace(last_response_headers={})
        backend = _AsyncRustBackend()
        hook_calls = []
        result = await AsyncDatabaseHelper(connection, backend).create_database(
            {"id": "db1"},
            {"throughputBucket": 9},
            response_hook=hook_calls.append,
        )
        assert result["id"] == "db1"
        assert backend.prepared.headers["throughputBucket"] == 9
        assert hook_calls[0]["x-ms-request-charge"] == "5.25"

    asyncio.run(run())


def test_async_helper_keeps_legacy_create_database_behind_boundary():
    """Async twin: with no rust backend, the async coordinator awaits the legacy
    ``CreateDatabase`` call directly, passing database/options/extra kwargs through."""
    async def run():
        connection = SimpleNamespace(
            CreateDatabase=AsyncMock(return_value={"id": "db1"}),
            last_response_headers={},
        )
        result = await AsyncDatabaseHelper(connection, None).create_database(
            {"id": "db1"},
            {},
            kwargs={"custom": "value"},
        )
        assert result == {"id": "db1"}
        connection.CreateDatabase.assert_awaited_once_with(
            database={"id": "db1"},
            options={},
            custom="value",
        )

    asyncio.run(run())


def test_async_helper_uses_legacy_when_read_timeout_is_requested():
    """Async twin of the read_timeout test: a per-call ``read_timeout`` forces the
    legacy call (which honors it), the rust backend is never touched, and the
    ``response_hook`` still fires with the response headers."""
    async def run():
        connection = SimpleNamespace(
            CreateDatabase=AsyncMock(return_value={"id": "db1"}),
            last_response_headers={"x-ms-request-charge": "4.25"},
        )
        backend = _AsyncRustBackend()
        hook_calls = []

        result = await AsyncDatabaseHelper(connection, backend).create_database(
            {"id": "db1"},
            {Constants.Kwargs.READ_TIMEOUT: 2},
            response_hook=hook_calls.append,
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

        assert result == {"id": "db1"}
        assert backend.prepared is None
        assert hook_calls[0]["x-ms-request-charge"] == "4.25"
        connection.CreateDatabase.assert_awaited_once()

    asyncio.run(run())


def test_sync_public_create_database_returns_proxy_and_properties():
    """End-to-end through the public sync method: with ``return_properties=True`` the
    customer gets back both the ``DatabaseProxy`` handle and the created database's
    properties (its server-assigned rid, etc.), and ``response_hook`` receives the
    headers and the created database."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(last_response_headers={})
    client._backend = _RustBackend()
    hook_calls = []

    proxy, properties = client.create_database(
        "db1",
        offer_throughput=400,
        return_properties=True,
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
    )

    assert proxy.id == "db1"
    assert properties["_rid"] == "rid1"
    assert hook_calls[0][1]["id"] == "db1"


def test_sync_public_create_database_preserves_zero_autoscale_increment():
    """A customer creating an autoscale database with an increment percent of ``0``
    keeps that ``0`` in the throughput settings sent -- it is a real, intentional
    value, not treated as "unset" and dropped."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(last_response_headers={})
    backend = _RustBackend()
    client._backend = backend

    client.create_database(
        "db1",
        offer_throughput=ThroughputProperties(
            auto_scale_max_throughput=4000,
            auto_scale_increment_percent=0,
        ),
    )

    policy = json.loads(backend.prepared.headers["autoUpgradePolicy"])
    assert policy["maxThroughput"] == 4000
    assert policy["autoUpgradePolicy"]["throughputPolicy"]["incrementPercent"] == 0


def test_async_public_create_database_returns_proxy_and_properties():
    """Async twin of the public-method test: ``return_properties=True`` returns the
    proxy and the created database's properties; the async ``response_hook`` receives
    the headers only."""
    async def run():
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = SimpleNamespace(last_response_headers={})
        client._backend = _AsyncRustBackend()
        hook_calls = []

        proxy, properties = await client.create_database(
            "db1",
            throughput_bucket=9,
            return_properties=True,
            response_hook=lambda headers: hook_calls.append(headers),
        )

        assert proxy.id == "db1"
        assert properties["_rid"] == "rid1"
        assert hook_calls[0]["x-ms-request-charge"] == "5.25"

    asyncio.run(run())


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_public_create_database_does_not_select_backend(client_type):
    """The public ``create_database`` (sync and async) must not name an engine: its
    source mentions no rust backend, no eligibility check, and no direct legacy call.
    That keeps engine selection entirely behind the coordinator, so the public method
    stays a thin delegate."""
    source = inspect.getsource(client_type.create_database)
    assert "RustBackend" not in source
    assert "can_use_rust" not in source
    assert "CreateDatabase(" not in source
