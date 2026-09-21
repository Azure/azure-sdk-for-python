# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for account-level database backend routing (no network).

Three public methods land here. ``create_database`` sends one request.
``DatabaseProxy.read`` sends one request -- a customer asking for a database's
properties. ``create_database_if_not_exists`` reads the database and creates it
only if the read comes back not-found. A creation conflict adds one final read.
The Rust driver
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

* the request the Rust engine is handed -- database name, no body, the headers
  built from the caller's options, and the per-call ``timeout``. If any of that
  is wrong the call reads the wrong database or drops an option.
* rejecting Rust reads when an option cannot be honored exactly, without
  replaying through legacy transport or silently rounding a deadline.
* ``response_hook`` firing exactly once, with the response headers and the
  properties, on **both** engines. Customers use it for cost and audit logging,
  so firing twice double-counts and firing zero times loses the record.
* a missing database raising the typed not-found error, with the hook not
  firing. Customers catch that type to decide whether to create the database.
* get-or-create checking both read and create eligibility before its first
  request, without switching backends halfway through.
* ``initial_headers`` layering over the client's default headers, with the
  caller winning a name collision -- that is the point of passing them.

Every read test is written twice, once sync and once async. That is not
duplication for its own sake: the async path builds its request through a
different wrapper, so it is separate code that can break on its own.

All fakes, no Cosmos account.
"""

from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings

import asyncio
import inspect
import json
import warnings
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import ServiceRequestError
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _base as base
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.operations import (
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
from azure.cosmos._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    is_read_database_rust_eligible,
)
from azure.cosmos._helpers._database_operations import DatabaseHelper
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncClientConnection,
)
from azure.cosmos.aio._cosmos_client import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.aio._helpers._database_operations import AsyncDatabaseHelper
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceExistsError, CosmosResourceNotFoundError
from azure.cosmos.offer import ThroughputProperties


def _created_response() -> BackendResponse:
    """Return a successful fake database-create response."""
    # A canned "201 Created" reply from the Rust backend: the new database's body
    # plus a request-charge header, used by the fake backends below.
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"db1","_rid":"rid1"}',
    )


def test_create_database_is_registered_as_single_response_operation():
    """Create-database is wired as a single-reply operation, so it is sent to the
    binding's ``create_database`` entry point rather than the paged query path."""
    assert OP_TO_BINDING_METHOD[OP_CREATE_DATABASE] == "create_database"


def test_create_database_if_not_exists_is_not_registered_in_the_binding():
    """The compound coordinator is not a wire op; its read primitive is."""
    assert "create_database_if_not_exists" not in OP_TO_BINDING_METHOD
    assert OP_TO_BINDING_METHOD[OP_READ_DATABASE] == "read_database"


@pytest.mark.parametrize("autoscale_mode", [False, True])
def test_create_database_prepared_request_preserves_body_and_options(autoscale_mode):
    """The request handed to the Rust backend carries everything the create needs:
    the database body, account-level scope (empty container link, cross-partition
    ``"[]"`` header since there is no partition key), and every option the customer
    set -- fixed throughput, autoscale settings, throughput bucket, custom headers,
    and the timeout deadline."""
    autoscale = '{"maxThroughput":4000}'
    prepared = build_create_database_prepared(
        {"id": "db1"},
        {
            **({"autoUpgradePolicy": autoscale} if autoscale_mode else {"offerThroughput": 400}),
            "throughputBucket": 7,
            "initialHeaders": {"x-custom": "value"},
        },
        kwargs={"timeout": 3.5},
    )

    assert prepared.op == OP_CREATE_DATABASE
    assert prepared.container_link == ""
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert json.loads(prepared.body_bytes) == {"id": "db1"}
    if autoscale_mode:
        assert wire_headers(prepared)["x-ms-cosmos-offer-autopilot-settings"] == autoscale
        assert "x-ms-offer-throughput" not in wire_headers(prepared)
    else:
        assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'
        assert "x-ms-cosmos-offer-autopilot-settings" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-custom": "value"}).items())
    assert settings_options(prepared)["timeout_seconds"] == 3.5


def test_read_database_prepared_request_is_bodiless():
    """The existence read sends no body, only the database id.

    Create sends the database definition; read identifies the database by id alone.
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
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert settings_options(prepared)["timeout_seconds"] == 3.5


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

    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in (initial_headers).items())
    assert wire_headers(prepared) is not initial_headers
    from azure.cosmos._helpers._request_settings import OPTION_HEADER_NAMES
    for option_key, option_value in options.items():
        if option_key not in ("initialHeaders", "sessionToken"):
            assert wire_headers(prepared)[OPTION_HEADER_NAMES[option_key]] == str(option_value)
    assert "sessionToken" not in wire_headers(prepared)


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

    assert option_key not in wire_headers(prepared)


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
        ({}, {"timeout": float("nan")}, False),
        ({}, {"timeout": float("inf")}, False),
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
    """Stand-in Rust backend: records the request it was handed and returns a canned
    reply, so a test can check what would have gone on the wire without a network."""
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


def test_sync_helper_routes_to_rust_and_parses_response():
    """On a Rust-backed client the coordinator runs the create through the backend,
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
    assert wire_headers(backend.prepared)["x-ms-offer-throughput"] == '400'
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
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert settings_options(backend.prepared)["timeout_seconds"] == 3.5
    connection.ReadDatabase.assert_not_called()
    assert hook_calls == [
        ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "existing"})
    ]
    assert isinstance(result, CosmosDict)
    assert type(hook_calls[0][1]) is dict


def test_sync_read_database_keeps_legacy_path_and_read_timeout():
    """Choosing the legacy helper explicitly still passes the internal timeout through."""
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
    result = DatabaseHelper(connection, LEGACY_BACKEND).read_database(
        "db1",
        {Constants.Kwargs.READ_TIMEOUT: 2},
        response_hook=response_hook,
        kwargs={Constants.Kwargs.READ_TIMEOUT: 2, "response_hook": MagicMock()},
    )

    assert result == {"id": "db1", "_rid": "legacy"}
    connection.ReadDatabase.assert_called_once_with(
        "dbs/db1",
        options={Constants.Kwargs.READ_TIMEOUT: 2},
        **{
            Constants.Kwargs.READ_TIMEOUT: 2,
            "response_hook": ANY,
        },
    )
    assert hook_calls == [
        ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "legacy"})
    ]


def test_sync_read_database_maps_not_found_and_skips_hook():
    """A not-found from the Rust engine still raises the typed not-found error."""
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
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    connection.ReadDatabase.assert_not_called()


def test_sync_database_proxy_read_rejects_deprecated_session_token():
    """Obsolete session-token usage fails before any request is sent."""
    backend = _RustBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({}),
            body=b'{"id":"db1"}',
        )
    )
    connection = SimpleNamespace(_backend=backend, last_response_headers={})

    with pytest.raises(TypeError, match="session_token"):
        DatabaseProxy(connection, "db1").read(session_token="ignored")

    assert backend.prepared is None


@pytest.fixture(params=["sync", "async"])
def database_read_case(request):
    """Build a ``DatabaseProxy`` whose read can be run against either engine.

    Each test using this fixture runs twice, once sync and once async, because
    the two proxies build their requests through separate code.

    Both engines are wired to hand back the same activity id, the same request
    charge, and the same body, so a test can switch engines and compare behavior
    without the response itself changing. The Rust backend's ``execute`` is
    wrapped in a mock, and the legacy ``ReadDatabase`` is a stand-in that also
    fires the caller's ``response_hook``, matching what the real legacy path
    does.

    One deliberate trap: the proxy starts out holding stale properties with an
    etag of ``"old"``. A successful read must replace them, and a failed read
    must leave them alone. Without that starting value a test could not tell the
    two apart.
    """
    response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-activity-id": "read-one", "x-ms-request-charge": "1.5"}),
        body=b'{"id":"db1","_etag":"v1"}',
        diagnostics="activity=read-one requests=1",
    )
    is_async = request.param == "async"
    backend = _AsyncRustBackend(response) if is_async else _RustBackend(response)
    mock_type = AsyncMock if is_async else MagicMock
    backend.execute = mock_type(wraps=backend.execute)
    connection = SimpleNamespace(_backend=backend, last_response_headers={})

    def legacy_read(*args, **kwargs):
        headers = CaseInsensitiveDict({"x-ms-activity-id": "read-one", "x-ms-request-charge": "1.5"})
        body = {"id": "db1", "_etag": "v1"}
        connection.last_response_headers = headers
        result = CosmosDict(body, response_headers=headers)
        hook = kwargs.get("response_hook")
        if hook:
            hook(headers, body)
        return result

    connection.ReadDatabase = mock_type(side_effect=legacy_read)
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    return SimpleNamespace(
        proxy=proxy_type(connection, "db1", properties={"id": "db1", "_etag": "old"}),
        connection=connection,
        backend=backend,
        legacy_backend=ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND,
    )


def _call_database_read(case, *args, **kwargs):
    """Call ``proxy.read`` and wait for it if the async proxy is under test.

    Lets one test body cover both the sync and the async proxy.
    """
    result = case.proxy.read(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize(
    "option, value",
    [(option, value) for option in ("session_token", "populate_query_metrics")
     for value in (None, False, True, "unused")]
    + [("read_timeout", value) for value in (False, True, "unused")],
)
def test_database_read_rejects_obsolete_and_socket_options(database_read_case, use_legacy, option, value):
    """Retired options are refused up front on both engines, whatever value they
    carry.

    ``session_token`` and ``populate_query_metrics`` no longer do anything, and
    ``read_timeout`` is a socket-level setting this method does not support. All
    three raise ``TypeError`` naming the offending option, including when the
    value passed is ``None`` or ``False`` -- a customer who leaves one of these
    in their call should be told, not silently ignored.

    The rejection happens before any request is sent, so no engine is called,
    the hook never fires, and the cached properties still hold the stale etag.
    """
    case = database_read_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _call_database_read(case, response_hook=hook, **{option: value})
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert case.proxy._properties["_etag"] == "old"


@pytest.mark.parametrize("value", [None, False, True])
def test_database_read_is_keyword_only(database_read_case, value):
    """``read`` takes no positional arguments, so a stray one is a ``TypeError``
    rather than being quietly bound to the first keyword and changing what the
    call does. Nothing is sent to either engine.
    """
    with pytest.raises(TypeError):
        _call_database_read(database_read_case, value)
    database_read_case.backend.execute.assert_not_called()
    database_read_case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10, float(2**64 - 2048)])
