"""Unit coverage for account-level database backend routing (no network).

These lock in how ``create_database`` and ``create_database_if_not_exists`` run
on the migrated path: public methods stay thin backend-neutral delegates, the
database coordinator owns fallback and request preparation, and final database
properties have the same shape on either engine. All fakes, no Cosmos account.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse, CosmosBackend
from azure.cosmos._backend.base import (
    OP_CREATE_DATABASE,
    OP_CREATE_DATABASE_IF_NOT_EXISTS,
    OP_TO_BINDING_METHOD,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_prep import (
    build_create_database_if_not_exists_prepared,
    build_create_database_prepared,
)
from azure.cosmos._helpers.database_helper import DatabaseHelper
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._cosmos_client import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._helpers.database_helper import AsyncDatabaseHelper
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
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


def test_create_database_if_not_exists_is_registered_and_carries_database_id():
    """The retry-safe create is wired to the binding's own
    ``create_database_if_not_exists`` entry point, and the prepared request carries
    the database id the existence read needs to look the database up."""
    assert (
        OP_TO_BINDING_METHOD[OP_CREATE_DATABASE_IF_NOT_EXISTS]
        == "create_database_if_not_exists"
    )
    prepared = build_create_database_if_not_exists_prepared(
        {"id": "db1"},
        {"offerThroughput": 400},
    )
    assert prepared.op == OP_CREATE_DATABASE_IF_NOT_EXISTS
    assert prepared.item_id == "db1"


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
        last_response_headers={"x-ms-request-charge": "4.0"},
    )
    hook_calls = []
    result = DatabaseHelper(connection, None).create_database(
        {"id": "db1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
        kwargs={"custom": "value", "response_hook": MagicMock()},
    )

    assert result == {"id": "db1"}
    connection.CreateDatabase.assert_called_once_with(
        database={"id": "db1"},
        options={"offerThroughput": 400},
        custom="value",
    )
    assert hook_calls == [
        ({"x-ms-request-charge": "4.0"}, {"id": "db1"})
    ]


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
    hook_calls = []
    with pytest.raises(CosmosResourceExistsError):
        DatabaseHelper(SimpleNamespace(last_response_headers={}), backend).create_database(
            {"id": "db1"},
            {},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )
    assert hook_calls == []


def test_sync_if_not_exists_routes_combined_operation_to_rust():
    """On the rust engine the whole read-then-create runs as one backend operation
    tagged ``create_database_if_not_exists``; on success ``response_hook`` fires once
    with the response headers and the resulting database."""
    connection = SimpleNamespace(last_response_headers={})
    backend = _RustBackend()
    hooks = []

    result = DatabaseHelper(connection, backend).create_database_if_not_exists(
        {"id": "db1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["_rid"] == "rid1"
    assert backend.prepared.op == OP_CREATE_DATABASE_IF_NOT_EXISTS
    assert backend.prepared.item_id == "db1"
    assert hooks == [
        (
            {"x-ms-request-charge": "5.25"},
            {"id": "db1", "_rid": "rid1"},
        )
    ]


def test_sync_if_not_exists_legacy_returns_existing_without_create_headers():
    """When the database already exists, the legacy path returns it straight from the
    existence read and never calls CreateDatabase. Provisioning-only options
    (``offerThroughput``, ``autoUpgradePolicy``) are stripped from the read so it can't
    try to set throughput, while ordinary options like ``throughputBucket`` still ride
    along."""
    hook_calls = []
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "existing"}),
        CreateDatabase=MagicMock(),
        last_response_headers={"x-ms-request-charge": "1.0"},
    )

    result = DatabaseHelper(connection, None).create_database_if_not_exists(
        {"id": "db1"},
        {
            "offerThroughput": 400,
            "autoUpgradePolicy": '{"maxThroughput":4000}',
            "throughputBucket": 7,
        },
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
    )

    assert result["_rid"] == "existing"
    read_options = connection.ReadDatabase.call_args.kwargs["options"]
    assert "offerThroughput" not in read_options
    assert "autoUpgradePolicy" not in read_options
    assert read_options["throughputBucket"] == 7
    connection.CreateDatabase.assert_not_called()
    assert "response_hook" not in connection.ReadDatabase.call_args.kwargs
    assert hook_calls == [
        ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "existing"})
    ]


def test_sync_if_not_exists_legacy_creates_only_after_404_and_propagates_409():
    """The legacy path creates only after the existence read returns 404 (not found).
    If two callers race and the create loses with a 409 ("already exists"), that 409 is
    handed to the customer rather than hidden behind a second read."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(
            side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
        ),
        CreateDatabase=MagicMock(
            side_effect=CosmosResourceExistsError(status_code=409, message="race")
        ),
        last_response_headers={},
    )

    with pytest.raises(CosmosResourceExistsError):
        DatabaseHelper(connection, None).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
        )

    connection.ReadDatabase.assert_called_once()
    connection.CreateDatabase.assert_called_once_with(
        database={"id": "db1"},
        options={"offerThroughput": 400},
    )


