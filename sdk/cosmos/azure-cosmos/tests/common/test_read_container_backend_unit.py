# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container-read rules and real backend routing, with fake network responses."""
from common.typed_requests import wire_headers, settings_options, legacy_settings

import asyncio
import copy
import inspect
import json
import time
import warnings
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import exceptions
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_READ_CONTAINER
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from .test_delete_container_backend_unit import delete_case


@pytest.fixture(params=[False, True], ids=["rust", "legacy"])
def read_case(delete_case, request):
    """Build a container whose read can be run on either engine.

    Each test using this runs twice, once on the Rust path and once on legacy,
    with both wired to return the same properties and headers so switching
    engines does not change the response itself.

    The properties are deliberately nested -- a partition key holding a list of
    paths, and an indexing policy holding a list of dictionaries. A test can
    then prove a response hook's edits were kept out of the caller's result and
    out of the cached copy, which a shallow copy would not manage.

    The legacy stand-in asserts it is never handed the customer's
    ``response_hook``. The coordinator fires that itself, so passing it down
    would run the customer's callback twice.
    """
    case = delete_case
    case.legacy = request.param
    case.properties = {
        "id": "c1", "_rid": "rid1", "partitionKey": {"paths": ["/pk"], "kind": "Hash"},
        "indexingPolicy": {"indexingMode": "consistent", "excludedPaths": [{"path": "/hidden/*"}]},
    }
    case.headers = CaseInsensitiveDict({"etag": '"v1"', "x-ms-request-charge": "1", "x-ms-activity-id": "read"})
    case.backend.response = BackendResponse(
        status_code=200, headers=case.headers.copy(),
        body=json.dumps(case.properties).encode(), diagnostics="read trace",
    )
    if case.legacy:
        from azure.cosmos._backend.legacy import LEGACY_BACKEND
        from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND

        case.connection._backend = ASYNC_LEGACY_BACKEND if case.is_async else LEGACY_BACKEND

        def legacy_read(link, options, **kwargs):
            assert "response_hook" not in kwargs
            case.connection.last_response_headers = case.headers.copy()
            return CosmosDict(copy.deepcopy(case.properties), response_headers=case.headers.copy())

        read = legacy_read
    else:
        read = AssertionError("Rust container read entered legacy ReadContainer")

    case.connection.ReadContainer = (AsyncMock if case.is_async else MagicMock)(side_effect=read)
    case.container = case.database.get_container_client("c1")
    return case


