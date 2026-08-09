# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for account-level database backend routing (no network).

Three public methods land here. ``create_database`` sends one request.
``DatabaseProxy.read`` sends one request -- a customer asking for a database's
properties. ``create_database_if_not_exists`` sends one or two: read the
database, and create it only if the read comes back not-found. The Rust driver
has a read call and a create call but no combined one, so Python decides between
them.

That split is what these tests protect. The public methods must stay thin and
must not pick an engine themselves; the database coordinator owns the branch,
the request building, and the decision about when the legacy core-python path is
allowed to take over. Get that wrong and a customer sees the same method behave
differently depending on which engine they selected -- different retries,
different diagnostics, or a per-call timeout silently dropped.

The tests also check that the database properties handed back are identical on
both paths, since customers read those directly.

What the read-specific tests cover, and the customer behavior behind each:

* the request the rust engine is handed -- database name, no body, the headers
  built from the caller's options, and the per-call ``timeout``. If any of that
  is wrong the call reads the wrong database or drops an option.
* routing away from rust when rust cannot honor an option exactly -- a
  sub-second ``timeout``, a socket-level ``read_timeout``, or a transport
  keyword. A customer who sets ``timeout=0.5`` must get 0.5 seconds, not a
  silently rounded-up value.
* ``response_hook`` firing exactly once, with the response headers and the
  properties, on **both** engines. Customers use it for cost and audit logging,
  so firing twice double-counts and firing zero times loses the record.
* a missing database raising the typed not-found error, with the hook not
  firing. Customers catch that type to decide whether to create the database.
* the same eligibility answer being used by ``DatabaseProxy.read`` and by the
  existence check inside ``create_database_if_not_exists``, so one call cannot
  run on different engines in the two methods.
* ``initial_headers`` layering over the client's default headers, with the
  caller winning a name collision -- that is the point of passing them.

Every read test is written twice, once sync and once async. That is not
duplication for its own sake: the async path builds its request through a
different wrapper, so it is separate code that can break on its own.

All fakes, no Cosmos account.
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

from azure.cosmos import _base as base
from azure.cosmos._backend.base import BackendResponse, CosmosBackend
from azure.cosmos._backend.base import (
    OP_CREATE_DATABASE,
    OP_DELETE_DATABASE,
    OP_READ_DATABASE,
    OP_TO_BINDING_METHOD,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_client_connection import (
    CosmosClientConnection as SyncClientConnection,
)
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_prep import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    is_read_database_rust_eligible,
)
from azure.cosmos._helpers.database_helper import DatabaseHelper
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncClientConnection,
)
from azure.cosmos.aio._cosmos_client import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.aio._helpers.database_helper import AsyncDatabaseHelper
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
from azure.cosmos.offer import ThroughputProperties


def _created_response() -> BackendResponse:
    """Return a successful fake database-create response."""
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


def test_create_database_if_not_exists_is_not_registered_in_the_binding():
    """The compound coordinator is not a wire op; its read primitive is."""
    assert "create_database_if_not_exists" not in OP_TO_BINDING_METHOD
    assert OP_TO_BINDING_METHOD[OP_READ_DATABASE] == "read_database"


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


def test_read_database_prepared_request_is_bodiless():
    """The existence read sends no body, only the database id.

    Create sends the database document; read identifies the database by id alone.
    Both build through the same helper, so this checks the read leg did not pick
    up the create's body while still carrying the caller's options and timeout.
    """
    prepared = build_read_database_prepared(
        "db1",
        {"throughputBucket": 7},
        kwargs={"timeout": 3.5},
    )

    assert prepared.op == OP_READ_DATABASE
    assert prepared.body_bytes == b""
    assert prepared.item_id == "db1"
    assert prepared.headers["throughputBucket"] == 7
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5


def test_read_database_prepared_preserves_legacy_option_headers():
    """Every truthy option that legacy GetHeaders emits reaches the binding."""
    initial_headers = {"x-custom": "value"}
    options = {
        "initialHeaders": initial_headers,
        "maxItemCount": 10,
        "enableScanInQuery": True,
        "resourceTokenExpirySeconds": 60,
        "offerType": "S1",
        "contentType": "application/custom+json",
        "isQueryPlanRequest": True,
        "supportedQueryFeatures": "Aggregate",
        "queryVersion": "1.0",
        "enableCrossPartitionQuery": True,
        "populateQueryMetrics": True,
        "populateIndexMetrics": True,
        "populateQueryAdvice": True,
        "responseContinuationTokenLimitInKb": 4,
        "enableScriptLogging": True,
        "offerEnableRUPerMinuteThroughput": True,
        "disableRUPerMinuteUsage": True,
        "continuation": "token",
        "populatePartitionKeyRangeStatistics": True,
        "populateQuotaInfo": True,
        "correlatedActivityId": "correlated-id",
        "sessionToken": "master-resource-token-is-ignored",
    }

    prepared = build_read_database_prepared("db1", options)

    assert prepared.headers["initialHeaders"] == initial_headers
    assert prepared.headers["initialHeaders"] is not initial_headers
    for option_key, option_value in options.items():
        if option_key not in ("initialHeaders", "sessionToken"):
            assert prepared.headers[option_key] == option_value
    assert "sessionToken" not in prepared.headers


@pytest.mark.parametrize(
    "option_key",
    [
        "continuation",
        "contentType",
        "enableScanInQuery",
        "maxItemCount",
        "populateQueryMetrics",
        "resourceTokenExpirySeconds",
        "sessionToken",
        "throughputBucket",
    ],
)
def test_read_database_prepared_omits_falsy_legacy_headers(option_key):
    """Prove empty Python-only options do not become request headers."""
    prepared = build_read_database_prepared("db1", {option_key: None})

    assert option_key not in prepared.headers


def test_read_database_prepared_preserves_legacy_id_stringification():
    """Read keeps its own id rules: it stringifies and tolerates a trailing slash,
    where create validates."""
    assert build_read_database_prepared(123, {}).item_id == "123"
    assert build_read_database_prepared("db1/", {}).item_id == "db1"


@pytest.mark.parametrize("database_id", ["", "/", "///"])
def test_read_database_prepared_rejects_empty_normalized_id(database_id):
    """Prove an empty database ID fails before a request is sent."""
    with pytest.raises(ValueError, match="Failed Parsing ResourceID from link: /dbs/"):
        build_read_database_prepared(database_id, {})