def test_sync_if_not_exists_read_timeout_forces_whole_operation_to_legacy():
    """A per-call ``read_timeout`` the rust path can't honor yet sends the whole
    read-then-create to the legacy path (which does honor it), so both legs share one
    engine and the timeout is never split or dropped -- the rust backend is never
    prepared here."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1"}),
        CreateDatabase=MagicMock(),
        last_response_headers={},
    )
    backend = _RustBackend()

    result = DatabaseHelper(connection, backend).create_database_if_not_exists(
        {"id": "db1"},
        {Constants.Kwargs.READ_TIMEOUT: 2},
        kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
    )

    assert result["id"] == "db1"
    assert backend.prepared is None
    connection.ReadDatabase.assert_called_once()


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in rust backend: records the request and returns the canned reply."""
    name = "rust"

    def __init__(self, response=None):
        self.prepared = None
        self.response = response or _created_response()

    async def execute(self, prepared):
        self.prepared = prepared
        return self.response


def test_async_helper_routes_to_rust():
    """Async twin of the rust-route test: the create runs through the async backend
    and returns the created database. The async ``response_hook`` fires once with
    the response headers and database body, matching legacy async behavior."""
    async def run():
        connection = SimpleNamespace(last_response_headers={})
        backend = _AsyncRustBackend()
        hook_calls = []
        result = await AsyncDatabaseHelper(connection, backend).create_database(
            {"id": "db1"},
            {"throughputBucket": 9},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )
        assert result["id"] == "db1"
        assert backend.prepared.headers["throughputBucket"] == 9
        assert hook_calls == [
            (
                {"x-ms-request-charge": "5.25"},
                {"id": "db1", "_rid": "rid1"},
            )
        ]

    asyncio.run(run())


def test_async_helper_does_not_call_response_hook_on_failure():
    async def run():
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=409,
                headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
                body=b'{"message":"database exists"}',
            )
        )
        hook_calls = []

        with pytest.raises(CosmosResourceExistsError):
            await AsyncDatabaseHelper(
                SimpleNamespace(last_response_headers={}),
                backend,
            ).create_database(
                {"id": "db1"},
                {},
                response_hook=lambda headers, body: hook_calls.append(
                    (headers, body)
                ),
            )

        assert hook_calls == []

    asyncio.run(run())


def test_async_helper_keeps_legacy_create_database_behind_boundary():
    """Async twin: with no rust backend, the async coordinator awaits the legacy
    ``CreateDatabase`` call directly, passing database/options/extra kwargs through."""
    async def run():
        connection = SimpleNamespace(
            CreateDatabase=AsyncMock(return_value={"id": "db1"}),
            last_response_headers={"x-ms-request-charge": "4.0"},
        )
        hook_calls = []
        result = await AsyncDatabaseHelper(connection, None).create_database(
            {"id": "db1"},
            {},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={"custom": "value", "response_hook": MagicMock()},
        )
        assert result == {"id": "db1"}
        connection.CreateDatabase.assert_awaited_once_with(
            database={"id": "db1"},
            options={},
            custom="value",
        )
        assert hook_calls == [
            ({"x-ms-request-charge": "4.0"}, {"id": "db1"})
        ]

    asyncio.run(run())


def test_async_helper_uses_legacy_when_read_timeout_is_requested():
    """Async twin of the read_timeout test: a per-call ``read_timeout`` forces the
    legacy call (which honors it), the rust backend is never touched, and the
    ``response_hook`` still fires with the response headers and database body."""
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
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

        assert result == {"id": "db1"}
        assert backend.prepared is None
        assert hook_calls == [
            ({"x-ms-request-charge": "4.25"}, {"id": "db1"})
        ]
        connection.CreateDatabase.assert_awaited_once()

    asyncio.run(run())