def _read(case, *args, **kwargs):
    """Call ``container.read`` and wait for it if the async proxy is under test."""
    result = case.container.read(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    """Assert the read never happened on either engine and cached nothing.

    The third check is the one worth stating: a rejected read must not leave a
    stale or half-built entry in the container properties cache, which later
    calls would then trust.
    """
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.fixture
def metadata_read_case(read_case):
    cache = {}
    read_case.connection._container_properties_cache = cache
    read_case.connection._set_container_properties_cache.side_effect = cache.__setitem__
    return read_case


@pytest.mark.parametrize("with_deadline", [False, True])
def test_metadata_preload_accepts_internal_start_time_and_preserves_budget_rust(metadata_read_case, with_deadline):
    """Internal timing must not block a cold metadata read or become a wire header."""
    case = metadata_read_case
    deadline = time.monotonic() + 30 if with_deadline else None
    options = {Constants.OperationStartTime: time.time() - 1, "excludedLocations": ["West US"], "timeout": 20}
    if deadline is not None:
        options["_item_operation_deadline"] = deadline
    original = copy.deepcopy(options)

    def properties():
        result = case.container._get_properties_with_options(options)
        return asyncio.run(result) if inspect.isawaitable(result) else result

    assert properties()["_rid"] == "rid1"
    assert properties()["_rid"] == "rid1"
    assert options == original
    case.connection._set_container_properties_cache.assert_called_once()
    if case.legacy:
        case.backend.execute.assert_not_called()
        case.connection.ReadContainer.assert_called_once()
        call = case.connection.ReadContainer.call_args
        assert call.kwargs["options"]["excludedLocations"] == ["West US"]
        if deadline is None:
            assert call.kwargs[Constants.OperationStartTime] == original[Constants.OperationStartTime]
        else:
            assert call.kwargs["options"]["_item_operation_deadline"] == deadline
    else:
        case.connection.ReadContainer.assert_not_called()
        case.backend.execute.assert_called_once()
        call = case.backend.execute.call_args
        assert call.kwargs["deadline"] == deadline
        prepared = call.args[0]
        assert prepared.op == OP_READ_CONTAINER
        assert prepared.settings.excluded_locations == ("West US",)
        assert prepared.settings.timeout_seconds == 20
        assert "operationstarttime" not in {name.lower() for name in wire_headers(prepared)}


def test_expired_metadata_preload_budget_prevents_dispatch_rust(metadata_read_case):
    case = metadata_read_case
    options = {
        Constants.OperationStartTime: time.time(),
        "_item_operation_deadline": time.monotonic() - 1,
        "timeout": 20,
    }
    with pytest.raises(exceptions.CosmosClientTimeoutError):
        result = case.container._get_properties_with_options(options)
        if inspect.isawaitable(result):
            asyncio.run(result)
    _assert_no_dispatch(case)


def test_sync_async_read_parameter_contracts_match_rust():
    """The sync and async container reads take exactly the same parameters, so a
    customer porting code between them does not find an option missing or
    renamed on one side.
    """
    assert inspect.signature(ContainerProxy.read) == inspect.signature(AsyncContainerProxy.read)


@pytest.mark.parametrize("args", [(None,), (None, True), (None, True, True)])
def test_all_settings_require_keywords_rust(read_case, args):
    """Container read takes no positional arguments at all.

    One, two, and three positional values are each a ``TypeError``. Older code
    passed settings this way; accepting them now would bind a value to whatever
    argument happens to sit in that position. Nothing is read and nothing is
    cached.
    """
    with pytest.raises(TypeError):
        _read(read_case, *args)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("option,wire_option", [
    ("session_token", "sessionToken"), ("populate_query_metrics", "populateQueryMetrics"),
])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_obsolete_options_rejected_by_presence_rust(read_case, option, wire_option, source, value):
    """Retired options are rejected because they were passed at all, not because of
    what they were set to.

    Session token and query metrics raise ``TypeError`` for every value,
    including ``None`` and ``False``. Ignoring a falsey one would leave a
    customer believing the setting still applies. The hook does not fire and
    neither engine is called.
    """
    response_hook = MagicMock()
    kwargs = {option: value} if source == "keyword" else {source: {wire_option: value}}
    with pytest.raises(TypeError, match=option):
        _read(read_case, response_hook=response_hook, **kwargs)
    response_hook.assert_not_called()
    _assert_no_dispatch(read_case)




@pytest.mark.parametrize("quota", [None, False, True])
@pytest.mark.parametrize("statistics", [None, False, True])
def test_metadata_flags_and_none_timeout_preserve_backend_rust(read_case, quota, statistics):
    """The two metadata flags reach whichever engine is in use, in that engine's own
    form, and neither engine hands the call off to the other.

    On the Rust path the flags become request headers; on legacy they stay
    named options. Left unset, they are absent from the request entirely rather
    than sent as a default. On the Rust path a flag set to false is also left
    off, since asking for no extra metadata is the same as not asking.

    Passing no socket timeout is accepted as an absence rather than treated as a
    value, and the legacy call does not receive the argument at all.

    The read returns the container properties and fills the properties cache
    exactly once using the selected engine.
    """
    case = read_case
    result = _read(
        case, populate_quota_info=quota, populate_partition_key_range_statistics=statistics,
    )
    assert isinstance(result, CosmosDict)
    assert result == case.properties
    case.connection._set_container_properties_cache.assert_called_once()
    if case.legacy:
        case.backend.execute.assert_not_called()
        call = case.connection.ReadContainer.call_args
        options = call.kwargs["options"]
    else:
        case.connection.ReadContainer.assert_not_called()
        prepared = case.backend.execute.call_args.args[0]
        assert prepared.op == OP_READ_CONTAINER
        assert prepared.container_link == "dbs/db1/colls/c1"
        assert prepared.body_bytes == b""
        options = wire_headers(prepared)
    for name, value in [("populateQuotaInfo", quota), ("populatePartitionKeyRangeStatistics", statistics)]:
        if not case.legacy:
            name = {
                "populateQuotaInfo": "x-ms-documentdb-populatequotainfo",
                "populatePartitionKeyRangeStatistics": "x-ms-documentdb-populatepartitionstatistics",
            }[name]
        if value is None or (not case.legacy and value is False):
            assert name not in options
        else:
            assert str(options[name]).lower() == str(value).lower()


@pytest.mark.parametrize("kwargs,expected", [
    ({}, None),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfNotModified}, ("IfMatch", '"v1"')),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfModified}, ("IfNoneMatch", '"v1"')),
    ({"etag": "unused", "match_condition": MatchConditions.IfPresent}, ("IfMatch", "*")),
    ({"etag": "unused", "match_condition": MatchConditions.IfMissing}, ("IfNoneMatch", "*")),
])
def test_conditions_preserved_without_unused_etag_fallback_rust(read_case, kwargs, expected):
    """Conditional reads carry the customer's condition on both engines, with no
    warning and no change of engine.

    An etag with a not-modified condition becomes a match condition; with a
    modified condition it becomes a none-match condition. A presence or absence
    condition becomes the wildcard form, and the etag passed alongside it is
    ignored, since the condition does not depend on a version.

    That last pair is why the test is named for an unused etag: ignoring the
    value is correct, but doing so silently while also warning, or while
    quietly moving the call to the other engine, would not be. No warning is
    raised.
    """
    case = read_case
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter("always")
        _read(case, **kwargs)
    assert not notices
    if case.legacy:
        call = case.connection.ReadContainer.call_args
        assert "etag" not in call.kwargs
        assert call.kwargs["options"].get("accessCondition") == (
            {"type": expected[0], "condition": expected[1]} if expected else None
        )
    else:
        case.connection.ReadContainer.assert_not_called()
        conditions = case.backend.execute.call_args.args[0].settings.item
        assert conditions.if_match == (expected[1] if expected and expected[0] == "IfMatch" else None)
        assert conditions.if_none_match == (expected[1] if expected and expected[0] == "IfNoneMatch" else None)