@pytest.mark.parametrize(
    "request_options,operation_kwargs,expected",
    [
        ({}, {}, True),
        ({}, {"timeout": 1.0}, True),
        ({}, {"timeout": 0.5}, False),
        ({}, {"timeout": 0}, False),
        ({}, {"timeout": -1}, False),
        ({}, {"timeout": float("-inf")}, False),
        ({}, {"timeout": "1"}, False),
        ({}, {"timeout": float("nan")}, True),
        ({}, {"timeout": float("inf")}, True),
        ({"read_timeout": 2}, {"read_timeout": 2}, False),
        ({}, {"connection_timeout": 2}, False),
        ({}, {"raw_request_hook": object()}, False),
        ({}, {"response_hook": object()}, True),
        ({"initialHeaders": {"x-custom": "value"}}, {}, True),
        ({"initialHeaders": {"Accept": "application/custom"}}, {}, False),
        ({"initialHeaders": {"CACHE-CONTROL": "max-age=60"}}, {}, False),
        ({"initialHeaders": {"User-Agent": "custom"}}, {}, False),
        ({"initialHeaders": {"X-MS-VERSION": "2018-12-31"}}, {}, False),
    ],
)
def test_read_database_rust_eligibility_never_drops_transport_kwargs(
    request_options, operation_kwargs, expected
):
    """Prove transport options keep a read on Python when Rust cannot honor them."""
    assert (
        is_read_database_rust_eligible(request_options, operation_kwargs)
        is expected
    )


def test_sync_connection_read_database_forwards_initial_headers():
    """Prove sync database reads preserve caller-supplied initial headers."""
    connection = SimpleNamespace(
        Read=MagicMock(return_value={"id": "db1"}),
        default_headers={
            "x-ms-version": "2020-07-15",
            "Cache-Control": "no-cache",
        },
    )
    options = {"initialHeaders": {"x-custom": "value"}}

    result = SyncClientConnection.ReadDatabase(
        connection,
        "dbs/db1",
        options=options,
    )

    assert result == {"id": "db1"}
    connection.Read.assert_called_once_with(
        "/dbs/db1/",
        "dbs",
        "dbs/db1",
        {
            "x-ms-version": "2020-07-15",
            "Cache-Control": "no-cache",
            "x-custom": "value",
        },
        options,
    )


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

    def __init__(self, response=None, responses=None):
        """Store the canned reply (or queue of replies) the stub will return on each ``execute`` call."""
        self.responses = list(responses or [response or _created_response()])
        self.prepared = None
        self.prepared_requests = []

    def execute(self, prepared):
        """Record the prepared request and return the next canned reply from the queue."""
        self.prepared = prepared
        self.prepared_requests.append(prepared)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


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


def test_sync_read_database_routes_to_rust_and_parses_response():
    """A proxy database read uses the Rust read primitive and never calls legacy."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _RustBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
            body=b'{"id":"db1","_rid":"existing"}',
        )
    )
    hook_calls = []

    result = DatabaseHelper(connection, backend).read_database(
        "db1",
        {"throughputBucket": 7},
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
        kwargs={"timeout": 3.5},
    )

    assert result == {"id": "db1", "_rid": "existing"}
    assert backend.prepared.op == OP_READ_DATABASE
    assert backend.prepared.item_id == "db1"
    assert backend.prepared.headers["throughputBucket"] == 7
    assert backend.prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5
    connection.ReadDatabase.assert_not_called()
    assert hook_calls == [
        ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "existing"})
    ]
    assert isinstance(result, CosmosDict)
    assert type(hook_calls[0][1]) is dict


def test_sync_read_database_keeps_legacy_path_and_read_timeout():
    """Core Python and per-call socket timeouts retain the legacy read behavior."""
    response_headers = {"x-ms-request-charge": "1.0"}
    legacy_body = {"id": "db1", "_rid": "legacy"}
    hook_calls = []

    def response_hook(headers, body):
        """Append the headers and body to hook_calls so the test can assert on them."""
        hook_calls.append((headers, body))

    def legacy_read(_link, *, options, **kwargs):
        """Invoke the caller's response_hook and return the canned legacy body."""
        kwargs["response_hook"](response_headers, legacy_body)
        return legacy_body

    connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=legacy_read),
        last_response_headers=response_headers,
    )
    backend = _RustBackend()

    result = DatabaseHelper(connection, backend).read_database(
        "db1",
        {Constants.Kwargs.READ_TIMEOUT: 2},
        response_hook=response_hook,
        kwargs={Constants.Kwargs.READ_TIMEOUT: 2, "response_hook": MagicMock()},
    )

    assert result == {"id": "db1", "_rid": "legacy"}
    assert backend.prepared is None
    connection.ReadDatabase.assert_called_once_with(
        "dbs/db1",
        options={Constants.Kwargs.READ_TIMEOUT: 2},
        **{
            Constants.Kwargs.READ_TIMEOUT: 2,
            "response_hook": response_hook,
        },
    )
    assert hook_calls == [
        ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "legacy"})
    ]


def test_sync_read_database_maps_not_found_and_skips_hook():
    """A Rust 404 preserves the typed not-found exception contract."""
    backend = _RustBackend(
        BackendResponse(
            status_code=404,
            headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
            body=b'{"message":"missing"}',
        )
    )
    hook_calls = []

    with pytest.raises(CosmosResourceNotFoundError):
        DatabaseHelper(SimpleNamespace(last_response_headers={}), backend).read_database(
            "missing",
            {},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )

    assert not hook_calls


def test_sync_database_proxy_read_selects_rust_backend():
    """The public sync proxy delegates its read through the stored backend."""
    backend = _RustBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
            body=b'{"id":"db1","_rid":"existing"}',
        )
    )
    connection = SimpleNamespace(
        _backend=backend,
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )

    result = DatabaseProxy(connection, "db1").read(throughput_bucket=7)

    assert result == {"id": "db1", "_rid": "existing"}
    assert backend.prepared.op == OP_READ_DATABASE
    assert backend.prepared.headers["throughputBucket"] == 7
    connection.ReadDatabase.assert_not_called()


