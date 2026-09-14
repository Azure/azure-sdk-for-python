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

* the request the rust engine is handed -- database name, no body, the headers
  built from the caller's options, and the per-call ``timeout``. If any of that
  is wrong the call reads the wrong database or drops an option.
* rejecting Rust reads when an option cannot be honored exactly, without
  replaying through legacy transport or silently rounding a deadline.
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
from azure.cosmos._helpers.database_helper import DatabaseHelper
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncClientConnection,
)
from azure.cosmos.aio._cosmos_client import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.aio._helpers.database_helper import AsyncDatabaseHelper
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceExistsError, CosmosResourceNotFoundError
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
    """Explicit legacy helper selection retains its internal timeout plumbing."""
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


def test_sync_database_proxy_read_rejects_deprecated_session_token():
    """Obsolete session-token usage fails before dispatch."""
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
    with pytest.raises(TypeError):
        _call_database_read(database_read_case, value)
    database_read_case.backend.execute.assert_not_called()
    database_read_case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10, float(2**64 - 2048)])
def test_database_read_preserves_supported_options_and_refreshes_properties(database_read_case, timeout):
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
    assert prepared.headers["initialHeaders"] == {"x-my-app": "catalog"}
    assert prepared.headers["throughputBucket"] == 7
    assert prepared.headers.get(Constants.OVERALL_TIMEOUT_SECONDS) == timeout
    if timeout is None:
        assert Constants.OVERALL_TIMEOUT_SECONDS not in prepared.headers
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
    case = database_read_case
    hook = MagicMock()
    with pytest.raises(NotImplementedError, match="DatabaseProxy.read.*legacy Python"):
        _call_database_read(case, response_hook=hook, **kwargs)
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True])
def test_database_read_hook_snapshot_is_isolated_and_falsey_callable_runs(database_read_case, use_legacy):
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
    from azure.cosmos._helpers._request_headers import flatten_options_to_headers

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
        headers = case.backend.prepared.headers
        case.connection.ReadDatabase.assert_not_called()
    assert {key: headers[key] for key in ("If-Match", "If-None-Match") if key in headers} == expected


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
    assert case.backend.prepared.headers["If-Match"] == "v1"
    assert case.proxy._properties["_etag"] == "old"
    hook.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.ReadDatabase.assert_not_called()


def test_database_read_not_modified_preserves_empty_response_and_hook(database_read_case):
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
    """With no rust backend (the core-python client) the coordinator runs the legacy
    ``CreateDatabase`` call directly, passing the database, options, and any extra
    kwargs straight through -- the legacy engine stays behind the same boundary."""
    connection = SimpleNamespace(
        CreateDatabase=MagicMock(return_value={"id": "db1"}),
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
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "existing"}),
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
    """Explicit async legacy helper selection retains internal timeout plumbing."""
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
        assert backend.prepared.headers["throughputBucket"] == 9
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_database_proxy_read_rejects_deprecated_session_token():
    """The async proxy also rejects the obsolete token before dispatch."""
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
    """Async twin: with no rust backend, the async coordinator awaits the legacy
    ``CreateDatabase`` call directly, passing database/options/extra kwargs through."""
    async def run():
        """Create via legacy-only path (no backend) and confirm the async ``CreateDatabase`` is awaited with correct args."""
        connection = SimpleNamespace(
            CreateDatabase=AsyncMock(return_value={"id": "db1"}),
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
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(
                side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
            ),
            CreateDatabase=AsyncMock(return_value={"id": "db1", "_rid": "created"}),
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
    result = getattr(client, method_name)(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("option", ["populate_query_metrics", "session_token", "etag", "match_condition"])
@pytest.mark.parametrize("value", [None, False, True, "value"])
@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
def test_create_database_rejects_inapplicable_options(create_database_client, option, value, method_name):
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
    headers = client._backend.prepared.headers
    assert headers["initialHeaders"] == {"x-custom": "value"}
    assert headers["throughputBucket"] == 9
    assert headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5
    if throughput is None or workflow in ("existing", "race"):
        assert "offerThroughput" not in headers
        assert "autoUpgradePolicy" not in headers
    elif isinstance(throughput, int):
        assert headers["offerThroughput"] == throughput
    else:
        assert json.loads(headers["autoUpgradePolicy"])["maxThroughput"] == 4000
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
        read_headers = client._backend.prepared_requests[0].headers
        assert "offerThroughput" not in read_headers
        assert "autoUpgradePolicy" not in read_headers
    if workflow == "race":
        assert headers == read_headers
        create_headers = client._backend.prepared_requests[1].headers
        if isinstance(throughput, int):
            assert create_headers["offerThroughput"] == throughput
        elif throughput is not None:
            assert json.loads(create_headers["autoUpgradePolicy"])["maxThroughput"] == 4000


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize("method_name", ["create_database", "create_database_if_not_exists"])
def test_create_database_signature_is_keyword_only_after_id(client_type, method_name):
    parameters = inspect.signature(getattr(client_type, method_name)).parameters
    assert parameters["id"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["id"].default is inspect.Parameter.empty
    assert parameters["offer_throughput"].kind == inspect.Parameter.KEYWORD_ONLY
    assert not any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in parameters.values())


def test_if_not_exists_unsupported_option_does_not_recommend_legacy(create_database_client):
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
    assert client.client_connection.last_response_headers["x-ms-activity-id"] == f"step-{len(statuses) - 1}"
    hook.assert_not_called()
    client.client_connection.ReadDatabase.assert_not_called()
    client.client_connection.CreateDatabase.assert_not_called()


@pytest.mark.parametrize("failure_type", [ServiceRequestError, asyncio.CancelledError])
def test_if_not_exists_follow_up_read_preserves_transport_error_or_cancellation(
    create_database_client, failure_type
):
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
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "existing"}),
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
    result = client.delete_database(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _use_legacy_delete(client):
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
    client = delete_database_client
    with pytest.raises(TypeError):
        _call_delete_database(client, "db1", value)
    client._backend.execute.assert_not_called()
    client.client_connection.DeleteDatabase.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
def test_delete_database_hook_receives_an_isolated_case_insensitive_snapshot(delete_database_client, use_legacy):
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
    assert client._backend.prepared.headers["If-Match"] == "known-etag"
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
    client = delete_database_client
    assert _call_delete_database(
        client, "db1", timeout=timeout, throughput_bucket=7,
        initial_headers={"x-my-app": "catalog-service"},
    ) is None
    prepared = client._backend.prepared
    assert prepared.headers["throughputBucket"] == 7
    assert prepared.headers["initialHeaders"]["x-my-app"] == "catalog-service"
    if timeout is None:
        assert Constants.OVERALL_TIMEOUT_SECONDS not in prepared.headers
    else:
        assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == timeout
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
        from azure.cosmos._helpers._request_headers import flatten_options_to_headers
        headers = flatten_options_to_headers(call.kwargs["options"])
        assert "etag" not in call.kwargs
    else:
        client.client_connection.DeleteDatabase.assert_not_called()
        rust_backend.execute.assert_called_once()
        headers = rust_backend.prepared.headers
    assert {key: headers[key] for key in ("If-Match", "If-None-Match") if key in headers} == expected


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
    assert prepared.headers["If-Match"] == "etag"
    assert "sessionToken" not in prepared.headers
    assert "x-ms-session-token" not in prepared.headers


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
    assert backend.prepared.headers["If-Match"] == "*"
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
        assert prepared.headers["If-Match"] == "etag"
        assert "sessionToken" not in prepared.headers
        assert "x-ms-session-token" not in prepared.headers

    asyncio.run(run())