@pytest.mark.parametrize("kwargs,error", [
    ({"etag": "v1"}, ValueError),
    ({"match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": MatchConditions.IfModified}, ValueError),
    ({"match_condition": "invalid"}, TypeError),
])
def test_invalid_conditions_do_not_dispatch_rust(read_case, kwargs, error):
    """A condition that is incomplete or not a real match condition stops the read.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a match condition at all is a ``TypeError``. Sending
    any of them would produce an unconditional read for a customer who believed
    theirs was guarded. Nothing is read and nothing is cached.
    """
    with pytest.raises(error):
        _read(read_case, **kwargs)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("timeout", [None, 1, 1.25, 10])
def test_supported_timeout_rust(read_case, timeout):
    """A usable deadline reaches the Rust request in seconds, exactly as given --
    whole numbers, fractions, and no deadline at all. Rounding it on the way
    through would quietly give the customer a different limit than they set.
    """
    case = read_case
    _read(case, timeout=timeout)
    if not case.legacy:
        options = settings_options(case.backend.execute.call_args.args[0])
        assert options.get("timeout_seconds") == timeout
        case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": float("nan")},
    {"timeout": float("inf")}, {"timeout": "10"},
    {"connection_timeout": 2}, {"connection_timeout": None},
    {"consistency_level": "Unknown"},
    {Constants.OperationStartTime: 123, "unsupported_option": True},
    {"initial_headers": {"User-Agent": "custom"}},
])
def test_unsupported_rust_settings_never_replay_rust(read_case, kwargs):
    """Settings the Rust path cannot honor raise there, and still work on legacy.

    The list covers deadlines that are too small, false, not a number, or a
    string, a socket connect timeout, an unknown keyword, and a user agent the
    driver owns.

    On the Rust path each raises ``TypeError`` naming the method, with
    nothing sent and nothing cached. A bad
    deadline is a wrong value, so it raises ``ValueError`` on both paths. On the
    legacy path the other settings simply succeed, because they are part of
    what that path offers.

    Both halves matter: a customer must not be moved between engines without
    asking, and must not lose a working feature by staying where they are.
    """
    case = read_case
    if "timeout" in kwargs:
        with pytest.raises(ValueError, match="timeout must be"):
            _read(case, **kwargs)
        _assert_no_dispatch(case)
        return
    if case.legacy:
        _read(case, **kwargs)
        case.backend.execute.assert_not_called()
        return
    with pytest.raises(TypeError, match="ContainerProxy.read"):
        _read(case, **kwargs)
    _assert_no_dispatch(case)


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize("option,value", [
    ("raw_request_hook", None),  # Closed gap 6.
    ("raw_response_hook", False),  # Closed gap 7.
    ("connection_verify", False),  # Closed gap 10.
    ("transport", None),
    ("proxies", {}),
    ("availability_strategy", {"threshold_steps_ms": 10}),  # Closed gap 14.
    ("retry_write", 0),  # Closed gap 13: the driver owns write retry policy.
])
def test_closed_gap_settings_raise_type_error_without_dispatch_rust(read_case, source, option, value):
    wire_option = "availabilityStrategy" if option == "availability_strategy" else option
    kwargs = {option: value} if source == "keyword" else {source: {wire_option: value}}
    hook = MagicMock()
    with pytest.raises(TypeError):
        _read(read_case, response_hook=hook, **kwargs)
    hook.assert_not_called()
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
@pytest.mark.parametrize("source", ["request_options", "feed_options", "initial_headers"])
def test_unknown_consistency_raises_value_error_from_native_binding_rust(read_case, source):
    from azure.cosmos import _rust

    case = read_case
    method = _rust.read_container_async if case.is_async else _rust.read_container
    case.backend.execute.side_effect = lambda prepared, **kwargs: method(
        driver_handle="invalid-driver-handle", prepared=prepared,
    )
    kwargs = {
        "request_options": {"request_options": {"consistencyLevel": "Unknown"}},
        "feed_options": {"feed_options": {"consistencyLevel": "Unknown"}},
        "initial_headers": {"initial_headers": {"x-ms-consistency-level": "Unknown"}},
    }[source]
    with pytest.raises(ValueError, match="per-call consistency"):
        _read(case, **kwargs)
    case.backend.execute.assert_called_once()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