def test_async_if_not_exists_legacy_reads_then_creates_only_on_404():
    """Async legacy path: the existence read returns 404, so it goes on to create, and
    ``response_hook`` fires once with the created database. The read leg drops the
    internal ``response_hook`` kwarg so the hook can't be invoked twice."""
    async def run():
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(
                side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
            ),
            CreateDatabase=AsyncMock(return_value={"id": "db1", "_rid": "created"}),
            last_response_headers={"x-ms-request-charge": "5.0"},
        )
        hook_calls = []

        result = await AsyncDatabaseHelper(connection, None).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={"response_hook": MagicMock()},
        )

        assert result["_rid"] == "created"
        connection.ReadDatabase.assert_awaited_once()
        connection.CreateDatabase.assert_awaited_once_with(
            database={"id": "db1"},
            options={"offerThroughput": 400},
        )
        assert "response_hook" not in connection.ReadDatabase.call_args.kwargs
        assert hook_calls == [
            (
                {"x-ms-request-charge": "5.0"},
                {"id": "db1", "_rid": "created"},
            )
        ]

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
    the headers and created database."""
    async def run():
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = SimpleNamespace(last_response_headers={})
        client._backend = _AsyncRustBackend()
        hook_calls = []

        proxy, properties = await client.create_database(
            "db1",
            throughput_bucket=9,
            return_properties=True,
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )

        assert proxy.id == "db1"
        assert properties["_rid"] == "rid1"
        assert hook_calls == [
            (
                {"x-ms-request-charge": "5.25"},
                {"id": "db1", "_rid": "rid1"},
            )
        ]

    asyncio.run(run())


def test_public_create_database_if_not_exists_returns_final_properties_sync_and_async():
    """End-to-end through the public method (sync and async): with
    ``return_properties=True`` the customer gets back the ``DatabaseProxy`` handle plus
    the final database properties, and the request is tagged
    ``create_database_if_not_exists``."""
    sync_client = object.__new__(CosmosClient)
    sync_client.client_connection = SimpleNamespace(last_response_headers={})
    sync_backend = _RustBackend()
    sync_client._backend = sync_backend

    proxy, properties = sync_client.create_database_if_not_exists(
        "db1",
        return_properties=True,
    )
    assert proxy.id == "db1"
    assert properties["_rid"] == "rid1"
    assert sync_backend.prepared.op == OP_CREATE_DATABASE_IF_NOT_EXISTS

    async def run():
        async_client = object.__new__(AsyncCosmosClient)
        async_client.client_connection = SimpleNamespace(last_response_headers={})
        async_backend = _AsyncRustBackend()
        async_client._backend = async_backend
        async_proxy, async_properties = await async_client.create_database_if_not_exists(
            "db1",
            return_properties=True,
        )
        assert async_proxy.id == "db1"
        assert async_properties["_rid"] == "rid1"
        assert async_backend.prepared.op == OP_CREATE_DATABASE_IF_NOT_EXISTS

    asyncio.run(run())


@pytest.mark.parametrize(
    "method_name",
    ["create_database", "create_database_if_not_exists"],
)
def test_sync_database_operations_really_ignore_inapplicable_conditions(method_name):
    """``session_token``, ``etag``, and ``match_condition`` don't apply to creating a
    database, so both create methods warn once for each and never place those
    conditions on the wire -- a customer who passes them gets a heads-up, not a
    silently conditional create."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(last_response_headers={})
    backend = _RustBackend()
    client._backend = backend

    with pytest.warns(UserWarning) as warnings_seen:
        getattr(client, method_name)(
            "db1",
            session_token="session",
            etag="etag",
            match_condition=MatchConditions.IfPresent,
        )

    assert len(warnings_seen) == 3
    assert "sessionToken" not in backend.prepared.headers
    assert "accessCondition" not in backend.prepared.headers


@pytest.mark.parametrize(
    "method_name",
    ["create_database", "create_database_if_not_exists"],
)
def test_async_database_operations_really_ignore_inapplicable_conditions(method_name):
    """Async twin of
    ``test_sync_database_operations_really_ignore_inapplicable_conditions``."""
    async def run():
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = SimpleNamespace(last_response_headers={})
        backend = _AsyncRustBackend()
        client._backend = backend

        with pytest.warns(DeprecationWarning) as warnings_seen:
            await getattr(client, method_name)(
                "db1",
                session_token="session",
                etag="etag",
                match_condition=MatchConditions.IfPresent,
            )

        assert len(warnings_seen) == 3
        assert "sessionToken" not in backend.prepared.headers
        assert "accessCondition" not in backend.prepared.headers

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


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_public_create_database_if_not_exists_does_not_orchestrate_backends(client_type):
    """The public ``create_database_if_not_exists`` (sync and async) must stay a thin
    delegate: its source names no rust backend and makes no direct ReadDatabase or
    CreateDatabase call, so the read-then-create and the engine choice live entirely in
    the coordinator."""
    source = inspect.getsource(client_type.create_database_if_not_exists)
    assert "RustBackend" not in source
    assert "ReadDatabase(" not in source
    assert "CreateDatabase(" not in source