def test_database_read_preserves_supported_options_and_refreshes_properties(database_read_case, timeout):
    """Supported options reach the Rust request unchanged, and the read refreshes
    the proxy's cached properties.

    The request names the right database, sends no body, carries the caller's
    own header, and carries the throughput bucket. The per-call ``timeout``
    arrives as a deadline in seconds; when it is left off, no overall-timeout
    header is added at all rather than a made-up default being sent.

    Afterwards the proxy holds the object the read returned, so a customer who
    reads and then inspects properties sees the values that just came back
    instead of the stale ones. A second read goes to the Rust engine as well,
    confirming a completed read does not switch the proxy over to legacy.
    """
    case = database_read_case
    result = _call_database_read(
        case, timeout=timeout, read_timeout=None, throughput_bucket=7,
        initial_headers={"x-my-app": "catalog"},
    )
    assert isinstance(result, CosmosDict)
    assert result == {"id": "db1", "_etag": "v1"}
    assert case.proxy._properties is result
    prepared = case.backend.prepared
    assert prepared.op == OP_READ_DATABASE
    assert prepared.item_id == "db1"
    assert prepared.body_bytes == b""
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-my-app": "catalog"}).items())
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert settings_options(prepared).get("timeout_seconds") == timeout
    if timeout is None:
        assert Constants.OVERALL_TIMEOUT_SECONDS not in wire_headers(prepared)
    _call_database_read(case)
    assert case.backend.execute.call_count == 2
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize(
    "timeout",
    [False, True, 0, -1, 0.5, "10", float("nan"), float("inf"), -float("inf"),
     2**64 - 1, 2**64, 10**400],
    ids=["false", "true", "zero", "negative", "subsecond", "string", "nan", "inf",
         "negative-inf", "rounds-out-of-range", "out-of-range", "overflow"],
)
def test_database_read_invalid_timeout_never_reaches_a_transport(database_read_case, timeout):
    """A timeout the Rust engine cannot express exactly is refused before anything
    is sent.

    The list covers booleans, zero, negatives, a value below one second, a
    string, the three non-finite floats, and values at or past the range the
    engine can hold. Each raises ``NotImplementedError`` telling the customer to
    use the legacy Python client for this call.

    Neither engine is invoked, so an unusable deadline can never be rounded into
    a usable one behind the customer's back. The compatibility fallback counter
    is also unchanged: this is an outright refusal, not a recorded fallback.
    """
    case = database_read_case
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
        _call_database_read(case, timeout=timeout)
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"connection_timeout": 1},
        {"raw_request_hook": lambda request: None},
        {"raw_response_hook": lambda response: None},
        {"unknown_option": True},
        {"initial_headers": {"User-Agent": "custom"}},
        {"initial_headers": {"X-MS-VERSION": "custom"}},
        {"initial_headers": {"Accept": "custom"}},
        {"initial_headers": {"Cache-Control": "custom"}},
        {"request_options": {"timeout": 10}},
    ],
)
def test_database_read_unsupported_settings_never_fall_back(database_read_case, kwargs):
    """Settings the Rust engine cannot honor raise instead of quietly replaying the
    call through the legacy transport.

    The list covers a socket-level connect timeout, the two raw request and
    response hooks, an unknown keyword, four headers the driver owns and a
    caller must not override, and a raw request-options dictionary.

    Each raises ``NotImplementedError`` pointing at the legacy Python client.
    The hook never fires and no request is sent, so a customer does not end up
    on a different transport, with different retries and diagnostics, without
    having asked for it.
    """
    case = database_read_case
    hook = MagicMock()
    with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
        _call_database_read(case, response_hook=hook, **kwargs)
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True])
def test_database_read_hook_snapshot_is_isolated_and_falsey_callable_runs(database_read_case, use_legacy):
    """The response hook runs once on both engines, and gets its own copy of the
    headers.

    Two things are checked at the same time. First, the hook here is an object
    that reports itself as false when tested as a boolean. It is still callable,
    so it must still run: deciding whether to call a hook by truth-testing it
    would skip a perfectly valid one.

    Second, the headers handed to the hook are a private copy. The hook edits
    them and the client's own record is unaffected; the returned response still
    reports the real request charge; and later changes to the client's headers
    do not reach back into what the hook already received. A customer logging
    cost from the hook gets the charge for their call, not a value some later
    request overwrote.

    On the Rust engine the hook also receives the driver diagnostics header.
    """
    case = database_read_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert headers["X-MS-ACTIVITY-ID"] == "read-one"
            assert body == {"id": "db1", "_etag": "v1"}
            assert type(body) is dict
            calls.append(headers)
            headers["x-ms-request-charge"] = "modified"
            assert case.connection.last_response_headers["x-ms-request-charge"] == "1.5"

    result = _call_database_read(case, response_hook=Hook())
    assert len(calls) == 1
    assert result.get_response_headers()["x-ms-request-charge"] == "1.5"
    assert calls[0] is not result.get_response_headers()
    assert calls[0] is not case.connection.last_response_headers
    case.connection.last_response_headers["x-ms-activity-id"] = "later"
    assert calls[0]["x-ms-activity-id"] == "read-one"
    if use_legacy:
        case.backend.execute.assert_not_called()
        case.connection.ReadDatabase.assert_called_once()
    else:
        case.backend.execute.assert_called_once()
        case.connection.ReadDatabase.assert_not_called()
        assert "x-ms-cosmos-sdk-diagnostics" in calls[0]


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {}),
        ({"etag": "v1", "match_condition": MatchConditions.IfNotModified}, {"If-Match": "v1"}),
        ({"etag": "v1", "match_condition": MatchConditions.IfModified}, {"If-None-Match": "v1"}),
        ({"match_condition": MatchConditions.IfPresent}, {"If-Match": "*"}),
        ({"match_condition": MatchConditions.IfMissing}, {"If-None-Match": "*"}),
        ({"etag": "unused", "match_condition": MatchConditions.IfPresent}, {"If-Match": "*"}),
        ({"etag": "unused", "match_condition": MatchConditions.IfMissing}, {"If-None-Match": "*"}),
        ({"if_match": "v1"}, {"If-Match": "v1"}),
        ({"if_none_match": "v1"}, {"If-None-Match": "v1"}),
    ],
)
def test_database_read_preserves_conditional_headers(database_read_case, use_legacy, kwargs, expected):
    """Conditional read arguments turn into the same request headers on both
    engines.

    An etag with a not-modified condition becomes ``If-Match``; with a modified
    condition it becomes ``If-None-Match``. A presence or absence condition
    becomes the wildcard form, and in that case any etag passed alongside is
    ignored, since the condition does not depend on a version. The raw
    ``if_match`` and ``if_none_match`` arguments pass through as given.

    No warning is raised for any of these. A customer relying on a conditional
    read to avoid clobbering a concurrent change must get identical behavior
    whichever engine they are on.
    """
    from common.typed_requests import flatten_options_to_headers

    case = database_read_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_database_read(case, **kwargs)
    assert caught == []
    if use_legacy:
        call = case.connection.ReadDatabase.call_args
        headers = flatten_options_to_headers(call.kwargs["options"])
        assert "etag" not in call.kwargs
        case.backend.execute.assert_not_called()
    else:
        headers = wire_headers(case.backend.prepared)
        case.connection.ReadDatabase.assert_not_called()
    assert {
        key.lower(): value for key, value in headers.items()
        if key.lower() in ("if-match", "if-none-match")
    } == {key.lower(): value for key, value in expected.items()}


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize(
    "kwargs, error_type",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"etag": "", "match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"etag": "v1", "match_condition": "invalid"}, TypeError),
    ],
)
def test_database_read_invalid_guards_fail_before_dispatch(database_read_case, use_legacy, kwargs, error_type):
    """Incomplete or malformed conditional arguments fail before a request is sent,
    on both engines.

    An etag with no condition, a condition with no etag, and an empty etag are
    all ``ValueError``; a condition that is not a real match condition is a
    ``TypeError``. Sending any of these would produce a read whose conditional
    behavior is not what the customer asked for, so the call is stopped instead.
    """
    case = database_read_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(error_type):
        _call_database_read(case, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("failure_source", ["hook", "backend"])
@pytest.mark.parametrize("error_type", [ValueError, ServiceRequestError, NotImplementedError, asyncio.CancelledError])
def test_database_read_exceptions_never_replay_or_replace_cached_properties(
    database_read_case, failure_source, error_type
):
    """A failure in either the hook or the engine is raised as-is, with no retry and
    no damage to the cached properties.

    The same four error types are raised from two places: from the customer's
    own response hook, and from the engine itself. In every combination the
    exact exception object reaches the caller, rather than being wrapped or
    turned into a different type.

    The engine is called exactly once, the legacy path is never tried, and the
    compatibility fallback counter does not move -- a failed read must not be
    replayed on the other engine, which for the hook case would mean running the
    customer's code twice. The proxy also keeps its previous properties, so a
    failed read never leaves a half-updated view behind.
    """
    case = database_read_case
    error = error_type("read failed")
    hook = MagicMock(side_effect=error if failure_source == "hook" else None)
    if failure_source == "backend":
        case.backend.execute.side_effect = error
    before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as raised:
        _call_database_read(case, response_hook=hook)
    assert raised.value is error
    assert case.proxy._properties["_etag"] == "old"
    case.backend.execute.assert_called_once()
    case.connection.ReadDatabase.assert_not_called()
    assert hook.call_count == (1 if failure_source == "hook" else 0)
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("status", [403, 404, 408, 412, 429, 500])
def test_database_read_service_errors_never_replay(database_read_case, status):
    """An error status from the service surfaces as a typed error and is not retried
    on the other engine.

    Forbidden, not-found, request-timeout, precondition-failed, throttled, and
    server-error all raise with the status preserved, and not-found raises the
    specific not-found type customers catch to decide whether to create the
    database.

    The conditional header the caller asked for is still on the request that
    failed, the success hook does not fire, the engine was called once, and the
    legacy path was never touched. Replaying a rejected conditional read would
    risk it succeeding the second time under different conditions.
    """
    case = database_read_case
    case.backend.responses = [BackendResponse(
        status_code=status,
        headers=CaseInsensitiveDict({"x-ms-activity-id": "failed-read"}),
        body=b'{"message":"read failed"}',
    )]
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_database_read(case, etag="v1", match_condition=MatchConditions.IfNotModified, response_hook=hook)
    assert raised.value.status_code == status
    if status == 404:
        assert isinstance(raised.value, CosmosResourceNotFoundError)
    assert wire_headers(case.backend.prepared)["if-match"] == "v1"
    assert case.proxy._properties["_etag"] == "old"
    hook.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.ReadDatabase.assert_not_called()


def test_database_read_not_modified_preserves_empty_response_and_hook(database_read_case):
    """A not-modified reply is a success, not an error.

    When the customer's conditional read matches, the service replies with no
    body. The call returns an empty result that still carries the response
    headers, including the etag, so the customer can confirm which version they
    already hold.

    The hook fires with those headers and a body of ``None``, since there was no
    body to hand over, and it receives its own copy of the headers rather than
    the one attached to the result. The proxy adopts the empty result as its
    properties, and the legacy path is not involved.
    """
    case = database_read_case
    case.backend.responses = [BackendResponse(
        status_code=304,
        headers=CaseInsensitiveDict({"etag": "v1"}),
        body=b"",
    )]
    calls = []
    result = _call_database_read(
        case, etag="v1", match_condition=MatchConditions.IfModified,
        response_hook=lambda headers, body: calls.append((headers, body)),
    )
    assert result == {}
    assert result.get_response_headers()["etag"] == "v1"
    assert calls == [({"etag": "v1"}, None)]
    assert calls[0][0] is not result.get_response_headers()
    assert case.proxy._properties is result
    case.connection.ReadDatabase.assert_not_called()


def test_sync_helper_keeps_legacy_create_database_behind_boundary():
    """With no Rust backend (the core-python client) the coordinator runs the legacy
    ``CreateDatabase`` call directly, passing the database, options, and any extra
    kwargs straight through -- the legacy engine stays behind the same boundary."""
    connection = SimpleNamespace(
        CreateDatabase=MagicMock(return_value=CosmosDict(
            {"id": "db1"}, response_headers={"x-ms-request-charge": "4.0"},
        )),
        last_response_headers={"x-ms-request-charge": "4.0"},
    )
    hook_calls = []
    result = DatabaseHelper(connection, LEGACY_BACKEND).create_database(
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


def test_sync_create_database_rejects_per_call_read_timeout():
    """Create-database uses the configured backend and does not support overriding
    the client's read timeout for one call."""
    connection = SimpleNamespace(
        CreateDatabase=MagicMock(return_value={"id": "db1"}),
        last_response_headers={},
    )
    backend = _RustBackend()

    with pytest.raises(TypeError, match="does not support the 'read_timeout'"):
        DatabaseHelper(connection, backend).create_database(
            {"id": "db1"},
            {Constants.Kwargs.READ_TIMEOUT: 2},
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

    assert backend.prepared is None
    connection.CreateDatabase.assert_not_called()


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
    assert backend.prepared_requests[0].settings.throughput_bucket == 7
    assert backend.prepared_requests[1].settings.resource.offer_throughput == 400
    assert hook_calls == [
        (
            {"x-ms-request-charge": "5.25"},
            {"id": "db1", "_rid": "rid1"},
        )
    ]
    connection.ReadDatabase.assert_not_called()
    connection.CreateDatabase.assert_not_called()


def test_sync_if_not_exists_rust_create_race_reads_winning_database():
    """Return the winning caller's database after a creation conflict."""
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
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                body=b'{"id":"db1","_rid":"winner"}',
            ),
        ]
    )

    result = DatabaseHelper(connection, backend).create_database_if_not_exists(
        {"id": "db1"},
        {"offerThroughput": 400},
    )

    assert result["_rid"] == "winner"
    assert [request.op for request in backend.prepared_requests] == [
        OP_READ_DATABASE,
        OP_CREATE_DATABASE,
        OP_READ_DATABASE,
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
    properties = CosmosDict(
        {"id": "db1", "_rid": "existing"},
        response_headers={"x-ms-request-charge": "1.0"},
    )
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value=properties),
        CreateDatabase=MagicMock(),
        last_response_headers={"x-ms-request-charge": "1.0"},
    )

    result = DatabaseHelper(connection, LEGACY_BACKEND).create_database_if_not_exists(
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


def test_sync_if_not_exists_legacy_reads_winning_database_after_conflict():
    """The shared Python coordinator also recovers when using legacy transport."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(
            side_effect=[
                CosmosResourceNotFoundError(status_code=404, message="missing"),
                {"id": "db1", "_rid": "winner"},
            ]
        ),
        CreateDatabase=MagicMock(
            side_effect=CosmosResourceExistsError(status_code=409, message="race")
        ),
        last_response_headers={},
    )

    result = DatabaseHelper(connection, LEGACY_BACKEND).create_database_if_not_exists(
        {"id": "db1"},
        {"offerThroughput": 400},
    )

    assert result["_rid"] == "winner"
    assert connection.ReadDatabase.call_count == 2
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

    result = DatabaseHelper(connection, LEGACY_BACKEND).create_database_if_not_exists(
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


def test_async_helper_routes_to_rust():
    """Async twin of the Rust-route test: the create runs through the async backend
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
        assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '9'
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
        """Confirm the async read helper sends the read to the Rust engine and fires the hook with the returned database body."""
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
        assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '9'
        assert settings_options(backend.prepared)["timeout_seconds"] == 3.5
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
    """Choosing the async legacy helper explicitly still passes the internal timeout through."""
    async def run():
        """The explicitly selected legacy path fires the hook once."""
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
        result = await AsyncDatabaseHelper(connection, ASYNC_LEGACY_BACKEND).read_database(
            "db1",
            {Constants.Kwargs.READ_TIMEOUT: 2},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
            kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
        )

        assert result == {"id": "db1", "_rid": "legacy"}
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
def test_read_database_rejects_options_rust_cannot_honor(
    operation_kwargs,
):
    """Unsupported reads never cross from Rust to legacy transport."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "legacy"}),
        last_response_headers={},
    )
    backend = _RustBackend()

    with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
        DatabaseHelper(connection, backend).read_database(
            "db1", {}, kwargs=dict(operation_kwargs),
        )

    assert backend.prepared is None
    connection.ReadDatabase.assert_not_called()


def test_read_database_rejects_driver_owned_initial_header():
    """Driver-owned header overrides fail without a legacy request."""
    request_options = {"initialHeaders": {"Accept": "application/custom"}}
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "legacy"}),
        last_response_headers={},
    )
    backend = _RustBackend()

    with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
        DatabaseHelper(connection, backend).read_database("db1", request_options)

    assert backend.prepared is None
    connection.ReadDatabase.assert_not_called()


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
def test_async_read_database_rejects_options_rust_cannot_honor(
    operation_kwargs,
):
    """Async reads also reject unsupported calls without fallback."""
    async def run():
        """No backend receives an unsupported request."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "legacy"}),
            last_response_headers={},
        )
        backend = _AsyncRustBackend()

        with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
            await AsyncDatabaseHelper(connection, backend).read_database(
                "db1", {}, kwargs=dict(operation_kwargs),
            )

        assert backend.prepared is None
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_read_database_rejects_driver_owned_initial_header():
    """Async driver-owned header overrides fail without fallback."""
    async def run():
        """Neither transport should receive this unsupported call."""
        request_options = {"initialHeaders": {"x-ms-version": "2018-12-31"}}
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "legacy"}),
            last_response_headers={},
        )
        backend = _AsyncRustBackend()

        with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
            await AsyncDatabaseHelper(connection, backend).read_database("db1", request_options)

        assert backend.prepared is None
        connection.ReadDatabase.assert_not_awaited()

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
        assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '9'
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_database_proxy_read_rejects_deprecated_session_token():
    """The async proxy also rejects the obsolete token before any request is sent."""
    async def run():
        """No request is prepared for an obsolete option."""
        backend = _AsyncRustBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({}),
                body=b'{"id":"db1"}',
            )
        )
        connection = SimpleNamespace(_backend=backend, last_response_headers={})

        with pytest.raises(TypeError, match="session_token"):
            await AsyncDatabaseProxy(connection, "db1").read(session_token="ignored")

        assert backend.prepared is None

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
    """Async twin: with no Rust backend, the async coordinator awaits the legacy
    ``CreateDatabase`` call directly, passing database/options/extra kwargs through."""
    async def run():
        """Create via legacy-only path (no backend) and confirm the async ``CreateDatabase`` is awaited with correct args."""
        connection = SimpleNamespace(
            CreateDatabase=AsyncMock(return_value=CosmosDict(
                {"id": "db1"}, response_headers={"x-ms-request-charge": "4.0"},
            )),
            last_response_headers={"x-ms-request-charge": "4.0"},
        )
        hook_calls = []
        result = await AsyncDatabaseHelper(connection, ASYNC_LEGACY_BACKEND).create_database(
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


def test_async_create_database_rejects_per_call_read_timeout():
    """Async create-database does not support overriding the client's read timeout
    for one call."""
    async def run():
        """Confirm the unsupported option fails before either backend is invoked."""
        connection = SimpleNamespace(
            CreateDatabase=AsyncMock(return_value={"id": "db1"}),
            last_response_headers={"x-ms-request-charge": "4.25"},
        )
        backend = _AsyncRustBackend()
        hook_calls = []

        with pytest.raises(TypeError, match="does not support the 'read_timeout'"):
            await AsyncDatabaseHelper(connection, backend).create_database(
                {"id": "db1"},
                {Constants.Kwargs.READ_TIMEOUT: 2},
                response_hook=lambda headers, body: hook_calls.append((headers, body)),
                kwargs={Constants.Kwargs.READ_TIMEOUT: 2},
            )

        assert backend.prepared is None
        assert hook_calls == []
        connection.CreateDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_if_not_exists_legacy_reads_then_creates_only_on_404():
    """Async legacy path: the existence read returns 404, so it goes on to create, and
    ``response_hook`` fires once with the created database. The read leg drops the
    internal ``response_hook`` kwarg so the hook can't be invoked twice."""
    async def run():
        """Read returns 404 on the legacy async path, triggering a create; assert hook fires once with the created body."""
        properties = CosmosDict(
            {"id": "db1", "_rid": "created"},
            response_headers={"x-ms-request-charge": "5.0"},
        )
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(
                side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
            ),
            CreateDatabase=AsyncMock(return_value=properties),
            last_response_headers={"x-ms-request-charge": "5.0"},
        )
        hook_calls = []

        result = await AsyncDatabaseHelper(connection, ASYNC_LEGACY_BACKEND).create_database_if_not_exists(
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
    from azure.cosmos._helpers._item_context import ItemClientContext
    client._item_context = ItemClientContext(client._backend)
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
    from azure.cosmos._helpers._item_context import ItemClientContext
    client._item_context = ItemClientContext(backend)

    client.create_database(
        "db1",
        offer_throughput=ThroughputProperties(
            auto_scale_max_throughput=4000,
            auto_scale_increment_percent=0,
        ),
    )

    policy = json.loads(wire_headers(backend.prepared)["x-ms-cosmos-offer-autopilot-settings"])
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
        from azure.cosmos._helpers._item_context import ItemClientContext
        client._item_context = ItemClientContext(client._backend)
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
    from azure.cosmos._helpers._item_context import ItemClientContext
    sync_client._item_context = ItemClientContext(sync_backend)

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
        async_client._item_context = ItemClientContext(async_backend)
        async_proxy, async_properties = await async_client.create_database_if_not_exists(
            "db1",
            return_properties=True,
        )
        assert async_proxy.id == "db1"
        assert async_properties["_rid"] == "existing"
        assert async_backend.prepared.op == OP_READ_DATABASE

    asyncio.run(run())


@pytest.fixture(params=[False, True], ids=["sync", "aio"])
def create_database_client(request):
    """Build a real client object wired to a fake Rust engine, once sync and once
    async.

    The client is created without running its constructor, so no account or
    credentials are needed. Its legacy connection is deliberately booby-trapped:
    both ``CreateDatabase`` and ``ReadDatabase`` raise if they are ever called.
    That turns any accidental fall back to the legacy path into a loud failure
    rather than a test that quietly passes for the wrong reason.
    """
    client_type = AsyncCosmosClient if request.param else CosmosClient
    client = object.__new__(client_type)
    client.client_connection = SimpleNamespace(
        last_response_headers={},
        CreateDatabase=MagicMock(side_effect=AssertionError("legacy create called")),
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
    )
    client._backend = _AsyncRustBackend() if request.param else _RustBackend()
    from azure.cosmos._helpers._item_context import ItemClientContext
    client._item_context = ItemClientContext(client._backend)
    return client


def _call_create_database(client, *args, method_name="create_database", **kwargs):
    """Call a create method on the client and wait for it if the client is async.

    ``method_name`` lets the same helper drive either ``create_database`` or
    ``create_database_if_not_exists``.
    """
    result = getattr(client, method_name)(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("options", [
    {"connection_timeout": 1}, {"raw_request_hook": lambda request: None},
    {"raw_response_hook": lambda response: None}, {"misspelled_setting": None},
    {"no_response": True}, {"max_item_count": 5}, {"retry_write": True},
    {"request_options": {"sessionToken": "unused"}},
    {"request_options": {"populateQueryMetrics": False}},
    {"request_options": {"operationStartTime": 123}},
    {"request_options": {"maxItemCount": 1}},
    *[{"initial_headers": {name: "unused"}} for name in (
        "Accept", "Cache-Control", "User-Agent", "X-MS-VERSION",
        "x-ms-client-id", "x-ms-cosmos-sdk-supportedcapabilities",
        "authorization", "x-ms-date", "if-match", "x-ms-session-token",
        "x-ms-documentdb-populatequerymetrics", "prefer",
    )],
])
def test_create_rejects_unhonored_options_without_dispatch(create_database_client, options):
    """Anything the Rust engine cannot honor exactly stops the call before a request
    is built.

    Three kinds of input are covered. First, options with no Rust equivalent: a
    socket-level connect timeout, the raw request and response hooks, a
    misspelled keyword, and paging or write-retry settings that do not apply to
    creating a database. Second, the same retired settings passed the back way
    in, nested inside a raw request-options dictionary, so the check cannot be
    bypassed by burying them. Third, twelve headers the driver owns outright,
    covering authentication, the API version, the client identity, and
    conditional and session headers.

    Each raises ``NotImplementedError`` naming ``create_database``. Nothing is
    prepared and the legacy create is never called, so a customer is told their
    option is unsupported instead of watching it be dropped.
    """
    client = create_database_client
    with pytest.raises(NotImplementedError, match="create_database"):
        _call_create_database(client, "db1", **options)
    assert not client._backend.prepared_requests
    client.client_connection.CreateDatabase.assert_not_called()


@pytest.mark.parametrize("timeout", [0.25, 0, -1, True, "5", float("nan"), float("inf"), 2**64])
@pytest.mark.parametrize("nested", [False, True])
def test_create_rejects_invalid_timeout_before_dispatch(create_database_client, timeout, nested):
    """An unusable timeout is a ``ValueError`` before any request is prepared,
    whether it is passed directly or nested in a raw request-options dictionary.

    A value under one second, zero, a negative, a boolean, a string, the two
    non-finite floats, and a value past the range the engine can hold are all
    refused. Both entry points are tested because a customer can supply the
    deadline either way and the two must agree.
    """
    options = {"request_options": {"timeout": timeout}} if nested else {"timeout": timeout}
    with pytest.raises(ValueError, match="timeout"):
        _call_create_database(create_database_client, "db1", **options)
    assert not create_database_client._backend.prepared_requests


@pytest.mark.parametrize("throughput", [
    ThroughputProperties(offer_throughput=400, auto_scale_max_throughput=4000),
    ThroughputProperties(offer_throughput=0, auto_scale_max_throughput=4000),
    ThroughputProperties(auto_scale_increment_percent=0),
    ThroughputProperties(auto_scale_increment_percent=10),
    ThroughputProperties(),
])
def test_create_rejects_invalid_throughput_choice(create_database_client, throughput):
    """A throughput setting that does not describe one clear choice is refused.

    A database is either at fixed throughput or autoscale, never both, so asking
    for a fixed amount and an autoscale ceiling together is an error -- including
    when the fixed amount is zero, which is still a stated fixed choice rather
    than an absence. An autoscale growth percentage with no ceiling to grow
    toward, and a completely empty throughput object, are equally unusable.

    Guessing which half the customer meant could create a database that bills
    differently from what they asked for, so the call raises instead and nothing
    is prepared.
    """
    with pytest.raises(ValueError):
        _call_create_database(create_database_client, "db1", offer_throughput=throughput)
    assert not create_database_client._backend.prepared_requests


@pytest.mark.parametrize("options", [
    {"request_options": {"offerThroughput": 400, "autoUpgradePolicy": '{"maxThroughput":4000}'}},
    {"offer_throughput": 400, "initial_headers": {
        "x-ms-cosmos-offer-autopilot-settings": '{"maxThroughput":4000}',
    }},
    {"initial_headers": {
        "x-ms-offer-throughput": "400",
        "x-ms-cosmos-offer-autopilot-settings": '{"maxThroughput":4000}',
    }},
])
def test_create_rejects_mixed_throughput_across_input_routes(create_database_client, options):
    """Conflicting throughput is caught even when the two halves arrive by different
    routes.

    There are three ways to ask for throughput: the ``offer_throughput``
    argument, a raw request-options dictionary, and raw headers. A customer can
    mix them, so the conflict check cannot look at only one. Here fixed and
    autoscale are combined through nested options, through the argument plus a
    header, and through two headers.

    All three raise ``ValueError`` saying not both, and nothing is prepared.
    """
    with pytest.raises(ValueError, match="not both"):
        _call_create_database(create_database_client, "db1", **options)
    assert not create_database_client._backend.prepared_requests


def test_create_snapshots_options_and_does_not_leak_throughput(create_database_client):
    """The caller's options dictionary is read, never written to, and never carried
    over into the next call.

    The same dictionary is reused for two creates, one asking for throughput and
    one not. Afterwards it is byte-for-byte what the customer passed in: no
    internal bookkeeping such as a start timestamp was written into it.

    The first request carries the throughput header and the second does not, so
    a value from an earlier call cannot leak into a later one and silently bill
    a customer for capacity they did not ask for the second time.

    Finally, editing the dictionary after the fact does not change the request
    that was already built, confirming the values were copied rather than
    referenced.
    """
    from copy import deepcopy
    client = create_database_client
    options = {"initialHeaders": {"x-trace-id": "original"}}
    original = deepcopy(options)
    _call_create_database(client, "db1", request_options=options, offer_throughput=400)
    _call_create_database(client, "db1", request_options=options)
    assert options == original
    first, second = client._backend.prepared_requests
    assert wire_headers(first)["x-ms-offer-throughput"] == "400"
    assert "x-ms-offer-throughput" not in wire_headers(second)
    assert "operationStartTime" not in options
    options["initialHeaders"]["x-trace-id"] = "later"
    assert wire_headers(first)["x-trace-id"] == "original"


def test_create_explicit_throughput_replaces_nested_mode(create_database_client):
    """The explicit ``offer_throughput`` argument wins over an autoscale setting
    buried in raw options, and the autoscale header is dropped rather than sent
    alongside it. Sending both would leave the service to decide which one
    applies.
    """
    _call_create_database(create_database_client, "db1", offer_throughput=400,
                          request_options={"autoUpgradePolicy": '{"maxThroughput":4000}'})
    headers = wire_headers(create_database_client._backend.prepared)
    assert headers["x-ms-offer-throughput"] == "400"
    assert "x-ms-cosmos-offer-autopilot-settings" not in headers


def test_create_hook_owns_headers_and_nested_body(create_database_client):
    """What the response hook receives is its own to modify, all the way down.

    The hook here reports itself as false when tested as a boolean but is still
    callable, so it must still run. It then edits everything it was handed: the
    headers, a top-level field, a field nested one level deeper, and the headers
    hanging off the properties object.

    None of those edits reach the caller's result or the client's own record of
    the last response. The nested edit is the important one: a shallow copy
    would have let it through. A customer whose logging hook happens to modify
    what it logs must not thereby change the object returned to their own code.
    """
    client = create_database_client
    client._backend.responses = [BackendResponse(
        status_code=201, headers={"x-ms-activity-id": "own"},
        body=b'{"id":"db1","nested":{"value":"original"}}',
    )]
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, properties):
            calls.append((dict(headers), dict(properties)))
            headers["x-ms-activity-id"] = "edited"
            properties["id"] = "edited"
            properties["nested"]["value"] = "edited"
            properties.get_response_headers()["x-ms-activity-id"] = "edited"

    proxy, result = _call_create_database(client, "db1", return_properties=True, response_hook=Hook())
    assert len(calls) == 1
    assert proxy.id == "db1"
    assert result["nested"]["value"] == "original"
    assert result.get_response_headers()["x-ms-activity-id"] == "own"
    assert client._item_context.response_state.last_response_headers["x-ms-activity-id"] == "own"


def test_create_hook_uses_result_not_latest_client_headers(create_database_client, monkeypatch):
    """The hook reports the headers from its own call, not whatever the client saw
    most recently.

    Response parsing is wrapped so that another request appears to land in
    between parsing and the hook firing, overwriting the client's shared record
    with a different request charge. The hook still receives the charge from the
    call it belongs to.

    This is what makes the hook usable for per-call cost tracking on a client
    shared across threads or tasks; reading a shared field instead would
    attribute one caller's charge to another.
    """
    from azure.cosmos._helpers import _database_operations as sync_helper
    from azure.cosmos.aio._helpers import _database_operations as async_helper
    client = create_database_client
    module = async_helper if isinstance(client, AsyncCosmosClient) else sync_helper
    original = module.process_backend_response

    def parse_with_interleaved_response(*args, **kwargs):
        result = original(*args, **kwargs)
        client.client_connection.last_response_headers = {"x-ms-request-charge": "99"}
        client._item_context.response_state.last_response_headers = CaseInsensitiveDict(
            {"x-ms-request-charge": "99"}
        )
        return result

    monkeypatch.setattr(module, "process_backend_response", parse_with_interleaved_response)
    calls = []
    _call_create_database(client, "db1", response_hook=lambda headers, body: calls.append(headers))
    assert calls[0]["x-ms-request-charge"] == "5.25"


@pytest.mark.parametrize("hook", [False, "invalid", 0])
def test_create_validates_hook_before_dispatch(create_database_client, hook):
    """A ``response_hook`` that is not callable is a ``TypeError`` before the
    database is created.

    The values tried are all falsey, which is the trap: a check that simply
    tested the hook for truth would treat them as absent and create the database
    anyway, leaving the customer with a new resource and no notification. Here
    nothing is prepared.
    """
    with pytest.raises(TypeError, match="response_hook"):
        _call_create_database(create_database_client, "db1", response_hook=hook)
    assert not create_database_client._backend.prepared_requests


def test_create_hook_error_is_not_retried_or_reclassified(create_database_client):
    """An error raised by the customer's hook reaches them unchanged and does not
    cause a second create.

    The hook raises a timeout error, which is exactly the type the SDK's own
    retry logic would be tempted to act on. The same exception object comes back
    out, only one request was made, and the legacy path was not tried. Retrying
    here would create a second database, because the first create already
    succeeded -- the failure was in the callback, after the fact.
    """
    failure = TimeoutError("customer callback failed")

    def hook(headers, body):
        raise failure

    with pytest.raises(TimeoutError) as caught:
        _call_create_database(create_database_client, "db1", timeout=5, response_hook=hook)
    assert caught.value is failure
    assert len(create_database_client._backend.prepared_requests) == 1
    create_database_client.client_connection.CreateDatabase.assert_not_called()


def test_create_passes_one_deadline_and_honors_nested_timeout(create_database_client, monkeypatch):
    """A timeout given in raw options becomes one absolute deadline, computed once.

    The clock is pinned so the arithmetic is exact: a 3.5 second budget starting
    at 10 produces a deadline of 13.5 handed to the engine, and the original 3.5
    still travels with the request as the per-request limit.

    Recomputing the deadline at each layer instead would let a slow step restart
    the customer's budget, so a call given 3.5 seconds could run considerably
    longer.
    """
    from azure.cosmos._helpers import _request_database
    client = create_database_client
    clock = [10.0]
    monkeypatch.setattr(_request_database.time, "monotonic", lambda: clock[0])
    execute = client._backend.execute
    observed = []

    def sync_execute(prepared, *, deadline=None):
        observed.append(deadline)
        return execute(prepared, deadline=deadline)

    async def async_execute(prepared, *, deadline=None):
        observed.append(deadline)
        return await execute(prepared, deadline=deadline)

    client._backend.execute = async_execute if isinstance(client, AsyncCosmosClient) else sync_execute
    _call_create_database(client, "db1", request_options={"timeout": 3.5})
    assert observed == [13.5]
    assert settings_options(client._backend.prepared)["timeout_seconds"] == 3.5


@pytest.mark.parametrize("setup_seconds", [0.75, 1.25])
def test_create_driver_setup_consumes_budget(create_database_client, monkeypatch, setup_seconds):
    """Time spent starting the driver counts against the customer's timeout.

    The customer allows one second. Preparing the driver is made to burn part of
    that budget while the clock is pinned so the outcome is exact.

    When setup takes three quarters of a second, the request still goes out and
    the driver is given the quarter second that remains, not a fresh second.
    When setup takes longer than the whole budget, a client timeout error is
    raised, the driver is never called, and the hook never fires.

    Without this, a one second timeout could take two seconds or more: one spent
    on setup and the full second again on the request.
    """
    from azure.cosmos._backend import binding as sync_rust
    from azure.cosmos.aio._backend import binding as async_rust
    from azure.cosmos._helpers import _request_database
    from azure.cosmos.exceptions import CosmosClientTimeoutError
    client = create_database_client
    is_async = isinstance(client, AsyncCosmosClient)
    clock = [100.0]
    monkeypatch.setattr(_request_database.time, "monotonic", lambda: clock[0])
    response = (201, 0, {}, b'{"id":"db1"}', None)
    binding = AsyncMock(return_value=response) if is_async else MagicMock(return_value=response)
    module = async_rust if is_async else sync_rust
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(
        create_database=binding, create_database_async=binding,
    ))

    def setup():
        clock[0] += setup_seconds
        return "fake-handle"

    backend = client._backend
    backend._ensure_driver_handle = AsyncMock(side_effect=setup) if is_async else setup
    if is_async:
        async def execute(prepared, *, deadline=None):
            return await async_rust.AsyncRustBinding.execute(backend, prepared, deadline=deadline)
    else:
        def execute(prepared, *, deadline=None):
            return sync_rust.RustBinding.execute(backend, prepared, deadline=deadline)
    backend.execute = execute
    hook = MagicMock()
    if setup_seconds > 1:
        with pytest.raises(CosmosClientTimeoutError):
            _call_create_database(client, "db1", timeout=1, response_hook=hook)
        binding.assert_not_called()
        hook.assert_not_called()
    else:
        _call_create_database(client, "db1", timeout=1, response_hook=hook)
        assert binding.call_args.kwargs["timeout_seconds"] == pytest.approx(0.25)
        hook.assert_called_once()


