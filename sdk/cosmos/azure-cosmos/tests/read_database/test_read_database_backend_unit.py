# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Maintained Rust database-read unit coverage; no legacy test imports."""

import asyncio
import warnings
from copy import deepcopy
from functools import partial
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from common.database_backend_stubs import (
    _FakeBackend,
    _AsyncFakeBackend,
    _call_database_read,
    make_database_read_case,
)
from common.typed_requests import wire_headers, settings_options
from azure.core import MatchConditions
from azure.core.exceptions import ServiceRequestError
from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_READ_DATABASE
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_database import (
    build_read_database_prepared,
    is_read_database_rust_eligible,
)
from azure.cosmos._helpers._database_operations import DatabaseHelper
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.aio._helpers._database_operations import AsyncDatabaseHelper
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError


@pytest.fixture(params=["sync", "async"])
def database_read_case(request):
    """Exercise each public surface without constructing a legacy backend."""
    return make_database_read_case(request.param == "async")


def test_database_read_test_dependencies_do_not_require_legacy_rust(monkeypatch):
    """Reload test code with legacy imports forbidden after SDK initialization."""
    import builtins
    import runpy
    from importlib.util import resolve_name
    from pathlib import Path

    original_import = builtins.__import__
    forbidden = {
        "azure.cosmos._backend.legacy",
        "azure.cosmos.aio._backend.legacy",
        "azure.cosmos._cosmos_client_connection",
        "azure.cosmos.aio._cosmos_client_connection_async",
        "common.test_create_database_backend_unit",
        "read_database.test_read_database_legacy_unit",
    }

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        absolute = (
            resolve_name("." * level + name, globals["__package__"]) if level else name
        )
        requested = {absolute, *(f"{absolute}.{item}" for item in (fromlist or ()))}
        if requested & forbidden:
            raise ImportError(
                f"Rust read tests require legacy code: {requested & forbidden}"
            )
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    shared = (
        Path(__file__).resolve().parents[1] / "common" / "database_backend_stubs.py"
    )
    helpers = runpy.run_path(str(shared))
    module = runpy.run_path(__file__)
    for is_async in (False, True):
        case = helpers["make_database_read_case"](is_async)
        assert module["_call_database_read"](case) == {"id": "db1", "_etag": "v1"}
        case.connection.ReadDatabase.assert_not_called()


def test_read_database_prepared_request_is_bodiless_rust():
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
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    assert settings_options(prepared)["timeout_seconds"] == 3.5