def test_sync_database_proxy_read_drops_deprecated_session_token():
    """The ignored session token must not reach the Rust wire request."""
    backend = _RustBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({}),
            body=b'{"id":"db1"}',
        )
    )
    connection = SimpleNamespace(_backend=backend, last_response_headers={})

    with pytest.warns(DeprecationWarning, match="session_token"):
        DatabaseProxy(connection, "db1").read(session_token="ignored")

    assert "sessionToken" not in backend.prepared.headers


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


def test_sync_if_not_exists_reads_through_rust_without_legacy_calls():
    """The database already exists, so the read is the only request sent.

    Python decides whether to create; the Rust path performs the read. The legacy
    calls are wired to fail the test if touched, because a customer who selected
    the Rust backend should not have half of this method run on the other engine.
    """
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        CreateDatabase=MagicMock(),
        last_response_headers={"x-ms-request-charge": "1.0"},
    )
    backend = _RustBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
            body=b'{"id":"db1","_rid":"existing"}',
        )
    )
    hooks = []

    result = DatabaseHelper(connection, backend).create_database_if_not_exists(
        {"id": "db1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["_rid"] == "existing"
    assert [request.op for request in backend.prepared_requests] == [OP_READ_DATABASE]
    connection.ReadDatabase.assert_not_called()
    connection.CreateDatabase.assert_not_called()
    assert hooks == [
        (
            {"x-ms-request-charge": "1.0"},
            {"id": "db1", "_rid": "existing"},
        )
    ]


def test_sync_if_not_exists_rust_404_then_rust_create_without_legacy_calls():
    """The database is missing, so both requests run on the Rust path.

    Also checks the two legs carry different options: ``offerThroughput`` sets the
    throughput of a database being created, so sending it on the existence read
    would be meaningless, while ``throughputBucket`` applies to both requests.
    """
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        CreateDatabase=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _RustBackend(
        responses=[
            BackendResponse(
                status_code=404,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                body=b'{"message":"missing"}',
            ),
            _created_response(),
        ]
    )
    hook_calls = []

    result = DatabaseHelper(connection, backend).create_database_if_not_exists(
        {"id": "db1"},
        {"offerThroughput": 400, "throughputBucket": 7},
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
    )

    assert result["_rid"] == "rid1"
    assert [request.op for request in backend.prepared_requests] == [
        OP_READ_DATABASE,
        OP_CREATE_DATABASE,
    ]
    assert "offerThroughput" not in backend.prepared_requests[0].headers
    assert backend.prepared_requests[0].headers["throughputBucket"] == 7
    assert backend.prepared_requests[1].headers["offerThroughput"] == 400
    assert hook_calls == [
        (
            {"x-ms-request-charge": "5.25"},
            {"id": "db1", "_rid": "rid1"},
        )
    ]
    connection.ReadDatabase.assert_not_called()
    connection.CreateDatabase.assert_not_called()


def test_sync_if_not_exists_rust_create_race_propagates_conflict():
    """Someone else created the database between the read and the create.

    The read said not-found and the create then came back 409 Conflict. There is
    a gap between the two requests that nothing can close, so the error is passed
    to the caller rather than swallowed -- their throughput settings were not
    applied, and pretending the call succeeded would hide that.
    """
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        CreateDatabase=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _RustBackend(
        responses=[
            BackendResponse(
                status_code=404,
                headers=CaseInsensitiveDict({}),
                body=b'{"message":"missing"}',
            ),
            BackendResponse(
                status_code=409,
                headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
                body=b'{"message":"database exists"}',
            ),
        ]
    )

    with pytest.raises(CosmosResourceExistsError):
        DatabaseHelper(connection, backend).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
        )

    assert [request.op for request in backend.prepared_requests] == [
        OP_READ_DATABASE,
        OP_CREATE_DATABASE,
    ]
    connection.ReadDatabase.assert_not_called()
    connection.CreateDatabase.assert_not_called()


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


def test_sync_if_not_exists_legacy_preserves_read_timeout_on_both_legs():
    """A per-call socket timeout applies to the read and to the create.

    The customer set one timeout for one method call. Applying it to only the
    first request would leave the second able to hang for the client default,
    which is not what they asked for.
    """
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(
            side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
        ),
        CreateDatabase=MagicMock(return_value={"id": "db1", "_rid": "created"}),
        last_response_headers={},
    )

    result = DatabaseHelper(connection, None).create_database_if_not_exists(
        {"id": "db1"},
        {},
        kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
    )

    assert result["_rid"] == "created"
    assert connection.ReadDatabase.call_args.kwargs[Constants.Kwargs.READ_TIMEOUT] == 2
    assert connection.CreateDatabase.call_args.kwargs[Constants.Kwargs.READ_TIMEOUT] == 2