def test_create_async_timeout_drains_pending_work():
    """When an async create times out, the work already in flight is cancelled and
    waited on before the error is raised.

    The engine is made to hang forever. The deadline passes, a client timeout
    error is raised, and the hanging task is confirmed cancelled rather than
    left running. The success hook does not fire, since nothing succeeded.

    Abandoning the task instead would leak it for the life of the event loop and
    produce warnings about a task that was never retrieved.
    """
    from azure.cosmos.exceptions import CosmosClientTimeoutError
    import time

    async def run():
        cancelled = asyncio.Event()
        backend = _AsyncRustBackend()

        async def execute(prepared, *, deadline=None):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        backend.execute = execute
        hook = MagicMock()
        with pytest.raises(CosmosClientTimeoutError):
            await AsyncDatabaseHelper(SimpleNamespace(), backend).create_database(
                {"id": "db1"}, {}, response_hook=hook, deadline=time.monotonic() + 0.01,
            )
        assert cancelled.is_set()
        hook.assert_not_called()

    asyncio.run(run())


@pytest.mark.parametrize("name", ["create_database", "create_database_async"])
@pytest.mark.parametrize("remaining", [0.125, 1.0])
def test_create_native_binding_accepts_remaining_budget(name, remaining):
    """The native create entry points, sync and async, accept a prepared request plus
    whatever time is left, and get as far as looking for the driver.

    The handle passed in was never registered, so the expected outcome is a
    driver error. That failure is the proof: the call was accepted and rejected
    on the missing driver, not on the shape of its arguments. If the remaining
    budget were the wrong type or in the wrong units the call would have failed
    earlier and differently.
    """
    from azure.cosmos import _rust
    prepared = build_create_database_prepared({"id": "db1"}, {})
    with pytest.raises(RuntimeError, match="(?i)driver"):
        getattr(_rust, name)("unregistered-create-test-handle", prepared, timeout_seconds=remaining)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_create_boolean_overload_preserves_literal_overloads(client_type):
    """``create_database`` keeps its three declared forms in order: asking for
    properties as a constant false, as a constant true, and as a plain boolean.

    That ordering is what lets a type checker tell a customer writing
    ``return_properties=True`` that they get a proxy and properties, and a
    customer writing ``False`` that they get only a proxy. Collapsing or
    reordering the declarations would leave them with an unhelpful union and no
    warning when they unpack the result wrongly.

    Runtime inspection of these declarations needs Python 3.11, so the test
    skips on older versions.
    """
    import typing
    from typing import Literal, get_type_hints
    if not hasattr(typing, "get_overloads"):
        pytest.skip("Runtime overload inspection requires Python 3.11 or later.")
    variants = typing.get_overloads(client_type.create_database)
    assert [
        get_type_hints(variant, localns={"ThroughputProperties": ThroughputProperties})["return_properties"]
        for variant in variants
    ] == [
        Literal[False], Literal[True], bool,
    ]