def test_read_database_prepared_preserves_original_option_headers_rust():
    """Every truthy option that legacy GetHeaders emits reaches the binding."""
    initial_headers = {"x-custom": "value"}
    options = {
        "initialHeaders": initial_headers,
        "maxItemCount": 10,
        "enableScanInQuery": True,
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

    assert all(
        wire_headers(prepared).get(key.lower()) == str(value)
        for key, value in (initial_headers).items()
    )
    assert wire_headers(prepared) is not initial_headers
    from azure.cosmos._helpers._request_settings import OPTION_HEADER_NAMES

    for option_key, option_value in options.items():
        if option_key not in ("initialHeaders", "sessionToken"):
            assert wire_headers(prepared)[OPTION_HEADER_NAMES[option_key]] == str(
                option_value
            )
    assert "x-ms-session-token" not in wire_headers(prepared)


@pytest.mark.parametrize(
    "option_key,header_name",
    [
        ("continuation", "x-ms-continuation"),
        ("contentType", "content-type"),
        ("enableScanInQuery", "x-ms-documentdb-query-enable-scan"),
        ("maxItemCount", "x-ms-max-item-count"),
        ("populateQueryMetrics", "x-ms-documentdb-populatequerymetrics"),
        ("sessionToken", "x-ms-session-token"),
        ("throughputBucket", "x-ms-cosmos-throughput-bucket"),
    ],
)
def test_read_database_prepared_omits_falsy_original_headers_rust(
    option_key, header_name
):
    """Prove empty Python-only options do not become request headers."""
    prepared = build_read_database_prepared("db1", {option_key: None})

    assert header_name not in wire_headers(prepared)


def test_read_database_prepared_preserves_original_id_stringification_rust():
    """Read keeps its own id rules: it stringifies and tolerates a trailing slash,
    where create validates."""
    assert build_read_database_prepared(123, {}).item_id == "123"
    assert build_read_database_prepared("db1/", {}).item_id == "db1"


@pytest.mark.parametrize("database_id", ["", "/", "///"])
def test_read_database_prepared_rejects_empty_normalized_id_rust(database_id):
    """Prove an empty database ID fails before a request is sent."""
    with pytest.raises(ValueError, match="Failed Parsing ResourceID from link: /dbs/"):
        build_read_database_prepared(database_id, {})


@pytest.mark.parametrize(
    "request_options,operation_kwargs,expected",
    [
        ({}, {}, True),
        ({}, {"timeout": 1.0}, True),
        ({}, {"connection_timeout": 2}, False),
        ({}, {"response_hook": object()}, True),
        ({"initialHeaders": {"x-custom": "value"}}, {}, True),
        ({"initialHeaders": {"Accept": "application/custom"}}, {}, False),
        ({"initialHeaders": {"CACHE-CONTROL": "max-age=60"}}, {}, False),
        ({"initialHeaders": {"User-Agent": "custom"}}, {}, False),
        ({"initialHeaders": {"X-MS-VERSION": "2018-12-31"}}, {}, False),
    ],
)
def test_read_database_rust_eligibility_never_drops_transport_kwargs_rust(
    request_options, operation_kwargs, expected
):
    """Unsupported transport settings make a Rust read ineligible, without enabling fallback."""
    assert is_read_database_rust_eligible(request_options, operation_kwargs) is expected


@pytest.mark.parametrize(
    "timeout", [0.5, 0, -1, float("-inf"), "1", float("nan"), float("inf")]
)
def test_read_database_rust_eligibility_rejects_bad_timeout_as_value_error_rust(
    timeout,
):
    """A bad timeout is a wrong value, so eligibility raises instead of answering "not eligible"."""
    with pytest.raises(ValueError, match="timeout must be None or a finite number"):
        is_read_database_rust_eligible({}, {"timeout": timeout})


def test_sync_read_database_routes_to_rust_and_parses_response_rust():
    """The database helper dispatches a read without a container lookup or legacy call."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _FakeBackend(
        BackendResponse(
            status_code=200,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
            body=b'{"id":"db1","_rid":"existing"}',
        )
    )
    hook_calls = []
    backend.get_container_metadata = MagicMock(
        side_effect=AssertionError("unexpected container lookup")
    )

    result = DatabaseHelper(connection, backend).read_database(
        "db1",
        {"throughputBucket": 7},
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
        kwargs={"timeout": 3.5},
    )

    assert result == {"id": "db1", "_rid": "existing"}
    assert backend.prepared.op == OP_READ_DATABASE
    assert backend.prepared.item_id == "db1"
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    assert settings_options(backend.prepared)["timeout_seconds"] == 3.5
    connection.ReadDatabase.assert_not_called()
    backend.get_container_metadata.assert_not_called()
    assert hook_calls == [
        ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "existing"})
    ]
    assert isinstance(result, CosmosDict)
    assert type(hook_calls[0][1]) is dict


def test_sync_read_database_maps_not_found_and_skips_hook_rust():
    """A not-found from the Rust engine still raises the typed not-found error."""
    backend = _FakeBackend(
        BackendResponse(
            status_code=404,
            headers=CaseInsensitiveDict({"x-ms-substatus": "0"}),
            body=b'{"message":"missing"}',
        )
    )
    hook_calls = []

    with pytest.raises(CosmosResourceNotFoundError):
        DatabaseHelper(
            SimpleNamespace(last_response_headers={}), backend
        ).read_database(
            "missing",
            {},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )

    assert not hook_calls


def test_sync_database_proxy_read_selects_rust_backend_rust():
    """The public sync proxy delegates its read through the stored backend."""
    backend = _FakeBackend(
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
    assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    connection.ReadDatabase.assert_not_called()


def test_sync_database_proxy_read_rejects_deprecated_session_token_rust():
    """Obsolete session-token usage fails before any request is sent."""
    backend = _FakeBackend(
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


@pytest.mark.parametrize(
    "option,key",
    [
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
    ],
)
@pytest.mark.parametrize(
    "source,other_source",
    [
        ("keyword", None),
        ("request_options", None),
        ("feed_options", None),
        ("request_options", "feed_options"),
        ("feed_options", "request_options"),
    ],
)
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_database_read_rejects_obsolete_and_socket_options_rust(
    database_read_case, option, key, source, other_source, value
):
    """Reject retired options before dispatch without changing caller dictionaries or cached properties."""
    case = database_read_case
    hook = MagicMock()
    kwargs = {option: value} if source == "keyword" else {source: {key: value}}
    if other_source is not None:
        kwargs[other_source] = {}
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match=option):
        _call_database_read(case, response_hook=hook, **kwargs)
    assert kwargs == original
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert case.proxy._properties["_etag"] == "old"


@pytest.mark.parametrize("value", [None, False, True])
def test_database_read_is_keyword_only_rust(database_read_case, value):
    """``read`` takes no positional arguments, so a stray one is a ``TypeError``
    rather than being quietly bound to the first keyword and changing what the
    call does. Nothing is sent to either engine.
    """
    with pytest.raises(TypeError):
        _call_database_read(database_read_case, value)
    database_read_case.backend.execute.assert_not_called()
    database_read_case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("source", ["request_options", "feed_options", "both"])
def test_database_read_options_are_unchanged_and_reusable_rust(
    database_read_case, source
):
    case = database_read_case
    options = {
        "throughputBucket": 4,
        "initialHeaders": {"x-my-app": "catalog"},
    }
    kwargs = {source if source != "both" else "request_options": options}
    if source == "both":
        kwargs["feed_options"] = {"throughputBucket": 9}
    original = deepcopy(kwargs)

    _call_database_read(
        case,
        **kwargs,
        timeout=3.5,
        throughput_bucket=7,
        etag="v1",
        match_condition=MatchConditions.IfModified,
    )
    assert kwargs == original
    assert settings_options(case.backend.prepared)["timeout_seconds"] == 3.5
    assert wire_headers(case.backend.prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    assert wire_headers(case.backend.prepared)["if-none-match"] == "v1"

    result = _call_database_read(case, **kwargs)
    assert result["id"] == "db1"
    assert kwargs == original
    assert settings_options(case.backend.prepared).get("timeout_seconds") is None
    assert wire_headers(case.backend.prepared)["x-ms-cosmos-throughput-bucket"] == "4"
    assert wire_headers(case.backend.prepared)["x-my-app"] == "catalog"
    assert "if-none-match" not in wire_headers(case.backend.prepared)
    assert case.backend.execute.call_count == 2
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("source", ["request_options", "feed_options"])
@pytest.mark.parametrize("invalid_kwargs", [{"timeout": 0.5}, {"etag": "v1"}])
def test_database_read_validation_preserves_caller_options_rust(
    database_read_case, source, invalid_kwargs
):
    case = database_read_case
    options = {"throughputBucket": 4}
    with pytest.raises(ValueError):
        _call_database_read(
            case, **{source: options}, throughput_bucket=7, **invalid_kwargs
        )
    assert options == {"throughputBucket": 4}
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert case.proxy._properties["_etag"] == "old"


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10, float(2**64 - 2048)])
def test_database_read_preserves_supported_options_and_refreshes_properties_rust(
    database_read_case, timeout
):
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
        case,
        timeout=timeout,
        throughput_bucket=7,
        initial_headers={"x-my-app": "catalog"},
    )
    assert isinstance(result, CosmosDict)
    assert result == {"id": "db1", "_etag": "v1"}
    assert case.proxy._properties is result
    prepared = case.backend.prepared
    assert prepared.op == OP_READ_DATABASE
    assert prepared.item_id == "db1"
    assert prepared.body_bytes == b""
    assert all(
        wire_headers(prepared).get(key.lower()) == str(value)
        for key, value in ({"x-my-app": "catalog"}).items()
    )
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == "7"
    assert settings_options(prepared).get("timeout_seconds") == timeout
    if timeout is None:
        assert Constants.OVERALL_TIMEOUT_SECONDS not in wire_headers(prepared)
    _call_database_read(case)
    assert case.backend.execute.call_count == 2
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize(
    "timeout",
    [
        False,
        True,
        0,
        -1,
        0.5,
        "10",
        float("nan"),
        float("inf"),
        -float("inf"),
        2**64 - 1,
        2**64,
        10**400,
    ],
    ids=[
        "false",
        "true",
        "zero",
        "negative",
        "subsecond",
        "string",
        "nan",
        "inf",
        "negative-inf",
        "rounds-out-of-range",
        "out-of-range",
        "overflow",
    ],
)
def test_database_read_invalid_timeout_never_reaches_a_transport_rust(
    database_read_case, timeout
):
    """A bad timeout is refused as a wrong value before anything is sent.

    The list covers booleans, zero, negatives, a value below one second, a
    string, the three non-finite floats, and values at or past the range the
    engine can hold. Each raises ``ValueError``: the value is wrong, so
    ``NotImplementedError`` ("Rust cannot do this") would mislead the customer.

    Neither engine is invoked, so an unusable deadline can never be rounded into
    a usable one behind the customer's back.
    """
    case = database_read_case
    with pytest.raises(ValueError, match="timeout must be None or a finite number"):
        _call_database_read(case, timeout=timeout)
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize(
    "kwargs,message",
    [
        (
            {"connection_timeout": 1},
            "connection_timeout.*ConnectionPoolOptions.connection_timeout",
        ),
        (
            {"connection_timeout": None},
            "connection_timeout.*ConnectionPoolOptions.connection_timeout",
        ),
        ({"unknown_option": True}, "unknown_option"),
        ({"initial_headers": {"User-Agent": "custom"}}, "initial_headers.*User-Agent"),
        (
            {"initial_headers": {"X-MS-VERSION": "custom"}},
            "initial_headers.*X-MS-VERSION",
        ),
        ({"initial_headers": {"Accept": "custom"}}, "initial_headers.*Accept"),
        (
            {"initial_headers": {"Cache-Control": "custom"}},
            "initial_headers.*Cache-Control",
        ),
        ({"request_options": {"timeout": 10}}, "timeout.*directly"),
        ({"feed_options": {"timeout": 10}}, "timeout.*directly"),
    ],
)
def test_database_read_unsupported_settings_never_fall_back_rust(
    database_read_case, kwargs, message
):
    """Unsupported arguments raise TypeError naming the setting before either backend runs."""
    case = database_read_case
    hook = MagicMock()
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match=message):
        _call_database_read(case, response_hook=hook, **kwargs)
    assert kwargs == original
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_database_read_rejects_non_callable_hook_before_dispatch_rust(
    database_read_case, hook
):
    case = database_read_case
    with pytest.raises(
        TypeError, match="read_database response_hook must be callable or None"
    ):
        _call_database_read(case, response_hook=hook)
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert case.proxy._properties["_etag"] == "old"


@pytest.mark.parametrize(
    "kind",
    [
        "function",
        "method",
        "partial",
        "callable",
        "partial-callable",
        "async-generator",
    ],
)
def test_database_read_rejects_async_hook_before_dispatch_rust(
    database_read_case, kind
):
    async def hook(_headers, _body):
        pytest.fail("An asynchronous response hook must not run")

    class AsyncHook:
        async def __call__(self, _headers, _body):
            pytest.fail("An asynchronous response hook must not run")

    async def generator_hook(_headers, body):
        pytest.fail("An asynchronous generator hook must not run")
        yield body

    callable_hook = AsyncHook()
    hooks = {
        "function": hook,
        "method": callable_hook.__call__,
        "partial": partial(hook),
        "callable": callable_hook,
        "partial-callable": partial(callable_hook),
        "async-generator": generator_hook,
    }
    case = database_read_case
    with pytest.raises(
        TypeError, match="read_database response_hook must be synchronous"
    ):
        _call_database_read(case, response_hook=hooks[kind])
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert case.proxy._properties["_etag"] == "old"


def test_database_read_hook_snapshot_is_isolated_and_falsey_callable_runs_rust(
    database_read_case,
):
    """Run even a falsey callable once and isolate its header snapshot from later changes."""
    case = database_read_case
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
    case.backend.execute.assert_called_once()
    case.connection.ReadDatabase.assert_not_called()
    assert "x-ms-cosmos-sdk-diagnostics" in calls[0]


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {}),
        (
            {"etag": "v1", "match_condition": MatchConditions.IfNotModified},
            {"If-Match": "v1"},
        ),
        (
            {"etag": "v1", "match_condition": MatchConditions.IfModified},
            {"If-None-Match": "v1"},
        ),
        ({"match_condition": MatchConditions.IfPresent}, {"If-Match": "*"}),
        ({"match_condition": MatchConditions.IfMissing}, {"If-None-Match": "*"}),
        (
            {"etag": "unused", "match_condition": MatchConditions.IfPresent},
            {"If-Match": "*"},
        ),
        (
            {"etag": "unused", "match_condition": MatchConditions.IfMissing},
            {"If-None-Match": "*"},
        ),
        ({"if_match": "v1"}, {"If-Match": "v1"}),
        ({"if_none_match": "v1"}, {"If-None-Match": "v1"}),
    ],
)
def test_database_read_preserves_conditional_headers_rust(
    database_read_case, kwargs, expected
):
    """Preserve conditional headers, ignoring an unnecessary ETag for wildcard conditions."""
    case = database_read_case
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_database_read(case, **kwargs)
    assert caught == []
    headers = wire_headers(case.backend.prepared)
    case.connection.ReadDatabase.assert_not_called()
    assert {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() in ("if-match", "if-none-match")
    } == {key.lower(): value for key, value in expected.items()}


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
def test_database_read_invalid_guards_fail_before_dispatch_rust(
    database_read_case, kwargs, error_type
):
    """Reject incomplete or malformed conditions before sending a request."""
    case = database_read_case
    with pytest.raises(error_type):
        _call_database_read(case, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize("failure_source", ["hook", "backend"])
@pytest.mark.parametrize(
    "error_type",
    [ValueError, ServiceRequestError, NotImplementedError, asyncio.CancelledError],
)
def test_database_read_exceptions_never_replay_or_replace_cached_properties_rust(
    database_read_case, failure_source, error_type
):
    """A failure in either the hook or the engine is raised as-is, with no retry and
    no damage to the cached properties.

    The same four error types are raised from two places: from the customer's
    own response hook, and from the engine itself. In every combination the
    exact exception object reaches the caller, rather than being wrapped or
    turned into a different type.

    The engine is called exactly once and the legacy path is never tried. A failed read must not be
    replayed on the other engine, which for the hook case would mean running the
    customer's code twice. The proxy also keeps its previous properties, so a
    failed read never leaves a half-updated view behind.
    """
    case = database_read_case
    error = error_type("read failed")
    hook = MagicMock(side_effect=error if failure_source == "hook" else None)
    if failure_source == "backend":
        case.backend.execute.side_effect = error
    with pytest.raises(error_type) as raised:
        _call_database_read(case, response_hook=hook)
    assert raised.value is error
    assert case.proxy._properties["_etag"] == "old"
    case.backend.execute.assert_called_once()
    case.connection.ReadDatabase.assert_not_called()
    assert hook.call_count == (1 if failure_source == "hook" else 0)


@pytest.mark.parametrize("status", [403, 404, 408, 412, 429, 500])
def test_database_read_service_errors_never_replay_rust(database_read_case, status):
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
    case.backend.responses = [
        BackendResponse(
            status_code=status,
            headers=CaseInsensitiveDict({"x-ms-activity-id": "failed-read"}),
            body=b'{"message":"read failed"}',
        )
    ]
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_database_read(
            case,
            etag="v1",
            match_condition=MatchConditions.IfNotModified,
            response_hook=hook,
        )
    assert raised.value.status_code == status
    if status == 404:
        assert isinstance(raised.value, CosmosResourceNotFoundError)
    assert wire_headers(case.backend.prepared)["if-match"] == "v1"
    assert case.proxy._properties["_etag"] == "old"
    hook.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.ReadDatabase.assert_not_called()


def test_database_read_not_modified_preserves_empty_response_and_hook_rust(
    database_read_case,
):
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
    case.backend.responses = [
        BackendResponse(
            status_code=304,
            headers=CaseInsensitiveDict({"etag": "v1"}),
            body=b"",
        )
    ]
    calls = []
    result = _call_database_read(
        case,
        etag="v1",
        match_condition=MatchConditions.IfModified,
        response_hook=lambda headers, body: calls.append((headers, body)),
    )
    assert result == {}
    assert result.get_response_headers()["etag"] == "v1"
    assert calls == [({"etag": "v1"}, None)]
    assert calls[0][0] is not result.get_response_headers()
    assert case.proxy._properties is result
    case.connection.ReadDatabase.assert_not_called()


def test_async_read_database_routes_to_rust():
    """Async database reads dispatch without a container lookup or legacy call."""

    async def run():
        """Confirm the async read helper sends the read to the Rust engine and fires the hook with the returned database body."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(side_effect=AssertionError("legacy read called")),
            last_response_headers={},
        )
        backend = _AsyncFakeBackend(
            BackendResponse(
                status_code=200,
                headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
                body=b'{"id":"db1","_rid":"existing"}',
            )
        )
        hook_calls = []
        backend.get_container_metadata = AsyncMock(
            side_effect=AssertionError("unexpected container lookup")
        )

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
        assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == "9"
        assert settings_options(backend.prepared)["timeout_seconds"] == 3.5
        connection.ReadDatabase.assert_not_awaited()
        backend.get_container_metadata.assert_not_called()
        assert hook_calls == [
            ({"x-ms-request-charge": "1.0"}, {"id": "db1", "_rid": "existing"})
        ]
        assert isinstance(result, CosmosDict)
        assert type(hook_calls[0][1]) is dict

    asyncio.run(run())


