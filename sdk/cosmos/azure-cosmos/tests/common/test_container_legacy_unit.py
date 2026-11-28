# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Temporary container legacy comparisons and retiring connection-router tests.

Run explicitly with --include-legacy-tests. Maintained Rust coverage and shared
stand-ins do not import this module.
"""

from __future__ import annotations
import asyncio
import json
import warnings
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict
from azure.cosmos import http_constants
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.operations import (
    OP_CREATE_CONTAINER,
    OP_LIST_CONTAINERS,
    OP_QUERY_CONTAINERS,
    OP_READ_CONTAINER,
)
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._container_operations import ContainerHelper
from azure.cosmos._helpers._response_parse import parse_backend_response
from azure.cosmos._helpers._client_context import CosmosClientContext
from common.typed_requests import flatten_options_to_headers
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)
from common.container_backend_stubs import (
    _call_container_create,
    _call_get_or_create,
    make_container_create_case,
    make_container_get_or_create_case,
)
from common.container_feed_stubs import (
    _FakePagedBackend,
    _AsyncFakePagedBackend,
    _new_sync_connection,
    _new_async_connection,
)


@pytest.fixture(params=["sync", "async"])
def container_create_case(request):
    case = make_container_create_case(request.param == "async")
    case.legacy_backend = (
        ASYNC_LEGACY_BACKEND if request.param == "async" else LEGACY_BACKEND
    )
    return case


@pytest.fixture(params=[False, True], ids=["existing", "missing"])
def container_get_or_create_case(container_create_case, request):
    return make_container_get_or_create_case(container_create_case, request.param)


_COLLECTION = http_constants.ResourceType.Collection


@pytest.mark.parametrize(
    "method", ["create_container", "create_container_if_not_exists"]
)
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_container_create_rejects_obsolete_keywords_legacy(
    container_create_case, method, option, value
):
    """Retired options are refused on both create methods, both engines, and every value.

    Session token and query metrics no longer do anything. Passing one raises
    ``TypeError`` naming it, even when the value is ``None`` or ``False``,
    because it is the presence of the option that signals a stale expectation.

    Nothing is created and the customer's hook never runs, so the refusal cannot
    be mistaken for a call that partly happened.
    """
    case = container_create_case
    case.connection._backend = case.legacy_backend
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _call_container_create(
            case,
            "c1",
            PartitionKey(path="/pk"),
            method=method,
            response_hook=hook,
            **{option: value},
        )
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize(
    "method", ["create_container", "create_container_if_not_exists"]
)
@pytest.mark.parametrize(
    "args, kwargs, message",
    [
        ((), {}, "missing required argument: 'id'"),
        ((), {"partition_key": None}, "missing required argument: 'id'"),
        ((), {"id": "c1"}, "missing required argument: 'partition_key'"),
        (("c1",), {}, "missing required argument: 'partition_key'"),
        (
            ("c1",),
            {"id": "c1", "partition_key": None},
            "multiple values for argument 'id'",
        ),
        (("c1", None), {"id": "other"}, "multiple values for argument 'id'"),
        (
            ("c1", None),
            {"partition_key": None},
            "multiple values for argument 'partition_key'",
        ),
        (
            ("c1", None),
            {"partition_key": PartitionKey(path="/pk")},
            "multiple values for argument 'partition_key'",
        ),
        (("c1", None, {}), {}, "Unexpected positional parameters"),
    ],
)
def test_container_create_invalid_argument_binding_fails_before_dispatch_legacy(
    container_create_case, method, args, kwargs, message
):
    """Calls that do not match the signature fail before anything is created, with a
    message naming the method and the problem.

    Nine shapes are covered: nothing at all, a partition key with no name, a name
    with no partition key, each of the two given twice, and settings passed by
    position. Each error names the method the customer called, so the same
    wording does not appear for both create methods.

    The caller's keyword dictionary is unchanged, so argument parsing reads
    rather than consumes.
    """
    case = container_create_case
    case.connection._backend = case.legacy_backend
    hook = MagicMock()
    original_kwargs = dict(kwargs)
    with pytest.raises(TypeError) as raised:
        _call_container_create(case, *args, **kwargs, method=method, response_hook=hook)
    assert "{}()".format(method) in str(raised.value)
    assert message in str(raised.value)
    assert kwargs == original_kwargs
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_preserves_required_arguments_and_return_shapes_legacy(
    container_create_case, return_properties, positional_count
):
    """A successful create returns the same thing however the arguments were passed
    and whichever engine ran it.

    The name and partition key are given by position, by keyword, and split
    between the two. In every case the returned proxy points at this database's
    container and carries the shared item context, so it can be used to read and
    write items straight away.

    Asking for the properties back returns a pair rather than a proxy alone, with
    the request charge still attached so the customer can account for the call.

    The properties cache is written exactly once, never twice and never zero
    times. Only the chosen engine runs, and the legacy route is not handed the
    socket-level timeout that does not belong in its options.
    """
    case = container_create_case
    case.connection._backend = case.legacy_backend
    args = ("c1", PartitionKey(path="/pk"))
    kwargs = dict(
        zip(("id", "partition_key")[positional_count:], args[positional_count:])
    )
    result = _call_container_create(
        case,
        *args[:positional_count],
        **kwargs,
        return_properties=return_properties,
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy._client_context is case.client_context
    assert proxy.container_link == "dbs/db1/colls/c1"
    if return_properties:
        assert len(result) == 2
        assert isinstance(result[1], CosmosDict)
        assert result[1]["id"] == proxy.id
        assert result[1].get_response_headers()["x-ms-request-charge"] == "5.25"
    case.connection._set_container_properties_cache.assert_called_once()
    case.backend.execute.assert_not_called()


def test_container_create_keeps_isolated_hook_headers_and_falsey_callable_legacy(
    container_create_case,
):
    """A hook that reports itself as false still runs, and the headers it is handed
    are its own copy.

    Being callable is what makes something a hook, not being true, so a hook
    object that says it is false is still invoked exactly once.

    It is given a copy of the properties the caller receives, so the two views agree.
    The headers are a separate copy: the hook changes the request charge and
    neither the properties nor the client's own record of the last response
    headers moves. A hook meant for logging must not be able to rewrite what the
    customer sees.
    """
    case = container_create_case
    case.connection._backend = case.legacy_backend
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert headers["X-MS-REQUEST-CHARGE"] == "5.25"
            assert isinstance(body, CosmosDict)
            calls.append((headers, body))
            headers["x-ms-request-charge"] = "changed"
            assert body.get_response_headers()["x-ms-request-charge"] == "5.25"

    proxy, properties = _call_container_create(
        case,
        "c1",
        PartitionKey(path="/pk"),
        return_properties=True,
        response_hook=Hook(),
    )
    assert len(calls) == 1
    assert calls[0][1] is not properties
    assert calls[0][1] == properties
    assert proxy.id == properties["id"]
    assert properties.get_response_headers()["x-ms-request-charge"] == "5.25"
    assert calls[0][0] is not case.connection.last_response_headers


@pytest.mark.parametrize("outcome", ["create", "existing", "missing"])
@pytest.mark.parametrize("return_properties", [False, True])
def test_container_creation_hook_cannot_mutate_result_or_cached_partition_key_legacy(
    container_create_case,
    outcome,
    return_properties,
):
    case = container_create_case
    original = {
        "id": "c1",
        "_rid": "rid1",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
    }
    properties = CosmosDict(
        json.loads(json.dumps(original)),
        response_headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
    )
    case.connection.CreateContainer.return_value = properties
    mock_type = (
        AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    )
    case.connection.ReadContainer = mock_type(return_value=properties)
    response = BackendResponse(
        status_code=201 if outcome != "existing" else 200,
        headers=properties.get_response_headers(),
        body=json.dumps(original).encode(),
    )
    case.backend.execute.side_effect = [response]
    if outcome == "missing":
        case.connection.ReadContainer.side_effect = CosmosResourceNotFoundError(
            status_code=404
        )
        case.backend.execute.side_effect = [
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'),
            response,
        ]
    case.connection._backend = case.legacy_backend
    seen = []

    def hook(headers, body):
        assert isinstance(body, CosmosDict)
        assert body == original
        assert headers["X-MS-REQUEST-CHARGE"] == "5.25"
        seen.append(body)
        body["id"] = "hook-id"
        body["partitionKey"]["paths"][0] = "/hook-key"
        headers["X-MS-REQUEST-CHARGE"] = "changed"

    result = _call_container_create(
        case,
        "c1",
        PartitionKey(path="/pk"),
        method=(
            "create_container"
            if outcome == "create"
            else "create_container_if_not_exists"
        ),
        return_properties=return_properties,
        response_hook=hook,
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy.container_link == "dbs/db1/colls/c1"
    case.connection._set_container_properties_cache.assert_called_once()
    link, cached = case.connection._set_container_properties_cache.call_args.args
    assert link == proxy.container_link
    assert cached["partitionKey"] == original["partitionKey"]
    assert len(seen) == 1
    seen[0]["partitionKey"]["paths"].append("/later-edit")
    assert cached["partitionKey"] == original["partitionKey"]
    if return_properties:
        assert result[1] == original
        assert result[1] is not seen[0]
        assert result[1].get_response_headers()["x-ms-request-charge"] == "5.25"
    assert properties == original
    case.backend.execute.assert_not_called()
    assert case.connection.CreateContainer.call_count == int(outcome != "existing")


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
def test_container_create_preserves_conditional_headers_legacy(
    container_create_case, kwargs, expected
):
    """Conditions become the right request headers on both engines, silently.

    Nine cases: no condition at all, an etag with not-modified and with modified,
    the two wildcard forms alone, the two wildcard forms with an etag alongside
    that is correctly ignored, and the older explicit match headers, which are
    still accepted and produce the same result as the modern spelling.

    No warning is raised in any of them, including where the etag is ignored. A
    warning there would send the customer looking for a problem that does not
    exist.
    """
    case = container_create_case
    case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_container_create(case, "c1", PartitionKey(path="/pk"), **kwargs)
    assert caught == []
    call = case.connection.CreateContainer.call_args
    headers = flatten_options_to_headers(call.kwargs["options"])
    assert "etag" not in call.kwargs
    assert {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() in ("if-match", "if-none-match")
    } == {key.lower(): value for key, value in expected.items()}


def test_container_get_or_create_still_creates_after_404_legacy(container_create_case):
    """When the container is not there, get-or-create goes on to create it.

    This is the whole point of the method: the read comes back not-found, and
    that is the signal to create rather than an error to report. On the Rust
    path that means two requests, the second of them a create; on legacy it
    means the create call runs once.

    The legacy create also has to go out without the retired session token and
    query metrics options, which older code used to put there by habit.
    """
    case = container_create_case
    missing = CosmosResourceNotFoundError(status_code=404, message="missing")
    mock_type = (
        AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    )
    case.connection.ReadContainer = mock_type(side_effect=missing)
    case.connection._backend = case.legacy_backend
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = _call_container_create(
            case,
            "c1",
            PartitionKey(path="/pk"),
            method="create_container_if_not_exists",
        )
    assert result.id == "c1"
    case.connection.CreateContainer.assert_called_once()
    assert (
        "sessionToken"
        not in case.connection.CreateContainer.call_args.kwargs["options"]
    )
    assert (
        "populateQueryMetrics"
        not in case.connection.CreateContainer.call_args.kwargs["options"]
    )


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_get_or_create_preserves_shapes_and_existing_settings_legacy(
    container_get_or_create_case, return_properties, positional_count
):
    """Get-or-create returns the same shape whether the container was found or
    created, and never rewrites one that already exists.

    The arguments are passed by position, by keyword, and split between the two,
    and the result is asked for both ways. In every case the proxy points at
    this database's container and carries the shared item context.

    The important guarantee is what happens when the container is already there:
    the properties handed back are the *existing* ones, still carrying the
    original partition key path and time to live, not the values passed to this
    call. A customer calling this at startup must not have their live container
    silently reshaped.

    The request charge also tells the two cases apart, so the hook sees the
    charge for whichever request actually ran.

    Settings meant for the create must not leak into the read: throughput is
    absent from the read on both engines, since asking to provision throughput
    while merely looking is meaningless and could be rejected. The deadline and
    the customer's own header, by contrast, apply to both steps. The properties
    cache is written once even when two requests were made.
    """
    case = container_get_or_create_case
    case.connection._backend = case.legacy_backend
    args = ("c1", PartitionKey(path="/pk"))
    kwargs = dict(
        zip(("id", "partition_key")[positional_count:], args[positional_count:])
    )
    hook = MagicMock()
    result = _call_container_create(
        case,
        *args[:positional_count],
        **kwargs,
        method="create_container_if_not_exists",
        default_ttl=99,
        offer_throughput=400,
        return_properties=return_properties,
        response_hook=hook,
        timeout=10,
        initial_headers={"x-company-trace": "setup"},
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy._client_context is case.client_context
    assert proxy.container_link == "dbs/db1/colls/c1"
    hook.assert_called_once()
    properties = hook.call_args.args[1]
    assert hook.call_args.args[0]["x-ms-request-charge"] == (
        "5.25" if case.missing else "2"
    )
    if return_properties:
        assert result[1] is not properties
        assert result[1] == properties
        assert isinstance(properties, CosmosDict)
    if not case.missing:
        assert properties["partitionKey"]["paths"] == ["/original"]
        assert properties["defaultTtl"] == 10
    case.connection._set_container_properties_cache.assert_called_once()
    case.backend.execute.assert_not_called()
    read = case.connection.ReadContainer.call_args
    assert "offerThroughput" not in read.kwargs["options"]
    assert "response_hook" not in read.kwargs
    assert 0 < read.kwargs["timeout"] <= 10
    assert case.connection.CreateContainer.call_count == int(case.missing)
    if case.missing:
        create = case.connection.CreateContainer.call_args
        assert create.kwargs["collection"]["defaultTtl"] == 99
        assert create.kwargs["options"]["offerThroughput"] == 400
        assert 0 < create.kwargs["timeout"] <= read.kwargs["timeout"]
        assert create.kwargs["options"]["_item_operation_deadline"] == (
            read.kwargs["options"]["_item_operation_deadline"]
        )


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": "invalid"}, TypeError),
    ],
)
def test_container_get_or_create_validates_conditions_before_read_legacy(
    container_get_or_create_case, kwargs, error
):
    """A malformed condition is rejected before the read, not after it.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. All three
    are caught before anything goes out, so a call that was never going to work
    does not cost a request or leave the cache holding properties from it.
    """
    case = container_get_or_create_case
    case.connection._backend = case.legacy_backend
    with pytest.raises(error):
        _call_get_or_create(case, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        (
            {"match_condition": MatchConditions.IfModified, "etag": '"v1"'},
            ("If-None-Match", '"v1"'),
        ),
        (
            {"match_condition": MatchConditions.IfNotModified, "etag": '"v1"'},
            ("If-Match", '"v1"'),
        ),
        (
            {"match_condition": MatchConditions.IfMissing, "etag": "unused"},
            ("If-None-Match", "*"),
        ),
        (
            {"match_condition": MatchConditions.IfPresent, "etag": "unused"},
            ("If-Match", "*"),
        ),
    ],
)
def test_container_get_or_create_forwards_conditions_without_ignored_warnings_legacy(
    container_get_or_create_case, kwargs, expected
):
    """A valid condition is attached to every request the call makes, on both engines,
    without warning.

    All four forms are covered. What is specific to get-or-create is that the
    condition must ride on *both* steps when the container turns out to be
    missing -- the read and the create that follows. Dropping it from the second
    would leave the create unguarded, which is exactly the step where a
    concurrent caller may have created the container in between.
    """
    case = container_get_or_create_case
    case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_get_or_create(case, **kwargs)
    assert not caught
    calls = [case.connection.ReadContainer.call_args]
    if case.missing:
        calls.append(case.connection.CreateContainer.call_args)
    expected_condition = {
        "type": "IfNoneMatch" if expected[0] == "If-None-Match" else "IfMatch",
        "condition": expected[1],
    }
    for call in calls:
        assert call.kwargs["options"]["accessCondition"] == expected_condition
        assert "etag" not in call.kwargs


@pytest.mark.parametrize(
    "error",
    [
        CosmosResourceNotFoundError(status_code=404, message="callback failure"),
        CosmosResourceExistsError(status_code=409, message="callback failure"),
        ValueError("callback failure"),
    ],
)
def test_container_get_or_create_does_not_interpret_hook_errors_as_missing_legacy(
    container_get_or_create_case, error
):
    """A not-found raised by the customer's own hook is not mistaken for the
    container being absent.

    This is the trap unique to this method. Get-or-create decides what to do next
    by catching not-found from the read. The hook runs afterwards, in customer
    code, and if it happens to raise the same error type, code that catches too
    broadly would read it as "the container is missing" and create one.

    Both a not-found and an ordinary error are raised from the hook, and in both
    cases the exact exception reaches the caller, the hook ran once, and no extra
    request was made beyond what the found-or-missing path already required. The
    cache is not written, since the call did not succeed.
    """
    case = container_get_or_create_case
    case.connection._backend = case.legacy_backend
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _call_get_or_create(case, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    case.connection._set_container_properties_cache.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_called_once()
    assert case.connection.CreateContainer.call_count == int(case.missing)


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("read_status", [200, 403, 404, 409])
def test_container_get_or_create_recovers_create_conflict_once_legacy(
    container_create_case,
    return_properties,
    read_status,
):
    case = container_create_case
    mock_type = (
        AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    )
    winner = CosmosDict(
        {
            "id": "c1",
            "_rid": "winner",
            "partitionKey": {"paths": ["/original"]},
            "defaultTtl": 10,
        },
        response_headers=CaseInsensitiveDict({"x-ms-activity-id": "winning-read"}),
    )
    missing = CosmosResourceNotFoundError(status_code=404, message="missing")
    conflict = CosmosResourceExistsError(
        status_code=409, message="created concurrently"
    )
    error_type = {
        403: CosmosHttpResponseError,
        404: CosmosResourceNotFoundError,
        409: CosmosResourceExistsError,
    }.get(read_status)
    case.connection._backend = case.legacy_backend
    case.connection.ReadContainer = mock_type(
        side_effect=[
            missing,
            (
                winner
                if error_type is None
                else error_type(status_code=read_status, message="reread")
            ),
        ]
    )
    case.connection.CreateContainer.side_effect = conflict
    seen = []

    def hook(headers, properties):
        assert headers["X-MS-ACTIVITY-ID"] == "winning-read"
        assert properties == winner
        properties["partitionKey"]["paths"].append("/hook-edit")
        seen.append(headers)

    options = dict(
        return_properties=return_properties,
        response_hook=hook,
        timeout=10,
        offer_throughput=400,
        default_ttl=99,
        initial_headers={"x-company-trace": "setup"},
        etag='"v1"',
        match_condition=MatchConditions.IfNotModified,
    )
    if error_type is not None:
        with pytest.raises(error_type) as caught:
            _call_get_or_create(case, **options)
        assert caught.value.status_code == read_status
        assert not seen
        case.connection._set_container_properties_cache.assert_not_called()
    else:
        result = _call_get_or_create(case, **options)
        proxy = result[0] if return_properties else result
        assert proxy.id == "c1"
        assert proxy._client_context is case.client_context
        if return_properties:
            assert result[1] == winner
        assert len(seen) == 1
        case.connection._set_container_properties_cache.assert_called_once()
        cached = case.connection._set_container_properties_cache.call_args.args[1]
        assert cached["partitionKey"]["paths"] == ["/original"]
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_called_once()
    assert case.connection.ReadContainer.call_count == 2
    first, second = case.connection.ReadContainer.call_args_list
    assert "offerThroughput" not in second.kwargs["options"]
    assert (
        second.kwargs["options"]["accessCondition"]
        == first.kwargs["options"]["accessCondition"]
    )
    assert 0 < second.kwargs["timeout"] <= first.kwargs["timeout"]


@pytest.mark.parametrize("status", [401, 403, 404, 409, 429, 500])
def test_container_get_or_create_propagates_failures_without_replay_legacy(
    container_get_or_create_case, status
):
    """A failure at either step reaches the caller with its status intact and is not
    retried.

    Six statuses are covered against both outcomes. Where the container exists
    the failure lands on the read; where it is missing it lands on the create
    that follows, so both steps are exercised.

    A genuine initial not-found is skipped in the existing case, because that is
    not a failure at all -- it is the signal to create, covered by its own test.

    A create conflict permits one follow-up read. If that read also fails, its
    error propagates without another create. The hook does not run and nothing
    is cached.
    """
    case = container_get_or_create_case
    if not case.missing and status == 404:
        pytest.skip("A genuine initial 404 is the create branch, covered separately.")
    error_type = (
        CosmosResourceExistsError
        if status == 409
        else (CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError)
    )
    error = error_type(status_code=status, message="failure")
    case.connection._backend = case.legacy_backend
    target = (
        case.connection.CreateContainer
        if case.missing
        else case.connection.ReadContainer
    )
    target.side_effect = error
    if case.missing and status == 409:
        case.connection.ReadContainer.side_effect = [
            CosmosResourceNotFoundError(status_code=404, message="missing"),
            error,
        ]
    hook = MagicMock()
    with pytest.raises(error_type) as raised:
        _call_get_or_create(case, response_hook=hook)
    assert raised.value.status_code == status
    hook.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    assert case.connection.ReadContainer.call_count == (
        2 if case.missing and status == 409 else 1
    )
    assert case.connection.CreateContainer.call_count == int(case.missing)


def test_concurrent_container_get_or_create_returns_winner_legacy(
    container_create_case,
):
    case = container_create_case
    asynchronous = isinstance(case.database, AsyncDatabaseProxy)
    case.connection._backend = case.legacy_backend
    case.client_context = CosmosClientContext(case.legacy_backend)
    case.database._client_context = case.client_context
    thread_gate = Barrier(8)
    async_gate = asyncio.Event()
    lock = Lock()
    reads = 0
    created = False
    winner = {"id": "c1", "_rid": "winner", "partitionKey": {"paths": ["/pk"]}}

    def response(operation, initial_read):
        nonlocal created
        with lock:
            if initial_read:
                status = 404
            elif operation == OP_CREATE_CONTAINER:
                status = 409 if created else 201
                created = True
            else:
                status = 200
        return BackendResponse(
            status_code=status,
            headers={"x-ms-activity-id": operation},
            body=json.dumps(winner if status < 400 else {"message": "race"}).encode(),
        )

    def starts_read(operation):
        nonlocal reads
        with lock:
            if operation == OP_READ_CONTAINER:
                reads += 1
                return reads <= 8
        return False

    def execute(operation):
        initial = starts_read(operation)
        if initial:
            thread_gate.wait(timeout=10)
        return response(operation, initial)

    async def execute_async(operation):
        initial = starts_read(operation)
        if initial:
            if reads == 8:
                async_gate.set()
            await asyncio.wait_for(async_gate.wait(), 10)
        return response(operation, initial)

    def dispatch(operation):
        if not asynchronous:
            reply = execute(operation)
            return parse_backend_response(reply)

        async def run():
            reply = await execute_async(operation)
            return parse_backend_response(reply)

        return run()

    mock_type = AsyncMock if asynchronous else MagicMock

    async def legacy_read(*_args, **_kwargs):
        return await dispatch(OP_READ_CONTAINER)

    async def legacy_create(*_args, **_kwargs):
        return await dispatch(OP_CREATE_CONTAINER)

    case.connection.ReadContainer = mock_type(
        side_effect=(
            legacy_read
            if asynchronous
            else lambda *_a, **_k: dispatch(OP_READ_CONTAINER)
        )
    )
    case.connection.CreateContainer.side_effect = (
        legacy_create
        if asynchronous
        else lambda *_a, **_k: dispatch(OP_CREATE_CONTAINER)
    )
    hook = MagicMock()

    async def run_all():
        return await asyncio.gather(
            *[
                case.database.create_container_if_not_exists(
                    "c1", PartitionKey(path="/pk"), response_hook=hook
                )
                for _ in range(8)
            ]
        )

    if asynchronous:
        results = asyncio.run(run_all())
    else:
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(
                pool.map(
                    lambda _: _call_get_or_create(case, response_hook=hook), range(8)
                )
            )
    assert [result.id for result in results] == ["c1"] * 8
    assert hook.call_count == 8
    assert case.connection._set_container_properties_cache.call_count == 8
    assert reads == 15
    assert case.connection.CreateContainer.call_count == 8
    case.backend.execute.assert_not_called()


def test_container_get_or_create_distinguishes_bodyless_read_and_create_legacy(
    container_get_or_create_case,
):
    """Keep 304 reads empty; read back requested properties after a bodyless create.

    The hook still observes the original response, not the additional properties read.
    """
    case = container_get_or_create_case
    empty = CosmosDict({}, response_headers=CaseInsensitiveDict({"etag": '"v1"'}))
    case.connection._backend = case.legacy_backend
    target = (
        case.connection.CreateContainer
        if case.missing
        else case.connection.ReadContainer
    )
    target.return_value = empty
    if case.missing:
        case.connection.ReadContainer.side_effect = [
            CosmosResourceNotFoundError(status_code=404),
            case.existing_properties,
        ]
    hook = MagicMock()
    kwargs = dict(
        match_condition=MatchConditions.IfMissing,
        return_properties=True,
        response_hook=hook,
    )
    proxy, properties = _call_get_or_create(case, **kwargs)
    assert proxy.id == "c1"
    if case.missing:
        assert properties == case.existing_properties
    else:
        assert properties == {}
        case.connection.CreateContainer.assert_not_called()
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}


def test_container_get_or_create_explicit_core_python_keeps_transport_options_legacy(
    container_get_or_create_case,
):
    """A customer who chose legacy on purpose keeps the transport options only legacy
    supports.

    A per-call deadline and a connect timeout (which the Rust path refuses) are
    forwarded when the customer explicitly asked for legacy -- to every
    request the call makes, not just the first. Dropping them would silently
    give a call a longer deadline than the one asked for.
    """
    case = container_get_or_create_case
    case.connection._backend = case.legacy_backend
    _call_get_or_create(case, timeout=1.5, connection_timeout=2)
    case.backend.execute.assert_not_called()
    calls = [case.connection.ReadContainer.call_args]
    if case.missing:
        calls.append(case.connection.CreateContainer.call_args)
    for call in calls:
        assert call.kwargs["timeout"] == 1.5
        assert call.kwargs["connection_timeout"] == 2


def test_create_container_preserves_conditional_headers_without_ignored_warnings_legacy():
    """Conditional options still reach the builder, without misleading warnings."""
    from azure.core import MatchConditions
    from azure.cosmos.database import DatabaseProxy
    from azure.cosmos.partition_key import PartitionKey

    captured = {}

    def fake_create_container(
        self,
        database_link,
        definition,
        request_options,
        *,
        response_hook=None,
        kwargs=None,
        deadline=None,
        prepared=None,
    ):
        """Capture the arguments so the test can inspect what the public method forwarded."""
        assert deadline is None
        assert prepared is None
        captured["kwargs"] = dict(kwargs or {})
        captured["request_options"] = dict(request_options or {})
        captured["definition"] = definition
        return {"id": "c1"}

    connection = SimpleNamespace(
        _backend=LEGACY_BACKEND,
        _get_database_link=lambda proxy: "dbs/db1",
        _set_container_properties_cache=lambda link, properties: None,
        last_response_headers={},
    )
    proxy = DatabaseProxy(connection, "db1")

    original = ContainerHelper.create_container
    ContainerHelper.create_container = fake_create_container
    try:
        with warnings.catch_warnings(record=True) as raised:
            warnings.simplefilter("always")
            proxy.create_container(
                "c1",
                PartitionKey(path="/pk"),
                etag="e1",
                match_condition=MatchConditions.IfNotModified,
            )
    finally:
        ContainerHelper.create_container = original

    assert raised == []
    assert captured["request_options"]["accessCondition"] == {
        "type": "IfMatch",
        "condition": "e1",
    }
    assert "sessionToken" not in captured["request_options"]
    assert "session_token" not in captured["kwargs"]
    assert "etag" not in captured["kwargs"]
    assert "match_condition" not in captured["kwargs"]
    assert captured["definition"]["id"] == "c1"


def test_create_container_still_rejects_an_etag_without_a_match_condition_legacy():
    """v4 raises ``ValueError`` here. Swallowing it -- by popping ``etag`` before
    ``build_options`` -- would silently send an unconditional create for a caller who
    asked for a conditional one."""
    from azure.cosmos.database import DatabaseProxy
    from azure.cosmos.partition_key import PartitionKey

    connection = SimpleNamespace(
        _backend=LEGACY_BACKEND,
        _get_database_link=lambda proxy: "dbs/db1",
        _set_container_properties_cache=lambda link, properties: None,
        last_response_headers={},
    )
    proxy = DatabaseProxy(connection, "db1")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(
            ValueError, match="'etag' specified without 'match_condition'"
        ):
            proxy.create_container("c1", PartitionKey(path="/pk"), etag="e1")


_CONTAINER_PAGE = b'{"DocumentCollections":[{"id":"c1"},{"id":"c2"}]}'


def test_sync_list_containers_dispatches_to_the_container_feed_legacy():
    """The read-feed arm keyed on ``Collection`` builds a container page carrying
    the owning database, and the containers come back out of the
    ``DocumentCollections`` envelope. A database feed uses ``Databases``; reading
    the wrong key yields an empty list instead of an error."""
    conn = _new_sync_connection()
    backend = _FakePagedBackend(_CONTAINER_PAGE)
    conn._backend = backend

    result, _headers = conn._CosmosClientConnection__QueryFeed(
        "/dbs/db1/colls/",
        _COLLECTION,
        "db1",
        lambda payload: payload["DocumentCollections"],
        lambda _connection, body: body,
        None,
        {},
    )

    assert backend.prepared.op == OP_LIST_CONTAINERS
    assert backend.prepared.container_link == "dbs/db1"
    assert [c["id"] for c in result] == ["c1", "c2"]


def test_sync_query_containers_dispatches_to_the_container_query_feed_legacy():
    """The query arm keys on ``Collection`` and a query payload, producing a ``OP_QUERY_CONTAINERS`` request."""
    conn = _new_sync_connection()
    backend = _FakePagedBackend(_CONTAINER_PAGE)
    conn._backend = backend

    result, _headers = conn._CosmosClientConnection__QueryFeed(
        "/dbs/db1/colls/",
        _COLLECTION,
        "db1",
        lambda payload: payload["DocumentCollections"],
        lambda _connection, body: body,
        {"query": "SELECT * FROM c"},
        {},
    )

    assert backend.prepared.op == OP_QUERY_CONTAINERS
    assert backend.prepared.container_link == "dbs/db1"
    assert backend.prepared.query == "SELECT * FROM c"
    assert [c["id"] for c in result] == ["c1", "c2"]


def test_async_list_containers_dispatches_to_the_container_feed_legacy():
    """The async routing is separate code with its own branch, so it can break alone."""

    async def _run():
        """Drive the async routing branch for a list feed so it can be verified independently."""
        conn = _new_async_connection()
        backend = _AsyncFakePagedBackend(_CONTAINER_PAGE)
        conn._backend = backend

        result = await conn._CosmosClientConnection__QueryFeed(
            "/dbs/db1/colls/",
            _COLLECTION,
            "db1",
            lambda payload: payload["DocumentCollections"],
            lambda _connection, body: body,
            None,
            {},
        )

        assert backend.prepared.op == OP_LIST_CONTAINERS
        assert backend.prepared.container_link == "dbs/db1"
        assert [c["id"] for c in result] == ["c1", "c2"]

    asyncio.run(_run())


def test_async_query_containers_dispatches_to_the_container_query_feed_legacy():
    """The async query arm builds an ``OP_QUERY_CONTAINERS`` request, separate from the list arm."""

    async def _run():
        """Drive the async routing for a query feed."""
        conn = _new_async_connection()
        backend = _AsyncFakePagedBackend(_CONTAINER_PAGE)
        conn._backend = backend

        result = await conn._CosmosClientConnection__QueryFeed(
            "/dbs/db1/colls/",
            _COLLECTION,
            "db1",
            lambda payload: payload["DocumentCollections"],
            lambda _connection, body: body,
            {"query": "SELECT * FROM c"},
            {},
        )

        assert backend.prepared.op == OP_QUERY_CONTAINERS
        assert backend.prepared.query == "SELECT * FROM c"
        assert [c["id"] for c in result] == ["c1", "c2"]

    asyncio.run(_run())


def test_read_container_does_not_pass_the_hook_to_the_core_python_call_legacy():
    """The helper owns the hook on both engines: it strips ``response_hook`` from the
    kwargs it forwards, so the legacy pipeline cannot fire it a second time."""
    legacy_body = CosmosDict({"id": "c1"}, response_headers=CaseInsensitiveDict())
    connection = SimpleNamespace(
        ReadContainer=MagicMock(return_value=legacy_body),
        last_response_headers={},
    )
    hooks = []

    ContainerHelper(connection, LEGACY_BACKEND).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hooks.append(body),
        kwargs={"response_hook": lambda *a: hooks.append("legacy")},
    )

    assert "response_hook" not in connection.ReadContainer.call_args.kwargs
    assert hooks == [{"id": "c1"}]