# ---------------------------------------------------------------------------
# Async create_database_if_not_exists coverage
# ---------------------------------------------------------------------------


def test_async_if_not_exists_routes_to_rust_and_hook_fires_once():
    """Async twin of ``test_sync_if_not_exists_routes_combined_operation_to_rust``:
    the combined operation dispatches to the Rust backend and the async
    ``response_hook`` fires exactly once with the response headers and result."""
    async def run():
        connection = SimpleNamespace(last_response_headers={"x-ms-request-charge": "5.25"})
        backend = _AsyncRustBackend()
        hook_calls = []

        result = await AsyncDatabaseHelper(connection, backend).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )

        assert result["_rid"] == "rid1"
        assert backend.prepared.op == OP_CREATE_DATABASE_IF_NOT_EXISTS
        assert backend.prepared.item_id == "db1"
        assert hook_calls == [
            (
                {"x-ms-request-charge": "5.25"},
                {"id": "db1", "_rid": "rid1"},
            )
        ]

    asyncio.run(run())


def test_async_if_not_exists_legacy_existing_skips_create_and_strips_create_only_options():
    """Async twin of ``test_sync_if_not_exists_legacy_returns_existing_without_create_headers``:
    the legacy path returns the existing database without calling CreateDatabase, and
    strips provisioning-only options (offerThroughput, autoUpgradePolicy) from the
    ReadDatabase call while keeping others (e.g. throughputBucket)."""
    async def run():
        hook_calls = []
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "existing"}),
            CreateDatabase=AsyncMock(),
            last_response_headers={"x-ms-request-charge": "1.0"},
        )

        result = await AsyncDatabaseHelper(connection, None).create_database_if_not_exists(
            {"id": "db1"},
            {
                "offerThroughput": 400,
                "autoUpgradePolicy": '{"maxThroughput":4000}',
                "throughputBucket": 7,
            },
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={"response_hook": MagicMock()},
        )

        assert result["_rid"] == "existing"
        read_options = connection.ReadDatabase.call_args.kwargs["options"]
        assert "offerThroughput" not in read_options
        assert "autoUpgradePolicy" not in read_options
        assert read_options["throughputBucket"] == 7
        connection.CreateDatabase.assert_not_awaited()
        assert "response_hook" not in connection.ReadDatabase.call_args.kwargs
        assert hook_calls == [
            (
                {"x-ms-request-charge": "1.0"},
                {"id": "db1", "_rid": "existing"},
            )
        ]

    asyncio.run(run())


def test_async_if_not_exists_read_timeout_forces_whole_operation_to_legacy():
    """Async twin of ``test_sync_if_not_exists_read_timeout_forces_whole_operation_to_legacy``:
    a per-call ``read_timeout`` bypasses the Rust backend entirely and runs the
    legacy read-then-conditional-create path, which honors the socket timeout."""
    async def run():
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1"}),
            CreateDatabase=AsyncMock(),
            last_response_headers={},
        )
        backend = _AsyncRustBackend()

        result = await AsyncDatabaseHelper(connection, backend).create_database_if_not_exists(
            {"id": "db1"},
            {Constants.Kwargs.READ_TIMEOUT: 2},
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

        assert result["id"] == "db1"
        assert backend.prepared is None
        connection.ReadDatabase.assert_awaited_once()

    asyncio.run(run())


def test_sync_if_not_exists_non_404_read_error_propagates_without_create():
    """A read error other than 404 (e.g. 403 Forbidden) propagates immediately
    without ever attempting the create.  The race-contract (404 -> 409 propagates)
    is a separate concern; this locks in that only 404 triggers create."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(
            side_effect=CosmosResourceExistsError(status_code=409, message="conflict")
        ),
        CreateDatabase=MagicMock(),
        last_response_headers={},
    )

    with pytest.raises(CosmosResourceExistsError):
        DatabaseHelper(connection, None).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
        )

    connection.CreateDatabase.assert_not_called()


def test_async_if_not_exists_non_404_read_error_propagates_without_create():
    """Async twin of the non-404 read-error propagation test."""
    async def run():
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(
                side_effect=CosmosResourceExistsError(status_code=409, message="conflict")
            ),
            CreateDatabase=AsyncMock(),
            last_response_headers={},
        )

        with pytest.raises(CosmosResourceExistsError):
            await AsyncDatabaseHelper(connection, None).create_database_if_not_exists(
                {"id": "db1"},
                {"offerThroughput": 400},
            )

        connection.CreateDatabase.assert_not_awaited()

    asyncio.run(run())