@pytest.mark.parametrize("is_async", [False, True])
def test_create_explicit_legacy_preserves_pipeline_and_isolates_hook(is_async):
    """On the legacy path the transport settings still reach the old call, and the
    hook is still handed its own copy.

    A customer who deliberately stays on the legacy client keeps the features
    only that path offers, so a socket-level connect timeout must arrive at the
    old create call untouched.

    At the same time the hook protection is identical to the Rust path: the hook
    edits its headers and a nested field of the body, and neither edit shows up
    in the result. The two paths must not differ in how safe a hook is to write.
    """
    response = CosmosDict(
        {"id": "db1", "nested": {"value": "original"}},
        response_headers={"x-ms-activity-id": "own"},
    )
    call = AsyncMock(return_value=response) if is_async else MagicMock(return_value=response)
    connection = SimpleNamespace(CreateDatabase=call, last_response_headers={"x-ms-activity-id": "other"})
    helper = (AsyncDatabaseHelper(connection, ASYNC_LEGACY_BACKEND) if is_async
              else DatabaseHelper(connection, LEGACY_BACKEND))

    def hook(headers, body):
        assert headers["x-ms-activity-id"] == "own"
        headers["x-ms-activity-id"] = "edited"
        body["nested"]["value"] = "edited"

    result = helper.create_database(
        {"id": "db1"}, {}, response_hook=hook, kwargs={"connection_timeout": 2},
    )
    if is_async:
        result = asyncio.run(result)
    assert result["nested"]["value"] == "original"
    assert result.get_response_headers()["x-ms-activity-id"] == "own"
    assert call.call_args.kwargs["connection_timeout"] == 2


@pytest.mark.parametrize("option", ["populate_query_metrics", "session_token", "etag", "match_condition"])
@pytest.mark.parametrize("value", [None, False, True, "value"])
@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
def test_create_database_rejects_inapplicable_options(create_database_client, option, value, method_name):
    """Options that mean nothing when creating a database are refused by both create
    methods, whatever value they carry.

    Query metrics and session token are retired. An etag or match condition
    cannot apply either: there is no existing version to compare against when
    creating something new, and on the get-or-create method allowing them would
    make the read leg behave conditionally while the create leg ignored them.

    Each raises ``TypeError`` naming the option in quotes, including for ``None``
    and ``False``. Nothing is prepared, neither legacy call runs, and the hook
    does not fire.
    """
    client = create_database_client
    hook = MagicMock()

    with pytest.raises(TypeError, match=f"'{option}'"):
        _call_create_database(client, "db1", method_name=method_name, response_hook=hook, **{option: value})

    assert client._backend.prepared_requests == []
    client.client_connection.CreateDatabase.assert_not_called()
    client.client_connection.ReadDatabase.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize(
    "args, kwargs",
    [
        (("db1", False, 400), {}),
        (("db1", None, 400), {}),
        (("db1", 400), {}),
        ((), {}),
        (("db1",), {"id": "other"}),
    ],
)
@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
def test_create_database_rejects_invalid_argument_binding(create_database_client, args, kwargs, method_name):
    """Arguments that do not match the signature fail as ``TypeError`` before
    anything is created.

    The cases are a customer writing positionally as if the old signature still
    applied, passing throughput as the second positional argument, omitting the
    required id entirely, and passing the id both positionally and by keyword.

    Both create methods are covered. Accepting any of these would risk creating
    a database with the wrong name or the wrong capacity, so nothing is prepared
    and no legacy call is made.
    """
    client = create_database_client
    with pytest.raises(TypeError):
        _call_create_database(client, *args, method_name=method_name, **kwargs)
    assert client._backend.prepared_requests == []
    client.client_connection.CreateDatabase.assert_not_called()
    client.client_connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("keyword_id", [False, True])
@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("throughput", [None, 400, ThroughputProperties(auto_scale_max_throughput=4000)])
@pytest.mark.parametrize("workflow", ["create", "existing", "missing", "race"])
def test_create_database_preserves_supported_settings(
    create_database_client, keyword_id, return_properties, throughput, workflow
):
    """The broadest test in the file: every supported option survives, across all
    four ways these calls can play out.

    The four workflows are a plain create; get-or-create finding the database
    already there; get-or-create finding nothing and creating it; and the race,
    where the create loses to another caller and a final read fetches the
    winner. Each is checked to make exactly the requests it should, in order:
    one, one, two, and three.

    Across all of them the customer's own header, the throughput bucket, and the
    per-call deadline reach the request; the id works positionally or by
    keyword; and asking for properties returns them alongside the proxy while
    not asking returns the proxy alone.

    The throughput rules are the subtle part. Throughput describes a database
    being created, so it must appear only on a create request. It is absent from
    every read, and absent altogether when the database already existed or when
    another caller won the race -- in both cases this caller created nothing and
    must not be billed as though they had. In the race the final read is checked
    to carry the same headers as the first read, while the create leg in the
    middle keeps its throughput.

    The hook fires exactly once with the final response, and neither legacy call
    is ever reached.
    """
    client = create_database_client
    method_name = "create_database" if workflow == "create" else "create_database_if_not_exists"
    if workflow in ("missing", "race"):
        client._backend.responses = [
            BackendResponse(
                status_code=404,
                headers=CaseInsensitiveDict({}),
                body=b'{"code":"NotFound","message":"missing"}',
            ),
            _created_response(),
        ]
        if workflow == "race":
            client._backend.responses.insert(
                1,
                BackendResponse(
                    status_code=409,
                    headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
                    body=b'{"code":"Conflict","message":"another caller created db1"}',
                ),
            )
            client._backend.responses[-1] = BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
                body=b'{"id":"db1","_rid":"rid1"}',
            )
    elif workflow == "existing":
        client._backend.responses = [
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
                body=b'{"id":"db1","_rid":"rid1"}',
            )
        ]
    hook = MagicMock()
    kwargs = {
        "offer_throughput": throughput,
        "return_properties": return_properties,
        "response_hook": hook,
        "initial_headers": {"x-custom": "value"},
        "throughput_bucket": 9,
        "timeout": 3.5,
    }
    args = () if keyword_id else ("db1",)
    if keyword_id:
        kwargs["id"] = "db1"

    result = _call_create_database(client, *args, method_name=method_name, **kwargs)

    proxy_type = AsyncDatabaseProxy if isinstance(client, AsyncCosmosClient) else DatabaseProxy
    if return_properties:
        proxy, properties = result
        assert isinstance(properties, CosmosDict)
        assert properties == {"id": "db1", "_rid": "rid1"}
    else:
        proxy = result
    assert isinstance(proxy, proxy_type)
    assert proxy.id == "db1"
    headers = wire_headers(client._backend.prepared)
    assert all(headers.get(key.lower()) == str(value) for key, value in ({"x-custom": "value"}).items())
    assert headers["x-ms-cosmos-throughput-bucket"] == '9'
    assert settings_options(client._backend.prepared)["timeout_seconds"] == 3.5
    if throughput is None or workflow in ("existing", "race"):
        assert "offerThroughput" not in headers
        assert "autoUpgradePolicy" not in headers
    elif isinstance(throughput, int):
        assert headers["x-ms-offer-throughput"] == str(throughput)
    else:
        assert json.loads(headers["x-ms-cosmos-offer-autopilot-settings"])["maxThroughput"] == 4000
    hook.assert_called_once_with(
        {"x-ms-request-charge": "5.25"}, {"id": "db1", "_rid": "rid1"}
    )
    client.client_connection.CreateDatabase.assert_not_called()
    client.client_connection.ReadDatabase.assert_not_called()
    expected_operations = {
        "create": [OP_CREATE_DATABASE],
        "existing": [OP_READ_DATABASE],
        "missing": [OP_READ_DATABASE, OP_CREATE_DATABASE],
        "race": [OP_READ_DATABASE, OP_CREATE_DATABASE, OP_READ_DATABASE],
    }
    assert [p.op for p in client._backend.prepared_requests] == expected_operations[workflow]
    if workflow != "create":
        read_headers = wire_headers(client._backend.prepared_requests[0])
        assert "offerThroughput" not in read_headers
        assert "autoUpgradePolicy" not in read_headers
    if workflow == "race":
        assert headers == read_headers
        create_headers = wire_headers(client._backend.prepared_requests[1])
        if isinstance(throughput, int):
            assert create_headers["x-ms-offer-throughput"] == str(throughput)
        elif throughput is not None:
            assert json.loads(create_headers["x-ms-cosmos-offer-autopilot-settings"])["maxThroughput"] == 4000


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
def test_create_database_signature_is_keyword_only_after_id(client_type, method_name):
    """Both create methods take the database id positionally and require everything
    else by name.

    The id is required with no default, throughput must be passed by name, and
    neither method accepts extra positional arguments. Keeping the shape fixed
    means a customer cannot pass throughput positionally and have it silently
    land on some other argument, and it leaves room to add options later without
    changing what existing positional calls mean.
    """
    parameters = inspect.signature(getattr(client_type, method_name)).parameters
    assert parameters["id"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["id"].default is inspect.Parameter.empty
    assert parameters["offer_throughput"].kind == inspect.Parameter.KEYWORD_ONLY
    assert not any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in parameters.values())