def test_async_read_database_maps_not_found_and_skips_hook_rust():
    """Async twin: a Rust 404 raises the typed error and runs no response hook.

    ``response_hook`` receives the properties of a database that was read. A 404
    means there are none, so calling the hook would hand the caller an error
    payload where they expect database properties.
    """

    async def run():
        """Confirm a Rust 404 response raises ``CosmosResourceNotFoundError`` and the hook is never called."""
        backend = _AsyncFakeBackend(
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
    "operation_kwargs,error,message",
    [
        # Bad timeouts are wrong values, so they raise ValueError.
        ({Constants.Kwargs.TIMEOUT: 0.5}, ValueError, "timeout must be"),
        ({Constants.Kwargs.TIMEOUT: 0}, ValueError, "timeout must be"),
        ({Constants.Kwargs.TIMEOUT: -1}, ValueError, "timeout must be"),
        ({Constants.Kwargs.TIMEOUT: "1"}, ValueError, "timeout must be"),
        # Transport keywords are consumed by the azure-core pipeline, which the
        # Rust path does not run.
        (
            {"connection_timeout": 2},
            TypeError,
            "connection_timeout.*ConnectionPoolOptions.connection_timeout",
        ),
    ],
)
def test_read_database_rejects_options_rust_cannot_honor_rust(
    operation_kwargs,
    error,
    message,
):
    """Unsupported reads never cross from Rust to legacy transport."""
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "legacy"}),
        last_response_headers={},
    )
    backend = _FakeBackend()

    with pytest.raises(error, match=message):
        DatabaseHelper(connection, backend).read_database(
            "db1",
            {},
            kwargs=dict(operation_kwargs),
        )

    assert backend.prepared is None
    connection.ReadDatabase.assert_not_called()