@pytest.mark.parametrize(
    "request_options,operation_kwargs",
    [
        ({Constants.Kwargs.READ_TIMEOUT: 2}, {}),
        ({}, {Constants.Kwargs.READ_TIMEOUT: 2}),
        # Both legs share DatabaseProxy.read's eligibility rule, so every option
        # that sends a plain read to the legacy path stops a get-or-create here.
        # The driver clamps a sub-second end-to-end timeout to 1 second, and a
        # transport keyword is consumed by the azure-core pipeline the Rust path
        # never runs.
        ({}, {Constants.Kwargs.TIMEOUT: 0.5}),
        ({}, {"connection_timeout": 2}),
    ],
)
def test_sync_if_not_exists_read_timeout_never_crosses_from_rust_to_legacy(
    request_options,
    operation_kwargs,
):
    """An unsupported per-call socket timeout fails instead of mixing engines.

    A per-call socket timeout is not something the Rust path can express, and the
    method needs both of its requests on the same engine. Quietly running the whole
    thing on the legacy path would give the customer different retry behavior and
    different diagnostics than every other call on that client, with no way to
    notice. It raises instead, and sends nothing.
    """
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1"}),
        CreateDatabase=MagicMock(),
        last_response_headers={},
    )
    backend = _RustBackend()

    with pytest.raises(NotImplementedError, match="create_database_if_not_exists"):
        DatabaseHelper(connection, backend).create_database_if_not_exists(
            {"id": "db1"},
            request_options,
            kwargs=operation_kwargs,
        )

    assert backend.prepared is None
    connection.ReadDatabase.assert_not_called()
    connection.CreateDatabase.assert_not_called()


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in rust backend: records the request and returns the canned reply."""
    name = "rust"

    def __init__(self, response=None, responses=None):
        """Store the canned reply (or queue of replies) the async stub will return on each ``execute`` call."""
        self.prepared = None
        self.prepared_requests = []
        self.responses = list(responses or [response or _created_response()])

    async def execute(self, prepared):
        """Record the prepared request and return the next canned reply from the queue."""
        self.prepared = prepared
        self.prepared_requests.append(prepared)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


def test_async_helper_routes_to_rust():
    """Async twin of the rust-route test: the create runs through the async backend
    and returns the created database. The async ``response_hook`` fires once with
    the response headers and database body, matching legacy async behavior."""
    async def run():
        """Run the async create through the Rust backend and assert the hook and returned database."""
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


def test_async_read_database_routes_to_rust():
    """Async database reads use the existing Rust read binding."""
    async def run():
        """Confirm the async read helper dispatches to Rust and fires the hook with the returned database body."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                body=b'{"id":"db1","_rid":"existing"}',
            )
        )
        hook_calls = []

        result = await AsyncDatabaseHelper(connection, backend).read_database(
            "db1",
            {"throughputBucket": 9},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={"timeout": 3.5},
        )

        assert result == {"id": "db1", "_rid": "existing"}
        assert backend.prepared.op == OP_READ_DATABASE
        # The async coordinator builds the request through an ``async def``
        # wrapper, so assert the same request fields the sync test does: a
        # wrapper that dropped an argument would otherwise go unnoticed.
        assert backend.prepared.item_id == "db1"
        assert backend.prepared.body_bytes == b""
        assert backend.prepared.headers["throughputBucket"] == 9
        assert backend.prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5
        connection.ReadDatabase.assert_not_awaited()
        assert hook_calls == [
            ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "existing"})
        ]
        assert isinstance(result, CosmosDict)
        assert type(hook_calls[0][1]) is dict

    asyncio.run(run())


@pytest.mark.parametrize(
    "options,expected",
    [
        # Nothing supplied: return None so the resource method keeps its
        # existing "fall back to the client's default headers" behavior.
        (None, None),
        ({}, None),
        ({"initialHeaders": {}}, None),
        # Supplied: the caller's headers layer over the defaults.
        (
            {"initialHeaders": {"x-custom": "value"}},
            {"x-ms-version": "2020-07-15", "x-custom": "value"},
        ),
        # A name collision goes to the caller -- that is the point of passing it.
        (
            {"initialHeaders": {"x-ms-version": "2018-12-31"}},
            {"x-ms-version": "2018-12-31"},
        ),
    ],
)
def test_resolve_initial_headers_layers_caller_headers_over_defaults(options, expected):
    """The sync and async connections share one merge, so it is tested once.

    Duplicating the merge in each connection is how the two paths drift: one
    gets the override order right and the other does not, and nothing fails.
    """
    default_headers = {"x-ms-version": "2020-07-15"}

    resolved = base.resolve_initial_headers(default_headers, options)

    assert resolved == expected
    # Never mutate the client's shared default headers.
    assert default_headers == {"x-ms-version": "2020-07-15"}


def test_async_connection_read_database_forwards_initial_headers():
    """Prove async database reads preserve caller-supplied initial headers."""
    async def run():
        """Call ``AsyncClientConnection.ReadDatabase`` and verify caller headers are merged into the upstream call."""
        connection = SimpleNamespace(Read=AsyncMock(return_value={"id": "db1"}))
        connection.default_headers = {
            "x-ms-version": "2020-07-15",
            "Cache-Control": "no-cache",
        }
        options = {"initialHeaders": {"x-custom": "value"}}

        result = await AsyncClientConnection.ReadDatabase(
            connection,
            "dbs/db1",
            options=options,
        )

        assert result == {"id": "db1"}
        connection.Read.assert_awaited_once_with(
            "/dbs/db1/",
            "dbs",
            "dbs/db1",
            {
                "x-ms-version": "2020-07-15",
                "Cache-Control": "no-cache",
                "x-custom": "value",
            },
            options,
        )

    asyncio.run(run())


def test_async_read_database_keeps_legacy_read_timeout():
    """Async per-call socket timeouts continue through the legacy transport."""
    async def run():
        """Verify that a ``read_timeout`` kwarg routes the async read to legacy and fires the hook once."""
        response_headers = {"x-ms-request-charge": "1.0"}
        legacy_body = {"id": "db1", "_rid": "legacy"}
        hook_calls = []

        async def legacy_read(_link, *, options, **kwargs):
            """Invoke the caller's response_hook and return the canned legacy body."""
            kwargs["response_hook"](response_headers, legacy_body)
            return legacy_body

        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=legacy_read),
            last_response_headers=response_headers,
        )
        backend = _AsyncRustBackend()

        result = await AsyncDatabaseHelper(connection, backend).read_database(
            "db1",
            {Constants.Kwargs.READ_TIMEOUT: 2},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

        assert result == {"id": "db1", "_rid": "legacy"}
        assert backend.prepared is None
        connection.ReadDatabase.assert_awaited_once()
        link, = connection.ReadDatabase.await_args.args
        awaited_kwargs = connection.ReadDatabase.await_args.kwargs
        assert link == "dbs/db1"
        assert awaited_kwargs["options"] == {Constants.Kwargs.READ_TIMEOUT: 2}
        assert awaited_kwargs[Constants.Kwargs.READ_TIMEOUT] == 2
        assert callable(awaited_kwargs["response_hook"])
        # The hook must fire exactly once on the legacy path too -- the
        # coordinator hands it to the legacy call instead of to the parser.
        assert hook_calls == [(response_headers, legacy_body)]

    asyncio.run(run())


def test_async_read_database_maps_not_found_and_skips_hook():
    """Async twin: a Rust 404 raises the typed error and runs no response hook.

    ``response_hook`` receives the properties of a database that was read. A 404
    means there are none, so calling the hook would hand the caller an error
    payload where they expect database properties.
    """
    async def run():
        """Confirm a Rust 404 response raises ``CosmosResourceNotFoundError`` and the hook is never called."""
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=404,
                headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
                body=b'{"message":"missing"}',
            )
        )
        hook_calls = []

        with pytest.raises(CosmosResourceNotFoundError):
            await AsyncDatabaseHelper(
                SimpleNamespace(last_response_headers={}),
                backend,
            ).read_database(
                "missing",
                {},
                response_hook=lambda headers, body: hook_calls.append((headers, body)),
            )

        assert not hook_calls

    asyncio.run(run())