@pytest.mark.parametrize("status,body", [(200, b"{}"), (304, b"")])
def test_empty_read_response_hook_preserves_not_modified_none_rust(read_case, status, body):
    case = read_case
    case.backend.response = BackendResponse(
        status_code=status, headers=case.headers.copy(), body=body,
    )
    received = []

    def response_hook(headers, properties):
        received.append(properties)
        headers["etag"] = "changed"

    result = _read(case, response_hook=response_hook)
    assert isinstance(result, CosmosDict)
    assert result == {}
    assert len(received) == 1
    if status == 304:
        assert received[0] is None
    else:
        assert received[0] == {}
        assert received[0] is not result
    assert result.get_response_headers()["etag"] == '"v1"'
    assert case.connection.last_response_headers["etag"] == '"v1"'
    case.backend.execute.assert_called_once()
    case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
@pytest.mark.parametrize("warm_cache", [False, True], ids=["cold-cache", "warm-cache"])
def test_not_modified_read_preserves_metadata_cache_rust(metadata_read_case, warm_cache):
    case = metadata_read_case
    cache = case.connection._container_properties_cache
    success = case.backend.response
    if warm_cache:
        _read(case)
    original_cache = copy.deepcopy(cache)
    case.connection._set_container_properties_cache.reset_mock()
    case.backend.execute.reset_mock()
    case.backend.response = BackendResponse(
        status_code=304, headers=case.headers.copy(), body=b"",
    )

    result = _read(case, etag='"v1"', match_condition=MatchConditions.IfModified)

    assert result == {}
    assert result.get_response_headers()["etag"] == '"v1"'
    assert cache == original_cache
    case.connection._set_container_properties_cache.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.ReadContainer.assert_not_called()

    case.backend.response = success
    case.backend.execute.reset_mock()
    properties = case.container._get_properties()
    if case.is_async:
        properties = asyncio.run(properties)
    assert properties["_rid"] == case.properties["_rid"]
    assert properties["partitionKey"] == case.properties["partitionKey"]
    assert case.backend.execute.call_count == (0 if warm_cache else 1)