def test_if_not_exists_unsupported_option_does_not_recommend_legacy(create_database_client):
    """The error for an unsupported option tells the customer how to fix it, in their
    own terms.

    The message names the offending option and points at how the client was
    constructed, which is the thing they can actually change. It does not
    mention the internal backend name, which would mean nothing to them and
    would leak an implementation detail into a public error message.

    Nothing is prepared and neither leg of the workflow runs.
    """
    client = create_database_client
    with pytest.raises(NotImplementedError) as error:
        _call_create_database(
            client, "db1", method_name="create_database_if_not_exists", read_timeout=1
        )
    message = str(error.value)
    assert "read_timeout" in message
    assert "constructing CosmosClient" in message
    assert "core-python" not in message
    assert client._backend.prepared_requests == []
    client.client_connection.ReadDatabase.assert_not_called()
    client.client_connection.CreateDatabase.assert_not_called()


@pytest.mark.parametrize(
    "statuses",
    [
        [409],
        [403],
        [404, 403],
        [404, 500],
        [404, 409, 404],
        [404, 409, 403],
        [404, 409, 409],
        [404, 409, 500],
    ],
)
def test_if_not_exists_recovery_is_bounded_and_preserves_errors(create_database_client, statuses):
    """Get-or-create gives up after at most three requests and reports the last real
    failure.

    The workflow is read, then create if the read found nothing, then one final
    read if the create hit a conflict. The cases here stop it at each point: a
    conflict on the first read, a forbidden read, a read that finds nothing
    followed by a failing create, and a full three-step sequence ending in a
    second not-found, a forbidden, another conflict, or a server error.

    In every case the request sequence is a prefix of read, create, read -- never
    a fourth attempt. A loop retrying until success could spin indefinitely
    against a database being repeatedly created and deleted.

    The error raised carries the status and message of the last step, not the
    first, so the customer sees what actually stopped the call. The client's
    recorded activity id matches that same step, and the success hook does not
    fire.
    """
    client = create_database_client
    client._backend.responses = [
        BackendResponse(
            status_code=status,
            headers=CaseInsensitiveDict({"x-ms-activity-id": f"step-{index}"}),
            body=json.dumps({"message": f"failure-{index}"}).encode(),
        )
        for index, status in enumerate(statuses)
    ]
    hook = MagicMock()

    with pytest.raises(CosmosHttpResponseError) as error:
        _call_create_database(
            client, "db1", method_name="create_database_if_not_exists", response_hook=hook
        )

    assert error.value.status_code == statuses[-1]
    assert f"failure-{len(statuses) - 1}" in str(error.value)
    assert [p.op for p in client._backend.prepared_requests] == [
        OP_READ_DATABASE, OP_CREATE_DATABASE, OP_READ_DATABASE
    ][:len(statuses)]
    assert client._item_context.response_state.last_response_headers["x-ms-activity-id"] == f"step-{len(statuses) - 1}"
    hook.assert_not_called()
    client.client_connection.ReadDatabase.assert_not_called()
    client.client_connection.CreateDatabase.assert_not_called()


@pytest.mark.parametrize("failure_type", [ServiceRequestError, asyncio.CancelledError])
def test_if_not_exists_follow_up_read_preserves_transport_error_or_cancellation(
    create_database_client, failure_type
):
    """If the final read is interrupted, the interruption itself is what the customer
    sees.

    The workflow reaches its third step -- read found nothing, create hit a
    conflict, so another caller owns the database -- and that last read then
    fails, either with a transport error or with cancellation.

    The original exception object comes back untouched. Cancellation especially
    must not be swallowed or converted: turning it into an ordinary error would
    stop it unwinding and leave a cancelled task looking like a failed request.

    All three steps ran in order, nothing was retried, and the success hook did
    not fire.
    """
    client = create_database_client
    failure = failure_type("follow-up interrupted")
    responses = [
        BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'),
        BackendResponse(status_code=409, headers={}, body=b'{"message":"exists"}'),
        failure,
    ]
    mock_type = AsyncMock if isinstance(client, AsyncCosmosClient) else MagicMock
    execute = mock_type(side_effect=responses)
    client._backend.execute = execute
    hook = MagicMock()

    with pytest.raises(failure_type) as error:
        _call_create_database(
            client, "db1", method_name="create_database_if_not_exists", response_hook=hook
        )

    assert error.value is failure
    assert [call.args[0].op for call in execute.call_args_list] == [
        OP_READ_DATABASE, OP_CREATE_DATABASE, OP_READ_DATABASE
    ]
    hook.assert_not_called()
    client.client_connection.ReadDatabase.assert_not_called()
    client.client_connection.CreateDatabase.assert_not_called()


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_public_create_database_does_not_select_backend(client_type):
    """The public ``create_database`` (sync and async) must not name an engine: its
    source mentions no Rust backend, no eligibility check, and no direct legacy call.
    That keeps engine selection entirely behind the coordinator, so the public method
    stays a thin delegate."""
    source = inspect.getsource(client_type.create_database)
    assert "RustBinding" not in source
    assert "can_use_rust" not in source
    assert "CreateDatabase(" not in source


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_public_create_database_if_not_exists_does_not_orchestrate_backends(client_type):
    """The public ``create_database_if_not_exists`` (sync and async) must stay a thin
    delegate: its source names no Rust backend and makes no direct ReadDatabase or
    CreateDatabase call, so the read-then-create and the engine choice live entirely in
    the coordinator."""
    source = inspect.getsource(client_type.create_database_if_not_exists)
    assert "RustBinding" not in source
    assert "ReadDatabase(" not in source
    assert "CreateDatabase(" not in source


# ---------------------------------------------------------------------------
# Async create_database_if_not_exists coverage
# ---------------------------------------------------------------------------