@pytest.mark.parametrize(
    "operation_kwargs",
    [
        # The driver clamps a sub-second end-to-end timeout up to 1 second.
        {Constants.Kwargs.TIMEOUT: 0.5},
        # The binding ignores non-positive timeouts instead of raising the
        # legacy CosmosClientTimeoutError.
        {Constants.Kwargs.TIMEOUT: 0},
        {Constants.Kwargs.TIMEOUT: -1},
        # Preserve the legacy validation error for malformed values.
        {Constants.Kwargs.TIMEOUT: "1"},
        # Transport keywords are consumed by the azure-core pipeline, which the
        # Rust path does not run.
        {"connection_timeout": 2},
        {"raw_response_hook": object()},
    ],
)
def test_read_database_falls_back_to_legacy_for_options_rust_cannot_honor(
    operation_kwargs,
):
    """A plain read still succeeds -- on the engine that honors the option.

    Unlike ``create_database_if_not_exists``, a single read has nothing to keep
    consistent across two requests, so falling back to legacy is better than
    failing: the caller gets the option they asked for and a database back.
    """
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "legacy"}),
        last_response_headers={},
    )
    backend = _RustBackend()

    result = DatabaseHelper(connection, backend).read_database(
        "db1",
        {},
        kwargs=dict(operation_kwargs),
    )

    assert result == {"id": "db1", "_rid": "legacy"}
    assert backend.prepared is None
    connection.ReadDatabase.assert_called_once_with(
        "dbs/db1", options={}, **operation_kwargs
    )


def test_read_database_falls_back_when_driver_would_replace_initial_header():
    """Prove sync reads use Python when Rust would change a caller header."""
    request_options = {"initialHeaders": {"Accept": "application/custom"}}
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "legacy"}),
        last_response_headers={},
    )
    backend = _RustBackend()

    result = DatabaseHelper(connection, backend).read_database(
        "db1",
        request_options,
    )

    assert result == {"id": "db1", "_rid": "legacy"}
    assert backend.prepared is None
    connection.ReadDatabase.assert_called_once_with(
        "dbs/db1",
        options=request_options,
    )


@pytest.mark.parametrize(
    "operation_kwargs",
    [
        {Constants.Kwargs.TIMEOUT: 0.5},
        {Constants.Kwargs.TIMEOUT: 0},
        {Constants.Kwargs.TIMEOUT: -1},
        {Constants.Kwargs.TIMEOUT: "1"},
        {"connection_timeout": 2},
        {"raw_response_hook": object()},
    ],
)
def test_async_read_database_falls_back_to_legacy_for_options_rust_cannot_honor(
    operation_kwargs,
):
    """Async twin of the single-read fallback."""
    async def run():
        """Read with an unsupported kwarg and confirm legacy is used and Rust backend is untouched."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "legacy"}),
            last_response_headers={},
        )
        backend = _AsyncRustBackend()

        result = await AsyncDatabaseHelper(connection, backend).read_database(
            "db1",
            {},
            kwargs=dict(operation_kwargs),
        )

        assert result == {"id": "db1", "_rid": "legacy"}
        assert backend.prepared is None
        connection.ReadDatabase.assert_awaited_once_with(
            "dbs/db1", options={}, **operation_kwargs
        )

    asyncio.run(run())


def test_async_read_database_falls_back_when_driver_would_replace_initial_header():
    """Prove async reads use Python when Rust would change a caller header."""
    async def run():
        """Read with a caller-owned header Rust would overwrite and confirm legacy is used instead."""
        request_options = {"initialHeaders": {"x-ms-version": "2018-12-31"}}
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "legacy"}),
            last_response_headers={},
        )
        backend = _AsyncRustBackend()

        result = await AsyncDatabaseHelper(connection, backend).read_database(
            "db1",
            request_options,
        )

        assert result == {"id": "db1", "_rid": "legacy"}
        assert backend.prepared is None
        connection.ReadDatabase.assert_awaited_once_with(
            "dbs/db1",
            options=request_options,
        )

    asyncio.run(run())


def test_async_database_proxy_read_selects_rust_backend():
    """The public async proxy delegates its read through the stored backend."""
    async def run():
        """Read via the public async proxy and confirm Rust serves the request, not the legacy connection."""
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                body=b'{"id":"db1","_rid":"existing"}',
            )
        )
        connection = SimpleNamespace(
            _backend=backend,
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            last_response_headers={},
        )

        result = await AsyncDatabaseProxy(connection, "db1").read(throughput_bucket=9)

        assert result == {"id": "db1", "_rid": "existing"}
        assert backend.prepared.op == OP_READ_DATABASE
        assert backend.prepared.headers["throughputBucket"] == 9
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_database_proxy_read_drops_deprecated_session_token():
    """The async proxy also drops the deprecated token before Rust dispatch."""
    async def run():
        """Pass a deprecated ``session_token`` through the async proxy and confirm it is absent from the Rust request."""
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({}),
                body=b'{"id":"db1"}',
            )
        )
        connection = SimpleNamespace(_backend=backend, last_response_headers={})

        with pytest.warns(DeprecationWarning, match="session_token"):
            await AsyncDatabaseProxy(connection, "db1").read(session_token="ignored")

        assert "sessionToken" not in backend.prepared.headers

    asyncio.run(run())


def test_async_helper_does_not_call_response_hook_on_failure():
    """A failed create does not run the caller's response hook.

    ``response_hook`` is customer code that receives the headers and body of a
    successful reply. A 409 means the database was not created, so calling the
    hook would hand them an error payload where they expect database properties.
    """
    async def run():
        """Trigger a 409 from the async backend and confirm the response hook is never called."""
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
        """Create via legacy-only path (no backend) and confirm the async ``CreateDatabase`` is awaited with correct args."""
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
        """Create with a ``read_timeout`` option and confirm the Rust backend is bypassed and the hook fires."""
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
        """Read returns 404 on the legacy async path, triggering a create; assert hook fires once with the created body."""
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
        """Call the public async ``create_database`` and verify the proxy, properties, and hook payload are correct."""
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
    the final database properties while orchestration remains in Python."""
    sync_client = object.__new__(CosmosClient)
    sync_client.client_connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        CreateDatabase=MagicMock(),
        last_response_headers={},
    )
    sync_backend = _RustBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({}),
            body=b'{"id":"db1","_rid":"existing"}',
        )
    )
    sync_client._backend = sync_backend

    proxy, properties = sync_client.create_database_if_not_exists(
        "db1",
        return_properties=True,
    )
    assert proxy.id == "db1"
    assert properties["_rid"] == "existing"
    assert sync_backend.prepared.op == OP_READ_DATABASE

    async def run():
        """Call the public async ``create_database_if_not_exists`` with an existing database and verify Rust serves the read."""
        async_client = object.__new__(AsyncCosmosClient)
        async_client.client_connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            CreateDatabase=AsyncMock(),
            last_response_headers={},
        )
        async_backend = _AsyncRustBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({}),
                body=b'{"id":"db1","_rid":"existing"}',
            )
        )
        async_client._backend = async_backend
        async_proxy, async_properties = await async_client.create_database_if_not_exists(
            "db1",
            return_properties=True,
        )
        assert async_proxy.id == "db1"
        assert async_properties["_rid"] == "existing"
        assert async_backend.prepared.op == OP_READ_DATABASE

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
    client.client_connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1"}),
        CreateDatabase=MagicMock(),
        last_response_headers={},
    )
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
    if method_name == "create_database":
        assert "sessionToken" not in backend.prepared.headers
        assert "accessCondition" not in backend.prepared.headers
    else:
        assert backend.prepared.op == OP_READ_DATABASE
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
        """Pass inapplicable conditions to the async method and confirm they are warned about and absent from the Rust request."""
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1"}),
            CreateDatabase=AsyncMock(),
            last_response_headers={},
        )
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
        if method_name == "create_database":
            assert "sessionToken" not in backend.prepared.headers
            assert "accessCondition" not in backend.prepared.headers
        else:
            assert backend.prepared.op == OP_READ_DATABASE
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