def test_read_database_rejects_driver_owned_initial_header_rust():
    """Driver-owned header overrides fail without a legacy request."""
    request_options = {"initialHeaders": {"Accept": "application/custom"}}
    connection = SimpleNamespace(
        ReadDatabase=MagicMock(return_value={"id": "db1", "_rid": "legacy"}),
        last_response_headers={},
    )
    backend = _FakeBackend()

    with pytest.raises(TypeError, match="initial_headers.*Accept"):
        DatabaseHelper(connection, backend).read_database("db1", request_options)

    assert backend.prepared is None
    connection.ReadDatabase.assert_not_called()


@pytest.mark.parametrize(
    "operation_kwargs,error,message",
    [
        ({Constants.Kwargs.TIMEOUT: 0.5}, ValueError, "timeout must be"),
        ({Constants.Kwargs.TIMEOUT: 0}, ValueError, "timeout must be"),
        ({Constants.Kwargs.TIMEOUT: -1}, ValueError, "timeout must be"),
        ({Constants.Kwargs.TIMEOUT: "1"}, ValueError, "timeout must be"),
        (
            {"connection_timeout": 2},
            TypeError,
            "connection_timeout.*ConnectionPoolOptions.connection_timeout",
        ),
    ],
)
def test_async_read_database_rejects_options_rust_cannot_honor_rust(
    operation_kwargs,
    error,
    message,
):
    """Async reads also reject unsupported calls without fallback."""

    async def run():
        """No backend receives an unsupported request."""
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "legacy"}),
            last_response_headers={},
        )
        backend = _AsyncFakeBackend()

        with pytest.raises(error, match=message):
            await AsyncDatabaseHelper(connection, backend).read_database(
                "db1",
                {},
                kwargs=dict(operation_kwargs),
            )

        assert backend.prepared is None
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_read_database_rejects_driver_owned_initial_header_rust():
    """Async driver-owned header overrides fail without fallback."""

    async def run():
        """Neither transport should receive this unsupported call."""
        request_options = {"initialHeaders": {"x-ms-version": "2018-12-31"}}
        connection = SimpleNamespace(
            ReadDatabase=AsyncMock(return_value={"id": "db1", "_rid": "legacy"}),
            last_response_headers={},
        )
        backend = _AsyncFakeBackend()

        with pytest.raises(TypeError, match="initial_headers.*x-ms-version"):
            await AsyncDatabaseHelper(connection, backend).read_database(
                "db1", request_options
            )

        assert backend.prepared is None
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_database_proxy_read_selects_rust_backend_rust():
    """The public async proxy delegates its read through the stored backend."""

    async def run():
        """Read via the public async proxy and confirm Rust serves the request, not the legacy connection."""
        backend = _AsyncFakeBackend(
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
        assert wire_headers(backend.prepared)["x-ms-cosmos-throughput-bucket"] == "9"
        connection.ReadDatabase.assert_not_awaited()

    asyncio.run(run())


def test_async_database_proxy_read_rejects_deprecated_session_token_rust():
    """The async proxy also rejects the obsolete token before any request is sent."""

    async def run():
        """No request is prepared for an obsolete option."""
        backend = _AsyncFakeBackend(
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


@pytest.mark.parametrize("name", ["read_database", "read_database_async"])
@pytest.mark.parametrize("remaining", [None, 0.125, 1.0])
@pytest.mark.parametrize("include_attempts", [False, True])
def test_database_read_native_binding_rejects_string_handle_rust(
    name, remaining, include_attempts
):
    """Reject string handles independently of the requested budget and diagnostics.

    Windows-emulator binding tests cover successful reads with real handles.
    """
    from azure.cosmos import _rust

    prepared = build_read_database_prepared("db1", {})
    with pytest.raises(TypeError, match="_DriverHandle"):
        getattr(_rust, name)(
            "unregistered-read-test-handle",
            prepared,
            timeout_seconds=remaining,
            include_attempts=include_attempts,
        )