def test_async_if_not_exists_uses_python_coordinator_with_rust_selected():
    """Async twin: the database already exists, so the read is the only request
    sent and no legacy call is made."""
    async def run():
        """Read an existing database via the async coordinator and confirm only a Rust read is sent."""
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
        assert backend.prepared_requests[0].settings.throughput_bucket == 7
        assert backend.prepared_requests[1].settings.resource.offer_throughput == 400
        assert hook_calls == [
            (
                {"x-ms-request-charge": "5.25"},
                {"id": "db1", "_rid": "rid1"},
            )
        ]
        connection.ReadDatabase.assert_not_awaited()
        connection.CreateDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_if_not_exists_rust_create_race_reads_winning_database():
    """Async twin: a creation conflict is followed by one read."""
    async def run():
        """Return the winning database without invoking legacy transport."""
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
                BackendResponse(
                    status_code=200,
                    headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                    body=b'{"id":"db1","_rid":"winner"}',
                ),
            ]
        )

        result = await AsyncDatabaseHelper(
            connection,
            backend,
        ).create_database_if_not_exists(
            {"id": "db1"},
            {"offerThroughput": 400},
        )

        assert result["_rid"] == "winner"
        assert [request.op for request in backend.prepared_requests] == [
            OP_READ_DATABASE,
            OP_CREATE_DATABASE,
            OP_READ_DATABASE,
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
        properties = CosmosDict(
            {"id": "db1", "_rid": "existing"},
            response_headers={"x-ms-request-charge": "1.0"},
        )
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value=properties),
            CreateDatabase=AsyncMock(),
            last_response_headers={"x-ms-request-charge": "1.0"},
        )

        result = await AsyncDatabaseHelper(connection, ASYNC_LEGACY_BACKEND).create_database_if_not_exists(
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
            ASYNC_LEGACY_BACKEND,
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
    without ever attempting the create. Recovery from a creation conflict is a
    separate concern; this locks in that only 404 triggers create."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(
            side_effect=CosmosResourceExistsError(status_code=409, message="conflict")
        ),
        CreateDatabase=MagicMock(),
        last_response_headers={},
    )

    with pytest.raises(CosmosResourceExistsError):
        DatabaseHelper(connection, LEGACY_BACKEND).create_database_if_not_exists(
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
            await AsyncDatabaseHelper(connection, ASYNC_LEGACY_BACKEND).create_database_if_not_exists(
                {"id": "db1"},
                {"offerThroughput": 400},
            )

        connection.CreateDatabase.assert_not_awaited()

    asyncio.run(run())


# ---------------------------------------------------------------------------
# Additional get-or-create rules
# ---------------------------------------------------------------------------


def _get_or_create_responses(statuses):
    """Build canned replies for a get-or-create run, one per status given.

    Successful steps carry a database body with a nested field, so a test can
    prove a hook's edit did not reach a value one level down. Failing steps
    carry a message instead. Every step is tagged with its own activity id and a
    request charge that counts up, which is what lets a test say which step a
    given header came from.
    """
    return [
        BackendResponse(
            status_code=status,
            headers={"x-ms-activity-id": f"step-{index}", "x-ms-request-charge": str(index + 1)},
            body=json.dumps(
                {"id": "db1", "nested": {"value": "original"}} if status < 400
                else {"message": f"failure-{index}"}
            ).encode(),
        )
        for index, status in enumerate(statuses)
    ]


@pytest.mark.parametrize("options,error", [
    ({"timeout": 0.5}, ValueError),
    ({"request_options": {"timeout": True}}, ValueError),
    ({"request_options": {"timeout": float("nan")}}, ValueError),
    ({"offer_throughput": True}, TypeError),
    ({"offer_throughput": ThroughputProperties()}, ValueError),
    ({"offer_throughput": ThroughputProperties(auto_scale_increment_percent=0)}, ValueError),
    ({"offer_throughput": ThroughputProperties(offer_throughput=400, auto_scale_max_throughput=4000)}, ValueError),
    ({"offer_throughput": 400, "initial_headers": {
        "x-ms-cosmos-offer-autopilot-settings": '{"maxThroughput":4000}',
    }}, ValueError),
    ({"request_options": {"offerThroughput": 400, "autoUpgradePolicy": '{"maxThroughput":4000}'}}, ValueError),
    ({"response_hook": False}, TypeError),
    ({"response_hook": 42}, TypeError),
    ({"initial_headers": {"If-Match": "*"}}, TypeError),
    ({"initial_headers": {"IF-NONE-MATCH": '"version"'}}, TypeError),
    ({"request_options": {"accessCondition": {"type": "IfMatch", "condition": "*"}}}, TypeError),
    ({"if_none_match": '"version"'}, TypeError),
    ({"if_match": None}, TypeError),
    ({"no_response": True}, NotImplementedError),
    ({"request_options": {"maxItemCount": 1}}, NotImplementedError),
    ({"initial_headers": {"x-ms-session-token": "unused"}}, NotImplementedError),
    ({"initial_headers": {"Prefer": "return=minimal"}}, NotImplementedError),
    ({"initial_headers": {"Authorization": "unused"}}, NotImplementedError),
])
def test_if_not_exists_preflight_validates_the_complete_workflow(create_database_client, options, error):
    """Get-or-create checks every option against the whole workflow before it sends
    anything.

    Twenty-one bad inputs are covered: unusable deadlines, throughput that is
    not one clear choice or is contradicted by a header, hooks that are not
    callable, conditional headers and arguments that cannot apply to a create,
    and settings the Rust engine does not support at all.

    The point is where the failure happens. A valid reply is queued and ready,
    yet nothing is prepared and neither leg runs. Validating lazily instead
    would let the read succeed and only then reject the create, leaving the
    customer with an error after work had already been done -- and, in the race
    case, after another caller's database had already been found.
    """
    client = create_database_client
    client._backend.responses = _get_or_create_responses([200])
    with pytest.raises(error):
        _call_create_database(client, "db1", method_name="create_database_if_not_exists", **options)
    assert client._backend.prepared_requests == []
    client.client_connection.ReadDatabase.assert_not_called()
    client.client_connection.CreateDatabase.assert_not_called()


@pytest.mark.parametrize("statuses", [[200], [404, 201], [404, 409, 200]])
@pytest.mark.parametrize("mapping_name", ["request_options", "feed_options"])
@pytest.mark.parametrize("header,value", [
    ("X-MS-OFFER-THROUGHPUT", "400"),
    ("X-MS-COSMOS-OFFER-AUTOPILOT-SETTINGS", '{"maxThroughput":4000}'),
])
def test_if_not_exists_snapshots_settings_and_limits_throughput_to_create(
    create_database_client, statuses, mapping_name, header, value
):
    """Options are read once at the start, and throughput reaches only the create
    leg.

    The customer's dictionary is edited from underneath the call, between one
    request and the next. Every request still carries the values as they were
    when the call began, so a dictionary a customer reuses or shares across
    threads cannot change a workflow that is already running.

    Throughput appears only on the create request. The reads before and after it
    must not carry it: a read is not a resource being created, and the final
    read in the race case belongs to a database somebody else created.

    All three shapes of the workflow are covered -- already there, created, and
    the race -- along with both names a customer can pass the dictionary under.
    The returned properties carry the last step's request charge, and the
    caller's dictionary gains no extra keys.
    """
    client = create_database_client
    client._backend.responses = _get_or_create_responses(statuses)
    options = {"initialHeaders": {"x-trace-id": "original", header: value}}
    execute = client._backend.execute

    def mutate_caller():
        options["initialHeaders"]["x-trace-id"] = "changed-during-read"
        options["initialHeaders"][header] = "changed-during-read"

    def sync_execute(prepared, *, deadline=None):
        mutate_caller()
        return execute(prepared, deadline=deadline)

    async def async_execute(prepared, *, deadline=None):
        mutate_caller()
        return await execute(prepared, deadline=deadline)

    client._backend.execute = async_execute if isinstance(client, AsyncCosmosClient) else sync_execute
    proxy, properties = _call_create_database(
        client, "db1", method_name="create_database_if_not_exists",
        return_properties=True, **{mapping_name: options},
    )
    assert proxy.id == "db1"
    assert len(client._backend.prepared_requests) == len(statuses)
    assert properties.get_response_headers()["x-ms-request-charge"] == str(len(statuses))
    for prepared in client._backend.prepared_requests:
        headers = wire_headers(prepared)
        assert headers["x-trace-id"] == "original"
        if prepared.op == OP_CREATE_DATABASE:
            assert headers[header.lower()] == value
        else:
            assert "x-ms-offer-throughput" not in headers
            assert "x-ms-cosmos-offer-autopilot-settings" not in headers
    assert set(options) == {"initialHeaders"}


@pytest.mark.parametrize("statuses", [[200], [404, 201], [404, 409, 200]])
def test_if_not_exists_hook_has_independent_final_response(create_database_client, monkeypatch, statuses):
    """The hook fires once, for the step that actually produced the result, and owns
    what it is given.

    Another call is made to appear between parsing and the hook firing,
    overwriting the client's shared record. The hook still receives the last
    step of its own workflow, whether that was a single read, a read and a
    create, or the full race.

    The hook then edits its headers, the returned headers, the database id, and
    a nested field. None of it reaches the caller: the properties keep the
    original nested value and the real activity id, and the proxy still points
    at the database the customer asked for rather than the name the hook wrote.
    """
    from azure.cosmos._helpers import _database_operations as sync_helper
    from azure.cosmos.aio._helpers import _database_operations as async_helper
    client = create_database_client
    client._backend.responses = _get_or_create_responses(statuses)
    module = async_helper if isinstance(client, AsyncCosmosClient) else sync_helper
    parse = module.process_backend_response
    calls = []

    def interleaved_response(*args, **kwargs):
        result = parse(*args, **kwargs)
        client._item_context.response_state.last_response_headers = {"x-ms-activity-id": "another-call"}
        return result

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            calls.append(dict(headers))
            headers["x-ms-activity-id"] = "edited"
            body.get_response_headers()["x-ms-activity-id"] = "edited"
            body["id"] = "different-database"
            body["nested"]["value"] = "edited"

    monkeypatch.setattr(module, "process_backend_response", interleaved_response)
    proxy, properties = _call_create_database(
        client, "db1", method_name="create_database_if_not_exists",
        return_properties=True, response_hook=Hook(),
    )
    assert len(calls) == 1
    assert calls[0]["x-ms-activity-id"] == f"step-{len(statuses) - 1}"
    assert proxy.id == "db1"
    assert properties["nested"]["value"] == "original"
    assert properties.get_response_headers()["x-ms-activity-id"] == f"step-{len(statuses) - 1}"


@pytest.mark.parametrize("statuses", [[200], [404, 201], [404, 409, 200]])
@pytest.mark.parametrize("failure", [
    TimeoutError("customer hook"),
    CosmosResourceNotFoundError(status_code=404, message="customer hook"),
    CosmosResourceExistsError(status_code=409, message="customer hook"),
])
def test_if_not_exists_hook_errors_never_enter_recovery(create_database_client, statuses, failure):
    """An error from the customer's hook is never mistaken for a service reply.

    This is the trap the test exists for. The hook raises the very error types
    the workflow uses to decide what to do next: not-found, which normally means
    create it, and already-exists, which normally means read the winner. If the
    hook's error were caught by that same logic, a failing callback would
    trigger extra requests and could create a database the customer never got
    told about.

    The exact exception reaches the caller, and the request count is unchanged:
    the hook runs after the workflow is finished, so nothing more is sent.
    """
    client = create_database_client
    client._backend.responses = _get_or_create_responses(statuses)

    def hook(headers, body):
        raise failure

    with pytest.raises(type(failure)) as caught:
        _call_create_database(
            client, "db1", method_name="create_database_if_not_exists",
            timeout=5, response_hook=hook,
        )
    assert caught.value is failure
    assert len(client._backend.prepared_requests) == len(statuses)


@pytest.mark.parametrize("expire_after", [1, 2, 3])
def test_if_not_exists_expiration_stops_requests_and_success_hooks(
    create_database_client, monkeypatch, expire_after
):
    """When the budget runs out mid-workflow, the remaining steps are not attempted.

    The clock is pinned and pushed past the deadline just before the first,
    second, or third request. In each case a client timeout error is raised and
    exactly that many requests were attempted -- the workflow stops where the
    budget ran out instead of finishing on borrowed time.

    Every step was handed the same deadline, confirming the budget is worked out
    once for the whole call rather than renewed per leg. The success hook never
    fires, since there was no successful result to report.
    """
    from azure.cosmos._helpers import _request_database
    from azure.cosmos.exceptions import CosmosClientTimeoutError
    client = create_database_client
    client._backend.responses = _get_or_create_responses([404, 409, 200])
    clock = [100.0]
    monkeypatch.setattr(_request_database.time, "monotonic", lambda: clock[0])
    execute = client._backend.execute
    deadlines = []

    def before_request(deadline):
        deadlines.append(deadline)
        if len(deadlines) == expire_after:
            clock[0] = 105.0

    def sync_execute(prepared, *, deadline=None):
        before_request(deadline)
        return execute(prepared, deadline=deadline)

    async def async_execute(prepared, *, deadline=None):
        before_request(deadline)
        return await execute(prepared, deadline=deadline)

    client._backend.execute = async_execute if isinstance(client, AsyncCosmosClient) else sync_execute
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        _call_create_database(
            client, "db1", method_name="create_database_if_not_exists",
            request_options={"timeout": 5}, response_hook=hook,
        )
    assert deadlines == [105.0] * expire_after
    hook.assert_not_called()


def test_if_not_exists_native_dispatch_gets_only_remaining_time(create_database_client, monkeypatch):
    """Each leg of the workflow is given only the time left, not a fresh budget.

    With a pinned clock, a five second budget, one second spent starting the
    driver and one second per request, the driver is handed four, then three,
    then two seconds.

    Handing five seconds to each leg would let a three-step workflow run for
    fifteen seconds after the customer asked for five.
    """
    from azure.cosmos._backend import binding as sync_rust
    from azure.cosmos.aio._backend import binding as async_rust
    from azure.cosmos._helpers import _request_database
    client = create_database_client
    is_async = isinstance(client, AsyncCosmosClient)
    module = async_rust if is_async else sync_rust
    clock = [100.0]
    monkeypatch.setattr(_request_database.time, "monotonic", lambda: clock[0])
    responses = iter(_get_or_create_responses([404, 409, 200]))
    remaining = []

    def dispatch(handle, prepared, *, timeout_seconds=None):
        remaining.append(timeout_seconds)
        clock[0] += 1
        response = next(responses)
        return response.status_code, 0, response.headers, response.body, None

    binding = AsyncMock(side_effect=dispatch) if is_async else MagicMock(side_effect=dispatch)
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(
        create_database=binding, create_database_async=binding,
        read_database=binding, read_database_async=binding,
    ))

    def setup():
        if not remaining:
            clock[0] += 1
        return "fake-handle"

    backend = client._backend
    backend._ensure_driver_handle = AsyncMock(side_effect=setup) if is_async else setup

    def sync_execute(prepared, *, deadline=None):
        return sync_rust.RustBinding.execute(backend, prepared, deadline=deadline)

    async def async_execute(prepared, *, deadline=None):
        return await async_rust.AsyncRustBinding.execute(backend, prepared, deadline=deadline)

    backend.execute = async_execute if is_async else sync_execute
    _call_create_database(client, "db1", method_name="create_database_if_not_exists", timeout=5)
    assert remaining == [4.0, 3.0, 2.0]


@pytest.mark.parametrize("stage", [1, 2, 3])
@pytest.mark.parametrize("cancel", [False, True])
def test_if_not_exists_async_timeout_or_cancellation_drains_each_stage(stage, cancel):
    """Whichever step is in flight when the async workflow stops, that work is
    cancelled and waited on before the error is raised.

    Each of the three steps is made to hang in turn, and each is interrupted
    both ways: by the deadline passing, and by the customer cancelling the task.

    Six combinations, same outcome every time. The hanging work is confirmed
    drained rather than abandoned, no further step is attempted, and the success
    hook does not fire. Cancellation surfaces as cancellation and a timeout as a
    client timeout error, so a customer can tell which one happened.
    """
    import time
    from azure.cosmos.exceptions import CosmosClientTimeoutError

    async def run():
        entered, drained = asyncio.Event(), asyncio.Event()
        backend = _AsyncRustBackend(responses=_get_or_create_responses([404, 409, 200]))
        execute = backend.execute
        calls = []

        async def blocking_execute(prepared, *, deadline=None):
            calls.append(prepared.op)
            if len(calls) == stage:
                entered.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    drained.set()
            return await execute(prepared, deadline=deadline)

        backend.execute = blocking_execute
        hook = MagicMock()
        task = asyncio.create_task(AsyncDatabaseHelper(SimpleNamespace(), backend).create_database_if_not_exists(
            {"id": "db1"}, {}, response_hook=hook,
            deadline=None if cancel else time.monotonic() + 0.05,
        ))
        await entered.wait()
        if cancel:
            task.cancel()
        with pytest.raises(asyncio.CancelledError if cancel else CosmosClientTimeoutError):
            await task
        assert drained.is_set()
        assert len(calls) == stage
        hook.assert_not_called()

    asyncio.run(run())


@pytest.mark.parametrize("name", ["read_database", "read_database_async"])
@pytest.mark.parametrize("remaining", [None, 0.125, 1.0])
def test_database_read_native_binding_accepts_remaining_budget(name, remaining):
    """The native read entry points, sync and async, accept a prepared read plus the
    time remaining, including no limit at all.

    As with the create binding, the handle is unregistered, so reaching a driver
    error proves the arguments themselves were accepted. Passing no limit is
    included because a read with no deadline is a normal call, not a special
    case.
    """
    from azure.cosmos import _rust
    prepared = build_read_database_prepared("db1", {})
    with pytest.raises(RuntimeError, match="(?i)driver"):
        getattr(_rust, name)("unregistered-read-test-handle", prepared, timeout_seconds=remaining)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_if_not_exists_boolean_overload_preserves_literal_overloads(client_type):
    """Get-or-create declares the same three forms in the same order as the plain
    create, so a customer gets identical type checking whichever method they
    pick. Needs Python 3.11 to inspect the declarations at runtime.
    """
    import typing
    from typing import Literal, get_type_hints
    if not hasattr(typing, "get_overloads"):
        pytest.skip("Runtime overload inspection requires Python 3.11 or later.")
    variants = typing.get_overloads(client_type.create_database_if_not_exists)
    assert [
        get_type_hints(variant, localns={"ThroughputProperties": ThroughputProperties})["return_properties"]
        for variant in variants
    ] == [Literal[False], Literal[True], bool]


@pytest.mark.parametrize("statuses", [[200], [404, 201], [404, 409, 200]])
def test_if_not_exists_legacy_receives_remaining_budget_and_isolated_hook(
    create_database_client, monkeypatch, statuses
):
    """On the legacy path the same budget and hook rules apply, in that path's own
    terms.

    The legacy calls take a deadline rather than a handle, so the checks are
    made against what they receive. Every leg gets the same shared deadline, and
    each one is given a per-call timeout one second smaller than the last as the
    pinned clock advances -- the budget shrinks here exactly as it does on the
    Rust path.

    The legacy-only ``read_timeout`` is passed through, since a customer on this
    path is entitled to the settings it supports, and each call carries its own
    start time.

    Two rules are kept from the Rust path. The hook is not handed down to the
    legacy call; the coordinator fires it once itself, so the customer's
    callback cannot run once per leg. And throughput reaches only the create
    leg, never the reads on either side of it.

    The hook's edits to the id, to a nested field, and to the headers do not
    reach the caller's result.
    """
    from azure.cosmos._helpers import _request_database
    from azure.cosmos._helpers._item_context import ItemClientContext
    client = create_database_client
    is_async = isinstance(client, AsyncCosmosClient)
    client._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND
    client._item_context = ItemClientContext(client._backend)
    clock = [100.0]
    monkeypatch.setattr(_request_database.time, "monotonic", lambda: clock[0])
    replies = iter(_get_or_create_responses(statuses))
    recorded = []
    hook_calls = []

    def dispatch(*args, options, **kwargs):
        recorded.append((options, kwargs))
        clock[0] += 1
        reply = next(replies)
        if reply.status_code == 404:
            raise CosmosResourceNotFoundError(status_code=404, message="missing")
        if reply.status_code == 409:
            raise CosmosResourceExistsError(status_code=409, message="race")
        return CosmosDict(json.loads(reply.body), response_headers=reply.headers)

    mock = AsyncMock if is_async else MagicMock
    client.client_connection.ReadDatabase = mock(side_effect=dispatch)
    client.client_connection.CreateDatabase = mock(side_effect=dispatch)

    def hook(headers, properties):
        hook_calls.append(dict(headers))
        properties["id"] = "wrong"
        properties["nested"]["value"] = "wrong"
        headers["x-ms-activity-id"] = "wrong"

    proxy, properties = _call_create_database(
        client, "db1", method_name="create_database_if_not_exists", timeout=5,
        read_timeout=2, offer_throughput=400, return_properties=True, response_hook=hook,
    )
    assert proxy.id == "db1"
    assert properties["nested"]["value"] == "original"
    assert properties.get_response_headers()["x-ms-activity-id"] == f"step-{len(statuses) - 1}"
    assert len(hook_calls) == 1
    for index, (options, kwargs) in enumerate(recorded):
        assert options["_item_operation_deadline"] == 105.0
        assert options["timeout"] == kwargs["timeout"] == 5.0 - index
        assert kwargs["read_timeout"] == 2
        assert kwargs[Constants.OperationStartTime] > 0
        assert "response_hook" not in kwargs
        assert ("offerThroughput" in options) == (index == 1)