def test_async_if_not_exists_uses_python_coordinator_with_rust_selected():
    """Async twin: the database already exists, so the read is the only request
    sent and no legacy call is made."""
    async def run():
        """Read an existing database via the async coordinator and confirm only a Rust read is dispatched."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            CreateDatabase=AsyncMock(),
            last_response_headers={"x-ms-request-charge": "1.0"},
        )
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                body=b'{"id":"db1","_rid":"existing"}',
            )
        )
        hook_calls = []

        result = await AsyncDatabaseHelper(connection, backend).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )

        assert result["_rid"] == "existing"
        assert [request.op for request in backend.prepared_requests] == [OP_READ_DATABASE]
        connection.ReadDatabase.assert_not_awaited()
        connection.CreateDatabase.assert_not_awaited()
        assert hook_calls == [
            (
                {"x-ms-request-charge": "1.0"},
                {"id": "db1", "_rid": "existing"},
            )
        ]

    asyncio.run(run())


def test_async_if_not_exists_rust_404_then_rust_create_without_legacy_calls():
    """Async twin: the database is missing, so both requests run on the Rust path.

    Async clients are a separate code path with their own coordinator, so the same
    behavior has to be proven twice.
    """
    async def run():
        """Send read-then-create through the async Rust backend and confirm options are split correctly across both requests."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            CreateDatabase=AsyncMock(side_effect=AssertionError("legacy create called")),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(
            responses=[
                BackendResponse(
                    status_code=404,
                    headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                    body=b'{"message":"missing"}',
                ),
                _created_response(),
            ]
        )
        hook_calls = []

        result = await AsyncDatabaseHelper(
            connection,
            backend,
        ).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400, "throughputBucket": 7},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )

        assert result["_rid"] == "rid1"
        assert [request.op for request in backend.prepared_requests] == [
            OP_READ_DATABASE,
            OP_CREATE_DATABASE,
        ]
        assert "offerThroughput" not in backend.prepared_requests[0].headers
        assert backend.prepared_requests[0].headers["throughputBucket"] == 7
        assert backend.prepared_requests[1].headers["offerThroughput"] == 400
        assert hook_calls == [
            (
                {"x-ms-request-charge": "5.25"},
                {"id": "db1", "_rid": "rid1"},
            )
        ]
        connection.ReadDatabase.assert_not_awaited()
        connection.CreateDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_if_not_exists_rust_create_race_propagates_conflict():
    """Async twin: a database created by someone else between the two requests
    surfaces as a conflict error instead of a silent success."""
    async def run():
        """Read returns 404 then create returns 409; confirm the conflict error propagates and no legacy call is made."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            CreateDatabase=AsyncMock(side_effect=AssertionError("legacy create called")),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(
            responses=[
                BackendResponse(
                    status_code=404,
                    headers=CaseInsensitiveDict({}),
                    body=b'{"message":"missing"}',
                ),
                BackendResponse(
                    status_code=409,
                    headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
                    body=b'{"message":"database exists"}',
                ),
            ]
        )

        with pytest.raises(CosmosResourceExistsError):
            await AsyncDatabaseHelper(
                connection,
                backend,
            ).create_database_if_not_exists(
                {"id": "db1"},
                {"offerThroughput": 400},
            )

        assert [request.op for request in backend.prepared_requests] == [
            OP_READ_DATABASE,
            OP_CREATE_DATABASE,
        ]
        connection.ReadDatabase.assert_not_awaited()
        connection.CreateDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_if_not_exists_legacy_existing_skips_create_and_strips_create_only_options():
    """Async twin of ``test_sync_if_not_exists_legacy_returns_existing_without_create_headers``:
    the legacy path returns the existing database without calling CreateDatabase, and
    strips provisioning-only options (offerThroughput, autoUpgradePolicy) from the
    ReadDatabase call while keeping others (e.g. throughputBucket)."""
    async def run():
        """Read returns the existing database; confirm provisioning-only options are stripped from the read and create is never called."""
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


def test_async_if_not_exists_legacy_preserves_read_timeout_on_both_legs():
    """Async twin: one per-call socket timeout applies to the read and the create."""
    async def run():
        """Confirm a ``read_timeout`` kwarg is forwarded to both the async read and create legacy calls."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(
                side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
            ),
            CreateDatabase=AsyncMock(return_value={"id": "db1", "_rid": "created"}),
            last_response_headers={},
        )

        result = await AsyncDatabaseHelper(
            connection,
            None,
        ).create_database_if_not_exists(
            {"id": "db1"},
            {},
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

        assert result["_rid"] == "created"
        assert connection.ReadDatabase.call_args.kwargs[Constants.Kwargs.READ_TIMEOUT] == 2
        assert connection.CreateDatabase.call_args.kwargs[Constants.Kwargs.READ_TIMEOUT] == 2

    asyncio.run(run())


@pytest.mark.parametrize(
    "request_options,operation_kwargs",
    [
        ({Constants.Kwargs.READ_TIMEOUT: 2}, {}),
        ({}, {Constants.Kwargs.READ_TIMEOUT: 2}),
        # Both legs share DatabaseProxy.read's eligibility rule, so every option
        # that sends a plain read to the legacy path stops a get-or-create here.
        # The driver clamps a sub-second end-to-end timeout to 1 second, and a
        # transport keyword is consumed by the azure-core pipeline the Rust path
        # never runs.
        ({}, {Constants.Kwargs.TIMEOUT: 0.5}),
        ({}, {"connection_timeout": 2}),
    ],
)
def test_async_if_not_exists_read_timeout_never_crosses_from_rust_to_legacy(
    request_options,
    operation_kwargs,
):
    """Async twin: an unsupported socket timeout fails without engine mixing, and
    without sending either request."""
    async def run():
        """Attempt ``create_database_if_not_exists`` with a Rust-incompatible option and confirm it raises ``NotImplementedError`` before any request is sent."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1"}),
            CreateDatabase=AsyncMock(),
            last_response_headers={},
        )
        backend = _AsyncRustBackend()

        with pytest.raises(NotImplementedError, match="create_database_if_not_exists"):
            await AsyncDatabaseHelper(
                connection,
                backend,
            ).create_database_if_not_exists(
                {"id": "db1"},
                request_options,
                kwargs=operation_kwargs,
            )

        assert backend.prepared is None
        connection.ReadDatabase.assert_not_awaited()
        connection.CreateDatabase.assert_not_awaited()

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
        """Read raises a non-404 error on the async legacy path; confirm it propagates and create is never called."""
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


# ---------------------------------------------------------------------------
# delete_database
# ---------------------------------------------------------------------------


def _deleted_response() -> BackendResponse:
    """Return a successful fake database-delete response."""
    # A canned "204 No Content" reply: what the service returns for a successful
    # delete. There is no body, which is exactly what the parse step has to
    # tolerate.
    return BackendResponse(
        status_code=204,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "4.24"}),
        body=b"",
    )


def test_delete_database_is_registered_as_single_response_operation():
    """Delete-database is a single-reply operation, so it dispatches to the
    binding's ``delete_database`` entry point rather than the paged query path."""
    assert OP_TO_BINDING_METHOD[OP_DELETE_DATABASE] == "delete_database"


@pytest.mark.parametrize(
    "database_link,expected_id",
    [
        ("dbs/db1", "db1"),
        ("dbs/db1/", "db1"),
        ("/dbs/db1/", "db1"),
        ("dbs/my db", "my db"),
    ],
)
def test_delete_database_prepared_derives_the_id_from_the_link(database_link, expected_id):
    """The binding names the database, while the legacy path passes the whole
    ``dbs/{id}`` link. The link forms the legacy parser accepts must all reduce to
    the same name here, or the two paths would delete different databases -- or
    the Rust path would delete nothing and report success."""
    prepared = build_delete_database_prepared(database_link, {})

    assert prepared.op == OP_DELETE_DATABASE
    assert prepared.item_id == expected_id
    assert prepared.body_bytes == b""
    assert prepared.container_link == ""
    assert prepared.partition_key_header == "[]"


@pytest.mark.parametrize("database_link", ["dbs/", "dbs", "/dbs/", ""])
def test_delete_database_prepared_rejects_a_link_with_no_id(database_link):
    """A link with no name raises the same error the legacy link parser raises,
    rather than sending an account-level request that fails later with a different
    service error."""
    with pytest.raises(ValueError, match="Failed Parsing ResourceID from link"):
        build_delete_database_prepared(database_link, {})


def test_delete_database_prepared_drops_headers_the_legacy_path_suppresses():
    """A database is a master resource: the legacy path attaches no session token
    and drops the intended-collection-rid header. The Rust request has to carry the
    same headers, while keeping the options the customer did set."""
    prepared = build_delete_database_prepared(
        "dbs/db1",
        {
            "sessionToken": "session",
            Constants.ContainerRID: "rid1",
            "throughputBucket": 7,
        },
        kwargs={"timeout": 3.5},
    )

    assert "sessionToken" not in prepared.headers
    assert Constants.ContainerRID not in prepared.headers
    assert prepared.headers["throughputBucket"] == 7
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5


def test_sync_delete_database_routes_to_rust_and_never_calls_legacy():
    """On a rust-backed client the delete runs through the backend, records the
    response headers on the connection, and returns nothing. A 204 with no body is
    a success, not a parse failure."""
    connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())

    result = DatabaseHelper(connection, backend).delete_database(
        "dbs/db1",
        {"throughputBucket": 7},
        kwargs={"timeout": 3.5},
    )

    assert result is None
    assert backend.prepared.op == OP_DELETE_DATABASE
    assert backend.prepared.item_id == "db1"
    assert backend.prepared.headers["throughputBucket"] == 7
    assert connection.last_response_headers["x-ms-request-charge"] == "4.24"
    connection.DeleteDatabase.assert_not_called()