@pytest.mark.parametrize("response_hook", [False, 1, "not-callable"])
def test_noncallable_response_hook_is_rejected_before_dispatch_rust(read_case, response_hook):
    with pytest.raises(TypeError, match="response_hook must be callable or None"):
        _read(read_case, response_hook=response_hook)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("hook_kind", ["function", "callable", "partial", "async-generator"])
def test_async_response_hook_is_rejected_before_dispatch_rust(read_case, hook_kind):
    async def hook(headers, properties):
        raise AssertionError("Async hook must not execute")

    class AsyncHook:
        async def __call__(self, headers, properties):
            raise AssertionError("Async hook must not execute")

    async def generator_hook(_headers, properties):
        yield properties

    response_hook = {
        "function": hook,
        "callable": AsyncHook(),
        "partial": partial(hook),
        "async-generator": generator_hook,
    }[hook_kind]
    with pytest.raises(TypeError, match="response_hook must be synchronous"):
        _read(read_case, response_hook=response_hook)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
def test_not_modified_hook_error_is_not_retried_or_cached_rust(read_case):
    case = read_case
    case.backend.response = BackendResponse(
        status_code=304, headers=case.headers.copy(), body=b"",
    )
    error = RuntimeError("customer hook failed")

    def fail(headers, properties):
        assert properties is None
        raise error

    response_hook = MagicMock(side_effect=fail)
    with pytest.raises(RuntimeError) as caught:
        _read(case, response_hook=response_hook)
    assert caught.value is error
    response_hook.assert_called_once()
    case.backend.execute.assert_called_once()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


def test_response_hook_cannot_mutate_results_or_cached_properties_rust(read_case):
    """A response hook cannot reach back into the result or the cached properties,
    however deeply it digs.

    The hook edits the headers, a top-level field, a path inside the partition
    key, a path inside the indexing policy, and the headers hanging off the
    properties. It also returns a value, which is ignored -- a hook reports, it
    does not replace the result.

    None of it lands. The caller still gets the real properties and etag, the
    client's record still shows the real request charge, and the cached
    partition key is untouched. The cache is the sharpest edge: a corrupted
    partition key there would misroute later requests for every caller sharing
    the client.
    """
    case = read_case
    received = []

    def response_hook(headers, properties):
        received.append(properties)
        headers["x-ms-request-charge"] = "changed"
        properties["id"] = "changed"
        properties["partitionKey"]["paths"][0] = "/changed"
        properties["indexingPolicy"]["excludedPaths"][0]["path"] = "/changed/*"
        properties.get_response_headers()["etag"] = "changed"
        return {"id": "ignored"}

    result = _read(case, response_hook=response_hook)
    assert len(received) == 1 and received[0] is not result
    assert result == case.properties
    assert result.get_response_headers()["etag"] == '"v1"'
    assert case.connection.last_response_headers["x-ms-request-charge"] == "1"
    cached = case.connection._set_container_properties_cache.call_args.args[1]
    assert cached["partitionKey"] == case.properties["partitionKey"]