@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("options,error", [
    ({"offer_throughput": ThroughputProperties(offer_throughput="4000")}, TypeError),
    ({"offer_throughput": ThroughputProperties(offer_throughput=True)}, TypeError),
    ({"offer_throughput": ThroughputProperties(offer_throughput=4000.0)}, TypeError),
    ({"offer_throughput": ThroughputProperties(auto_scale_max_throughput="4000")}, TypeError),
    ({"offer_throughput": ThroughputProperties(auto_scale_max_throughput=True)}, TypeError),
    ({"offer_throughput": ThroughputProperties(
        auto_scale_max_throughput=4000, auto_scale_increment_percent=False,
    )}, TypeError),
    ({"offer_throughput": ThroughputProperties(
        auto_scale_max_throughput=4000, auto_scale_increment_percent=1.5,
    )}, TypeError),
    ({"offer_throughput": 2**63}, ValueError),
    ({"offer_throughput": -(2**63) - 1}, ValueError),
    ({"request_options": {"offerThroughput": "4000"}}, TypeError),
    ({"request_options": {"offerThroughput": False}}, TypeError),
    ({"feed_options": {"offerThroughput": 2**80}}, ValueError),
    ({"request_options": {"autoUpgradePolicy": {"maxThroughput": 4000}}}, TypeError),
    ({"feed_options": {"autoUpgradePolicy": 4000}}, TypeError),
])
def test_creation_values_fail_before_any_request(create_database_client, method_name, use_legacy, options, error):
    client = create_database_client
    backend = client._backend
    backend.responses = _get_or_create_responses([200])
    if use_legacy:
        client._backend = ASYNC_LEGACY_BACKEND if isinstance(client, AsyncCosmosClient) else LEGACY_BACKEND
    hook = MagicMock()
    with pytest.raises(error):
        _call_create_database(client, "db1", method_name=method_name, response_hook=hook, **options)
    assert backend.prepared_requests == []
    client.client_connection.ReadDatabase.assert_not_called()
    client.client_connection.CreateDatabase.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
@pytest.mark.parametrize("mapping_name", ["request_options", "feed_options"])
@pytest.mark.parametrize("throughput", [None, 0, -(2**63), 2**63 - 1])
def test_manual_throughput_local_validation_preserves_representable_values(
    create_database_client, method_name, mapping_name, throughput
):
    client = create_database_client
    statuses = [201] if method_name == "create_database" else [404, 201]
    client._backend.responses = _get_or_create_responses(statuses)
    _call_create_database(
        client, "db1", method_name=method_name, **{mapping_name: {"offerThroughput": throughput}},
    )
    assert client._backend.prepared.settings.resource.offer_throughput == (throughput or None)


@pytest.mark.parametrize("method_name,statuses", [
    ("create_database", [201]),
    ("create_database_if_not_exists", [200]),
    ("create_database_if_not_exists", [404, 201]),
    ("create_database_if_not_exists", [404, 409, 200]),
])
@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("typed,raw,explicit,expected", [
    ({}, {}, {}, ("Low", "7")),
    ({}, {}, {"priority": None, "throughput_bucket": 0}, ("Low", "7")),
    ({}, {}, {"priority": "", "throughput_bucket": None}, ("Low", "7")),
    ({}, {"x-ms-cosmos-priority-level": "High", "X-MS-COSMOS-THROUGHPUT-BUCKET": "2"},
     {}, ("High", "2")),
    ({"priorityLevel": "High", "throughputBucket": 3}, {}, {}, ("High", "3")),
    ({"priorityLevel": "Low", "throughputBucket": 2},
     {"x-ms-cosmos-priority-level": "Low", "x-ms-cosmos-throughput-bucket": "2"},
     {"priority": "High", "throughput_bucket": 3}, ("High", "3")),
    ({"priorityLevel": "High", "throughputBucket": 3},
     {"x-ms-cosmos-priority-level": "Low", "x-ms-cosmos-throughput-bucket": "2"},
     {"priority": None, "throughput_bucket": 0}, ("Low", "2")),
])
def test_database_defaults_and_overrides_are_stable_across_every_step(
    create_database_client, method_name, statuses, use_legacy, reverse, typed, raw, explicit, expected,
):
    from copy import deepcopy
    from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
    from azure.cosmos import documents
    client = create_database_client
    is_async = isinstance(client, AsyncCosmosClient)
    backend = client._backend
    backend.responses = _get_or_create_responses(statuses)
    default_headers = {"x-ms-cosmos-priority-level": "Low", "x-ms-cosmos-throughput-bucket": 7}
    recorded_headers = []
    if use_legacy:
        client._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND
        replies = iter(_get_or_create_responses(statuses))
        header_context = SimpleNamespace(
            UseMultipleWriteLocations=False, master_key=None, resource_tokens=None, client_id=None,
        )

        def dispatch(*args, options, **kwargs):
            initial = base.resolve_initial_headers(default_headers, options) or default_headers
            creates = "database" in kwargs
            headers = base.GetHeaders(
                header_context, initial, "post" if creates else "get",
                "/dbs/" if creates else "/dbs/db1/", "" if creates else "dbs/db1", "dbs",
                documents._OperationType.Create if creates else documents._OperationType.Read, options,
            )
            recorded_headers.append({key.lower(): str(value) for key, value in headers.items()})
            reply = next(replies)
            if reply.status_code == 404:
                raise CosmosResourceNotFoundError(status_code=404, message="missing")
            if reply.status_code == 409:
                raise CosmosResourceExistsError(status_code=409, message="race")
            return CosmosDict(json.loads(reply.body), response_headers=reply.headers)

        mock = AsyncMock if is_async else MagicMock
        client.client_connection.ReadDatabase = mock(side_effect=dispatch)
        client.client_connection.CreateDatabase = mock(side_effect=dispatch)
    client._item_context = ItemClientContext(
        client._backend, ItemClientDefaults(priority="Low", throughput_bucket=7, no_response_on_write=True),
    )
    entries = [*typed.items(), ("initialHeaders", raw), ("offerThroughput", 1000)]
    options = dict(reversed(entries) if reverse else entries)
    original = deepcopy(options)
    result = _call_create_database(
        client, "db1", method_name=method_name, request_options=options, offer_throughput=4000, **explicit,
    )
    assert result.id == "db1"
    assert options == original
    if not use_legacy:
        recorded_headers = [wire_headers(request) for request in backend.prepared_requests]
    assert len(recorded_headers) == len(statuses)
    for index, headers in enumerate(recorded_headers):
        assert (headers["x-ms-cosmos-priority-level"], headers["x-ms-cosmos-throughput-bucket"]) == expected
        creates = method_name == "create_database" or index == 1
        assert headers.get("x-ms-offer-throughput") == ("4000" if creates else None)
        assert "prefer" not in headers


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("option,header,value,override", [
    ("offerThroughput", "x-ms-offer-throughput", 1000, 4000),
    ("autoUpgradePolicy", "x-ms-cosmos-offer-autopilot-settings",
     '{"maxThroughput":1000}', '{"maxThroughput":4000}'),
    ("contentType", "content-type", "application/json", "application/custom+json"),
    ("correlatedActivityId", "x-ms-cosmos-correlated-activityid", "raw", "typed"),
])
def test_get_or_create_typed_options_override_headers_without_order_dependency(
    create_database_client, reverse, option, header, value, override,
):
    client = create_database_client
    client._backend.responses = _get_or_create_responses([404, 409, 200])
    entries = [(option, override), ("initialHeaders", {header.upper(): str(value)})]
    options = dict(reversed(entries) if reverse else entries)
    _call_create_database(client, "db1", method_name="create_database_if_not_exists", request_options=options)
    for request in client._backend.prepared_requests:
        if option in ("offerThroughput", "autoUpgradePolicy") and request.op == OP_READ_DATABASE:
            assert header not in wire_headers(request)
        else:
            assert wire_headers(request)[header] == str(override)


@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
@pytest.mark.parametrize("offer", [4000, ThroughputProperties(auto_scale_max_throughput=4000)])
def test_explicit_throughput_replaces_invalid_unused_nested_values(create_database_client, method_name, offer):
    client = create_database_client
    client._backend.responses = _get_or_create_responses(
        [201] if method_name == "create_database" else [404, 201]
    )
    options = {"offerThroughput": "invalid", "autoUpgradePolicy": {"maxThroughput": "invalid"}}
    _call_create_database(client, "db1", method_name=method_name, offer_throughput=offer, request_options=options)
    resource = client._backend.prepared.settings.resource
    if offer == 4000:
        assert resource.offer_throughput == 4000
        assert resource.autoscale_settings is None
    else:
        assert json.loads(resource.autoscale_settings) == {"maxThroughput": 4000}
        assert resource.offer_throughput is None
    assert options == {"offerThroughput": "invalid", "autoUpgradePolicy": {"maxThroughput": "invalid"}}


@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
@pytest.mark.parametrize("options", [{}, {"priority": None, "throughput_bucket": None},
                                    {"priority": "", "throughput_bucket": 0}])
def test_unset_database_defaults_add_no_request_tags_or_capacity(create_database_client, method_name, options):
    client = create_database_client
    client._backend.responses = _get_or_create_responses(
        [201] if method_name == "create_database" else [404, 409, 200]
    )
    _call_create_database(client, "db1", method_name=method_name, **options)
    for request in client._backend.prepared_requests:
        assert request.settings.priority is None
        assert request.settings.throughput_bucket is None
        assert request.settings.resource.offer_throughput is None
        assert request.settings.resource.autoscale_settings is None
        assert not {
            "x-ms-cosmos-priority-level", "x-ms-cosmos-throughput-bucket",
            "x-ms-offer-throughput", "x-ms-cosmos-offer-autopilot-settings",
        }.intersection(wire_headers(request))


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


@pytest.fixture(params=[False, True], ids=["sync", "aio"])
def delete_database_client(request):
    """Build a client for delete tests, once sync and once async.

    The legacy ``DeleteDatabase`` raises if called, so an accidental fall back
    shows up as a failure rather than a quiet pass. The client starts with a
    stale activity id recorded, so a test can prove the hook got this call's
    headers and not what was left over from before.

    The canned reply is a no-content success with a request charge, which is
    what a real successful delete looks like: headers but no body.
    """
    is_async = request.param
    client_type = AsyncCosmosClient if is_async else CosmosClient
    client = object.__new__(client_type)
    delete_mock = AsyncMock if is_async else MagicMock
    client.client_connection = SimpleNamespace(
        DeleteDatabase=delete_mock(side_effect=AssertionError("legacy delete called")),
        last_response_headers=CaseInsensitiveDict({"x-ms-activity-id": "stale"}),
    )
    response = BackendResponse(
        status_code=204,
        headers=CaseInsensitiveDict({
            "x-ms-request-charge": "4.24",
            "x-ms-activity-id": "delete-one",
        }),
        body=b"",
        diagnostics="activity=delete-one requests=1",
    )
    client._backend = _AsyncRustBackend(response) if is_async else _RustBackend(response)
    client._backend.execute = delete_mock(wraps=client._backend.execute)
    return client