def test_sync_delete_database_raises_not_found_for_a_missing_database():
    """The parse step is what turns a 404 into the typed error. Dropping the parse
    because the delete returns nothing would turn a failed delete into a silent
    success."""
    connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(
        BackendResponse(
            status_code=404,
            headers=CaseInsensitiveDict({}),
            body=b'{"message":"Resource Not Found"}',
        )
    )

    with pytest.raises(CosmosResourceNotFoundError):
        DatabaseHelper(connection, backend).delete_database("dbs/db1", {})


def test_sync_delete_database_keeps_legacy_path_for_read_timeout():
    """A socket-level ``read_timeout`` has no per-request equivalent on the Rust
    path, so the delete stays on legacy rather than accepting the number and not
    applying it."""
    connection = SimpleNamespace(
        DeleteDatabase=MagicMock(return_value=None),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())

    DatabaseHelper(connection, backend).delete_database(
        "dbs/db1",
        {Constants.Kwargs.READ_TIMEOUT: 2},
        kwargs={},
    )

    assert backend.prepared is None
    connection.DeleteDatabase.assert_called_once()
    assert connection.DeleteDatabase.call_args.args[0] == "dbs/db1"


def test_async_delete_database_routes_to_rust_and_never_calls_legacy():
    """Prove async database deletion uses Rust and does not call Python."""
    async def run():
        """Drive the async delete through Rust and verify the backend was used, not legacy."""
        connection = SimpleNamespace(
            DeleteDatabase=AsyncMock(side_effect=AssertionError("legacy delete called")),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(_deleted_response())

        result = await AsyncDatabaseHelper(connection, backend).delete_database(
            "dbs/db1",
            {"throughputBucket": 7},
            kwargs={"timeout": 3.5},
        )

        assert result is None
        assert backend.prepared.op == OP_DELETE_DATABASE
        assert backend.prepared.item_id == "db1"
        assert connection.last_response_headers["x-ms-request-charge"] == "4.24"
        connection.DeleteDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_delete_database_keeps_legacy_path_for_read_timeout():
    """Prove async database deletion uses Python for ``read_timeout``."""
    async def run():
        """Drive the async delete with ``read_timeout`` and verify legacy was used, not Rust."""
        connection = SimpleNamespace(
            DeleteDatabase=AsyncMock(return_value=None),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(_deleted_response())

        await AsyncDatabaseHelper(connection, backend).delete_database(
            "dbs/db1",
            {Constants.Kwargs.READ_TIMEOUT: 2},
            kwargs={},
        )

        assert backend.prepared is None
        connection.DeleteDatabase.assert_awaited_once()

    asyncio.run(run())


@pytest.mark.parametrize(
    "database_argument",
    ["db1", {"id": "db1", "_self": "dbs/db1/"}],
    ids=["name", "properties"],
)
def test_public_sync_delete_database_accepts_every_argument_form(database_argument):
    """``delete_database`` takes a name, a properties mapping, or a proxy. All three
    have to reach the backend as the same database, because the reduction from
    argument to link happens once and the Rust request derives its name from it."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())
    client._backend = backend

    assert client.delete_database(database_argument) is None
    assert backend.prepared.op == OP_DELETE_DATABASE
    assert backend.prepared.item_id == "db1"


def test_public_sync_delete_database_accepts_a_proxy():
    """The proxy form of the same check."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())
    client._backend = backend

    client.delete_database(DatabaseProxy(client.client_connection, "db1"))

    assert backend.prepared.item_id == "db1"


def test_public_sync_delete_database_fires_response_hook_with_headers_only():
    """The public hook for a delete takes the headers alone -- there is no body to
    hand it. Routing through the coordinator must not change that signature."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    client._backend = _RustBackend(_deleted_response())
    hook_calls = []

    client.delete_database("db1", response_hook=lambda headers: hook_calls.append(headers))

    assert len(hook_calls) == 1
    assert hook_calls[0]["x-ms-request-charge"] == "4.24"


def test_sync_delete_database_forwards_the_conditions_it_warns_about():
    """The sync method warns once each for ``session_token``, ``etag`` and
    ``match_condition`` -- but, exactly as in the released v4 SDK, it still forwards
    them to ``build_options``. So ``match_condition`` really does put an ``If-Match``
    on the wire; only ``session_token`` is dropped, because a database is a master
    resource and the legacy ``GetHeaders`` never attaches a session token to one.
    Treating the warnings as if they meant "silently discarded" would make the rust
    path send an unconditional delete for a caller who asked for a conditional one."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())
    client._backend = backend

    with pytest.warns(UserWarning) as warnings_seen:
        client.delete_database(
            "db1",
            session_token="session",
            etag="etag",
            match_condition=MatchConditions.IfNotModified,
        )

    assert len(warnings_seen) == 3
    prepared = backend.prepared
    assert prepared is not None
    assert prepared.item_id == "db1"
    assert prepared.headers["If-Match"] == "etag"
    assert "sessionToken" not in prepared.headers
    assert "x-ms-session-token" not in prepared.headers


def test_sync_delete_database_stays_on_legacy_when_build_options_leaves_an_etag():
    """``MatchConditions.IfPresent`` sets ``If-Match: *`` and -- a quirk of
    ``_get_match_headers`` that predates the rust path -- leaves ``etag`` behind in
    the kwargs. A leftover kwarg is exactly what the eligibility gate exists to catch:
    it means something the rust request builder has not accounted for, so the call
    stays on the legacy transport, which receives the kwarg just as it does in v4."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())
    client._backend = backend

    with pytest.warns(UserWarning) as warnings_seen:
        client.delete_database(
            "db1",
            session_token="session",
            etag="etag",
            match_condition=MatchConditions.IfPresent,
        )

    assert len(warnings_seen) == 3
    assert backend.prepared is None
    call = client.client_connection.DeleteDatabase.call_args
    assert call.kwargs["options"]["accessCondition"] == {"type": "IfMatch", "condition": "*"}
    assert call.kwargs["etag"] == "etag"


def test_async_delete_database_forwards_the_conditions_it_warns_about():
    """Prove the async method forwards conditions and emits ``DeprecationWarning``
    warns with ``UserWarning``. That difference predates the rust path and routing
    through the coordinator must not change it."""
    async def run():
        """Verify the async public method forwards conditions to ``build_options`` and emits ``DeprecationWarning``."""
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = SimpleNamespace(
            DeleteDatabase=AsyncMock(side_effect=AssertionError("legacy delete called")),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(_deleted_response())
        client._backend = backend

        with pytest.warns(DeprecationWarning) as warnings_seen:
            await client.delete_database(
                "db1",
                session_token="session",
                etag="etag",
                match_condition=MatchConditions.IfNotModified,
            )

        assert len(warnings_seen) == 3
        prepared = backend.prepared
        assert prepared is not None
        assert prepared.item_id == "db1"
        assert prepared.headers["If-Match"] == "etag"
        assert "sessionToken" not in prepared.headers
        assert "x-ms-session-token" not in prepared.headers

    asyncio.run(run())