def test_false_valued_response_hook_is_called_once_rust(read_case):
    """A hook that reports itself as false when tested as a boolean still runs, once.

    It is callable, so it must be called; deciding by truth-test would skip it.
    Returning false from it changes nothing either. What it receives equals the
    result but is not the same object, so it cannot alter what the caller gets.
    """
    calls = []

    class ResponseHook:
        def __bool__(self):
            return False

        def __call__(self, headers, properties):
            calls.append((headers, properties))
            return False

    result = _read(read_case, response_hook=ResponseHook())
    assert len(calls) == 1
    assert calls[0][1] == result and calls[0][1] is not result


@pytest.mark.parametrize("error_type", [ValueError, NotImplementedError, exceptions.CosmosResourceNotFoundError])
def test_response_hook_error_is_not_retried_or_cached_rust(read_case, error_type):
    """When the customer's hook raises, the read is not repeated and nothing is
    cached.

    The exact exception reaches the caller and the engine was called once. The
    not-found case is the trap: an error type the SDK normally interprets as a
    real service reply, raised here from customer code. Treating it as one would
    turn a broken callback into a wrong answer about whether the container
    exists.

    The properties cache stays empty, so a call that did not finish cleanly
    leaves nothing behind for later calls to trust.
    """
    case = read_case
    error = (error_type(status_code=404, message="response hook failed")
             if error_type is exceptions.CosmosResourceNotFoundError else error_type("response hook failed"))
    response_hook = MagicMock(side_effect=error)
    with pytest.raises(error_type) as caught:
        _read(case, response_hook=response_hook)
    assert caught.value is error
    response_hook.assert_called_once()
    case.connection._set_container_properties_cache.assert_not_called()
    (case.connection.ReadContainer if case.legacy else case.backend.execute).assert_called_once()


@pytest.mark.parametrize("status", [403, 404, 412])
def test_service_errors_have_no_success_response_hook_rust(read_case, status):
    """A failed read raises with its status and never reports success.

    Forbidden, not-found, and precondition-failed are each raised on both
    engines with the status preserved, and not-found keeps its specific type so
    a customer can catch it to decide whether to create the container.

    The hook does not fire, since there is no successful response to report, and
    nothing is written to the properties cache. On the Rust path the legacy read
    is never tried as a second attempt.
    """
    case = read_case
    response_hook = MagicMock()
    if case.legacy:
        error_type = exceptions.CosmosResourceNotFoundError if status == 404 else exceptions.CosmosHttpResponseError
        case.connection.ReadContainer.side_effect = error_type(status_code=status, message="read failed")
    else:
        case.backend.response = BackendResponse(
            status_code=status, headers=case.headers.copy(), body=b'{"message":"read failed"}',
        )
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        _read(case, response_hook=response_hook)
    assert caught.value.status_code == status
    response_hook.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    if not case.legacy:
        case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
def test_binding_failure_never_replays_rust(read_case):
    """If the Rust engine reports it cannot carry out the read, the call fails there
    rather than being retried on legacy.

    A capability failure means the request was never satisfied, so a customer
    must be told, not quietly served by a different engine with different
    retries and diagnostics. Nothing is cached.

    Only the Rust fixture is applicable to a Rust binding failure.
    """
    case = read_case
    case.backend.execute.side_effect = NotImplementedError("binding capability")
    with pytest.raises(NotImplementedError):
        _read(case)
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("read_case", [False], indirect=True, ids=["rust"])
@pytest.mark.parametrize("delete_case", ["async"], indirect=True)
def test_async_cancellation_is_not_replayed_rust(read_case):
    """A cancelled async read stays cancelled.

    Cancellation is the customer or their framework asking the work to stop.
    Catching it and retrying on the legacy path would keep running work that was
    told to end, and would stop the cancellation unwinding. Nothing is cached.

    Runs only for the async Rust combination, which is the only place this can
    happen.
    """
    case = read_case
    case.backend.execute.side_effect = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        _read(case)
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