def _call_delete_database(client, *args, **kwargs):
    """Call ``delete_database`` and wait for it if the client is async."""
    result = client.delete_database(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _use_legacy_delete(client):
    """Switch the client to the legacy path and make its delete succeed.

    The legacy call records the response headers on the connection instead of
    returning them, which is how that path reports a delete. Tests read them
    from there.
    """
    is_async = isinstance(client, AsyncCosmosClient)
    client._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND

    def delete(*_args, **_kwargs):
        client.client_connection.last_response_headers = CaseInsensitiveDict({
            "x-ms-request-charge": "4.24",
            "x-ms-activity-id": "delete-one",
        })

    client.client_connection.DeleteDatabase.side_effect = delete


@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_delete_database_rejects_obsolete_options_before_dispatch(
    delete_database_client, use_legacy, option, value
):
    """Retired options are refused on both paths before anything is deleted.

    Session token and query metrics no longer do anything. Each raises
    ``TypeError`` naming the option, for every value including ``None`` and
    ``False``.

    Failing before anything is sent matters more here than anywhere else in this
    file: a delete cannot be undone, so the customer must be told their option is
    unsupported rather than have the database removed and the option ignored.
    Neither path is called and the hook does not fire.
    """
    client = delete_database_client
    rust_backend = client._backend
    if use_legacy:
        _use_legacy_delete(client)
    hook = MagicMock()
    with pytest.raises(TypeError, match=f"'{option}'"):
        _call_delete_database(client, "db1", response_hook=hook, **{option: value})
    rust_backend.execute.assert_not_called()
    client.client_connection.DeleteDatabase.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("value", [None, False, True])
def test_delete_database_rejects_positional_query_metrics(delete_database_client, value):
    """A second positional argument is a ``TypeError``, not a silently accepted
    option.

    Older code passed query metrics this way. Accepting it now would mean the
    value lands on whatever argument happens to be second, so the call is
    refused and nothing is deleted.
    """
    client = delete_database_client
    with pytest.raises(TypeError):
        _call_delete_database(client, "db1", value)
    client._backend.execute.assert_not_called()
    client.client_connection.DeleteDatabase.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
def test_delete_database_hook_receives_an_isolated_case_insensitive_snapshot(delete_database_client, use_legacy):
    """The delete hook is handed one argument -- the headers -- and they are its own
    private copy, on both paths.

    A successful delete has no body, so the hook takes headers alone and the
    call itself returns nothing. Header lookups are case-insensitive, so the
    hook can use whatever spelling it likes.

    The copy is independent in both directions. Changing the client's headers
    afterwards does not alter what the hook received, and the hook emptying its
    own copy does not wipe the client's record. A customer whose hook logs the
    request charge gets the charge for this delete, and cannot break the client
    by modifying what it was handed.

    On the Rust path the hook also receives the driver diagnostics header.
    """
    client = delete_database_client
    rust_backend = client._backend
    if use_legacy:
        _use_legacy_delete(client)
    calls = []

    def hook(headers):
        assert client.client_connection.last_response_headers["x-ms-activity-id"] == "delete-one"
        assert headers["X-MS-ACTIVITY-ID"] == "delete-one"
        assert headers["X-MS-REQUEST-CHARGE"] == "4.24"
        calls.append(headers)

    assert _call_delete_database(client, "db1", response_hook=hook) is None
    assert len(calls) == 1
    assert calls[0] is not client.client_connection.last_response_headers
    if use_legacy:
        rust_backend.execute.assert_not_called()
        client.client_connection.DeleteDatabase.assert_called_once()
    else:
        rust_backend.execute.assert_called_once()
        client.client_connection.DeleteDatabase.assert_not_called()
        assert calls[0]["x-ms-cosmos-sdk-diagnostics"] == "activity=delete-one requests=1"
    client.client_connection.last_response_headers["x-ms-activity-id"] = "later-operation"
    assert calls[0]["x-ms-activity-id"] == "delete-one"
    calls[0].clear()
    assert client.client_connection.last_response_headers["x-ms-request-charge"] == "4.24"


def test_delete_database_invokes_falsey_callable_hook(delete_database_client):
    """A hook that reports itself as false when tested as a boolean is still
    callable, so it still runs exactly once. Deciding whether to call a hook by
    truth-testing it would silently skip a valid one and lose the customer's
    record of a delete.
    """
    class Hook:
        calls = 0

        def __bool__(self):
            return False

        def __call__(self, headers):
            assert headers["x-ms-activity-id"] == "delete-one"
            self.calls += 1

    hook = Hook()
    _call_delete_database(delete_database_client, "db1", response_hook=hook)
    assert hook.calls == 1


@pytest.mark.parametrize("error_type", [ValueError, NotImplementedError, asyncio.CancelledError])
def test_delete_database_hook_failure_never_replays(delete_database_client, error_type):
    """If the customer's hook raises after a successful delete, the delete is not
    repeated.

    The exact exception reaches the caller, the engine was called once, and the
    legacy path was never tried. The database is already gone at this point;
    replaying would send a second delete that finds nothing and reports a
    confusing not-found for a delete the customer actually completed.

    The compatibility fallback counter does not move either, so this is not
    recorded as a fallback.
    """
    client = delete_database_client
    error = error_type("callback failed")
    hook = MagicMock(side_effect=error)
    before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as raised:
        _call_delete_database(client, "db1", response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    client._backend.execute.assert_called_once()
    client.client_connection.DeleteDatabase.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("error_type", [ServiceRequestError, NotImplementedError, asyncio.CancelledError])
def test_delete_database_backend_failure_never_replays(delete_database_client, error_type):
    """A failure inside the engine is raised as-is and is not retried on the other
    path.

    A transport error is the dangerous case: the delete may well have reached
    the service before the connection broke, so repeating it could report
    not-found for a delete that succeeded. The exact exception is raised, the
    engine was called once, the hook never fires, and the fallback counter is
    unchanged.
    """
    client = delete_database_client
    error = error_type("backend failed")
    client._backend.execute.side_effect = error
    hook = MagicMock()
    before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as raised:
        _call_delete_database(client, "db1", response_hook=hook)
    assert raised.value is error
    hook.assert_not_called()
    client._backend.execute.assert_called_once()
    client.client_connection.DeleteDatabase.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("status", [403, 404, 412, 429, 500])
def test_delete_database_service_error_never_fires_success_hook_or_replays(delete_database_client, status):
    """A rejected delete surfaces with its status and is never tried again on the
    other path.

    Forbidden, not-found, precondition-failed, throttled, and server error all
    raise with the status preserved. The conditional header the customer asked
    for is still on the request that failed, and the failure's activity id is
    recorded so they can quote it in a support case.

    The success hook does not fire, since nothing was deleted, and the fallback
    counter does not move. Replaying a precondition failure on the other path
    would be the worst case of all: the condition might pass the second time and
    delete a database the customer had guarded against exactly that.
    """
    client = delete_database_client
    client._backend.responses = [BackendResponse(
        status_code=status,
        headers=CaseInsensitiveDict({"x-ms-activity-id": "failed-delete"}),
        body=b'{"message":"delete failed"}',
    )]
    hook = MagicMock()
    before = rust_compatibility_fallback_count()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_delete_database(
            client, "db1", etag="known-etag",
            match_condition=MatchConditions.IfNotModified, response_hook=hook,
        )
    assert raised.value.status_code == status
    assert wire_headers(client._backend.prepared)["if-match"] == "known-etag"
    assert client.client_connection.last_response_headers["x-ms-activity-id"] == "failed-delete"
    hook.assert_not_called()
    client._backend.execute.assert_called_once()
    client.client_connection.DeleteDatabase.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"read_timeout": 0.5},
        {"timeout": 0.5},
        {"timeout": 0},
        {"timeout": "invalid"},
        {"connection_timeout": 1},
        {"raw_request_hook": lambda request: None},
        {"raw_response_hook": lambda response: None},
        {"initial_headers": {"user-agent": "custom"}},
        {"initial_headers": {"X-MS-VERSION": "2020-07-15"}},
        {"unknown_option": True},
    ],
)
def test_delete_database_unsupported_options_never_fall_back(delete_database_client, kwargs):
    """Options the Rust engine cannot honor stop the delete instead of quietly
    sending it through the legacy transport.

    The list covers a socket-level read timeout, deadlines that are too small,
    zero, or not a number, a connect timeout, the raw request and response
    hooks, two headers the driver owns, and an unknown keyword.

    Each raises ``NotImplementedError`` pointing at the legacy Python client.
    Nothing is sent on either path, the hook does not fire, and the fallback
    counter does not move -- a customer must not have a delete carried out on a
    transport they did not choose.
    """
    client = delete_database_client
    hook = MagicMock()
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="delete_database.*legacy Python"):
        _call_delete_database(client, "db1", response_hook=hook, **kwargs)
    hook.assert_not_called()
    client._backend.execute.assert_not_called()
    client.client_connection.DeleteDatabase.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("timeout", [None, 1, 3.5])
def test_delete_database_preserves_supported_deadlines_and_options(delete_database_client, timeout):
    """Supported options reach the delete request unchanged, and the call returns
    nothing on success.

    The customer's own header and the throughput bucket are both on the request.
    A per-call deadline travels with it in seconds; leaving it off adds no
    overall-timeout header at all, rather than inventing a default the customer
    never asked for. One request, and the legacy path is untouched.
    """
    client = delete_database_client
    assert _call_delete_database(
        client, "db1", timeout=timeout, throughput_bucket=7,
        initial_headers={"x-my-app": "catalog-service"},
    ) is None
    prepared = client._backend.prepared
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert wire_headers(prepared)["x-my-app"] == "catalog-service"
    if timeout is None:
        assert Constants.OVERALL_TIMEOUT_SECONDS not in wire_headers(prepared)
    else:
        assert settings_options(prepared)["timeout_seconds"] == timeout
    client._backend.execute.assert_called_once()
    client.client_connection.DeleteDatabase.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {}),
        ({"etag": "v1", "match_condition": MatchConditions.IfNotModified}, {"If-Match": "v1"}),
        ({"etag": "v1", "match_condition": MatchConditions.IfModified}, {"If-None-Match": "v1"}),
        ({"match_condition": MatchConditions.IfPresent}, {"If-Match": "*"}),
        ({"match_condition": MatchConditions.IfMissing}, {"If-None-Match": "*"}),
        ({"etag": "unused", "match_condition": MatchConditions.IfPresent}, {"If-Match": "*"}),
        ({"etag": "unused", "match_condition": MatchConditions.IfMissing}, {"If-None-Match": "*"}),
        ({"if_match": "v1"}, {"If-Match": "v1"}),
        ({"if_none_match": "v1"}, {"If-None-Match": "v1"}),
    ],
)
def test_delete_database_preserves_conditional_headers_on_both_backends(
    delete_database_client, use_legacy, kwargs, expected
):
    """Conditional delete arguments become the same headers on both paths.

    An etag with a not-modified condition becomes ``If-Match``; with a modified
    condition it becomes ``If-None-Match``. A presence or absence condition
    becomes the wildcard form, and any etag passed alongside is ignored because
    the condition does not depend on a version. The raw ``if_match`` and
    ``if_none_match`` arguments pass through as given, and no warning is raised.

    This is a customer's protection against deleting a database that changed
    since they last looked at it, so it has to behave identically whichever path
    they are on.
    """
    client = delete_database_client
    rust_backend = client._backend
    if use_legacy:
        _use_legacy_delete(client)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert _call_delete_database(client, "db1", **kwargs) is None
    assert caught == []
    if use_legacy:
        rust_backend.execute.assert_not_called()
        client.client_connection.DeleteDatabase.assert_called_once()
        call = client.client_connection.DeleteDatabase.call_args
        from common.typed_requests import flatten_options_to_headers
        headers = flatten_options_to_headers(call.kwargs["options"])
        assert "etag" not in call.kwargs
    else:
        client.client_connection.DeleteDatabase.assert_not_called()
        rust_backend.execute.assert_called_once()
        headers = wire_headers(rust_backend.prepared)
    assert {
        key.lower(): value for key, value in headers.items()
        if key.lower() in ("if-match", "if-none-match")
    } == {key.lower(): value for key, value in expected.items()}


@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"etag": "", "match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"etag": "v1", "match_condition": "invalid"}, TypeError),
    ],
)
def test_delete_database_invalid_guards_fail_before_dispatch(
    delete_database_client, use_legacy, kwargs, error
):
    """Incomplete or malformed conditional arguments stop the delete on both paths.

    An etag with no condition, a condition with no etag, and an empty etag are
    ``ValueError``; a condition that is not a real match condition is a
    ``TypeError``.

    Sending any of these would produce an unconditional delete from a customer
    who believed they had guarded it. Nothing is sent and the hook does
    not fire.
    """
    client = delete_database_client
    rust_backend = client._backend
    if use_legacy:
        _use_legacy_delete(client)
    hook = MagicMock()
    with pytest.raises(error):
        _call_delete_database(client, "db1", response_hook=hook, **kwargs)
    hook.assert_not_called()
    rust_backend.execute.assert_not_called()
    client.client_connection.DeleteDatabase.assert_not_called()


def test_delete_database_is_registered_as_single_response_operation():
    """Delete-database is a single-reply operation, so it is sent to the
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
    assert legacy_partition_key_from_request(prepared) == "[]"


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

    assert "sessionToken" not in wire_headers(prepared)
    assert Constants.ContainerRID not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert settings_options(prepared)["timeout_seconds"] == 3.5


def test_sync_delete_database_routes_to_rust_and_never_calls_legacy():
    """On a Rust-backed client the delete runs through the backend, records the
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
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == '7'
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


def test_sync_delete_database_rejects_unsupported_read_timeout_without_fallback():
    """The timeout eligibility rule is unchanged, but no legacy delete is allowed."""
    connection = SimpleNamespace(
        DeleteDatabase=MagicMock(return_value=None),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())

    with pytest.raises(NotImplementedError, match="delete_database.*legacy Python"):
        DatabaseHelper(connection, backend).delete_database(
            "dbs/db1",
            {Constants.Kwargs.READ_TIMEOUT: 2},
            kwargs={},
        )

    assert backend.prepared is None
    connection.DeleteDatabase.assert_not_called()


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


def test_async_delete_database_rejects_unsupported_read_timeout_without_fallback():
    """The async delete uses the same no-fallback policy."""
    async def run():
        """An unsupported timeout must not reach either transport."""
        connection = SimpleNamespace(
            DeleteDatabase=AsyncMock(return_value=None),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(_deleted_response())

        with pytest.raises(NotImplementedError, match="delete_database.*legacy Python"):
            await AsyncDatabaseHelper(connection, backend).delete_database(
                "dbs/db1",
                {Constants.Kwargs.READ_TIMEOUT: 2},
                kwargs={},
            )

        assert backend.prepared is None
        connection.DeleteDatabase.assert_not_awaited()

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


def test_sync_delete_database_preserves_access_conditions_without_warnings():
    """A guarded delete remains guarded without misleading deprecation warnings."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())
    client._backend = backend

    with warnings.catch_warnings(record=True) as warnings_seen:
        warnings.simplefilter("always")
        client.delete_database(
            "db1",
            etag="etag",
            match_condition=MatchConditions.IfNotModified,
        )

    assert warnings_seen == []
    prepared = backend.prepared
    assert prepared is not None
    assert prepared.item_id == "db1"
    assert wire_headers(prepared)["if-match"] == "etag"
    assert "sessionToken" not in wire_headers(prepared)
    assert "x-ms-session-token" not in wire_headers(prepared)


def test_sync_delete_database_preserves_wildcard_guard_without_fallback():
    """An unused ETag must not force fallback or remove the validated wildcard guard."""
    client = object.__new__(CosmosClient)
    client.client_connection = SimpleNamespace(
        DeleteDatabase=MagicMock(side_effect=AssertionError("legacy delete called")),
        last_response_headers={},
    )
    backend = _RustBackend(_deleted_response())
    client._backend = backend

    with warnings.catch_warnings(record=True) as warnings_seen:
        warnings.simplefilter("always")
        client.delete_database(
            "db1",
            etag="etag",
            match_condition=MatchConditions.IfPresent,
        )

    assert warnings_seen == []
    assert wire_headers(backend.prepared)["if-match"] == "*"
    client.client_connection.DeleteDatabase.assert_not_called()


def test_async_delete_database_preserves_access_conditions_without_warnings():
    """Async deletes retain conditional headers without deprecation warnings."""
    async def run():
        """Verify the condition reaches the Rust request."""
        client = object.__new__(AsyncCosmosClient)
        client.client_connection = SimpleNamespace(
            DeleteDatabase=AsyncMock(side_effect=AssertionError("legacy delete called")),
            last_response_headers={},
        )
        backend = _AsyncRustBackend(_deleted_response())
        client._backend = backend

        with warnings.catch_warnings(record=True) as warnings_seen:
            warnings.simplefilter("always")
            await client.delete_database(
                "db1",
                etag="etag",
                match_condition=MatchConditions.IfNotModified,
            )

        assert warnings_seen == []
        prepared = backend.prepared
        assert prepared is not None
        assert prepared.item_id == "db1"
        assert wire_headers(prepared)["if-match"] == "etag"
        assert "sessionToken" not in wire_headers(prepared)
        assert "x-ms-session-token" not in wire_headers(prepared)

    asyncio.run(run())
