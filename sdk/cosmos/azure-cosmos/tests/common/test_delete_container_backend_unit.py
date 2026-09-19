# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for deleting a container, on both engines (no network).

Deleting a container destroys everything in it, and there is no undo. That
shapes what these tests care about.

The biggest risk is deleting the wrong container. The target can be named,
described by a dictionary, or handed over as a proxy -- including a proxy
belonging to a different database -- and in every form the delete must land on
the container the caller's own database owns.

The second risk is deleting twice. A delete that failed and was then retried on
the other engine could destroy a container somebody recreated in between. So no
failure, at any stage, is ever replayed.

The third is that a delete returns nothing at all. There are no properties to
hand back, so the response hook is given ``None`` as the body, and nothing is
written to the properties cache for a container that no longer exists.

Every test runs against both the sync and async clients and, where it matters,
on both the Rust path and legacy.

All fakes, no Cosmos account.
"""
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
import asyncio
import inspect
import warnings
from collections import UserDict
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.operations import OP_DELETE_CONTAINER, OP_TO_BINDING_METHOD
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_container import build_delete_container_prepared
from azure.cosmos._helpers._response_parse import process_delete_response
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError


class _RustBackend(CosmosBackend):
    """Stand-in Rust backend that returns a canned reply instead of calling a service.

    It subclasses the real backend and replaces only ``execute``, so everything
    else under test is the shipping code rather than a copy that could drift.
    """
    name = "rust"

    def execute(self, prepared, *, deadline=None):
        """Return the canned reply, ignoring the request."""
        return self.response


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in Rust backend that returns a canned reply instead of calling a service."""
    name = "rust"

    async def execute(self, prepared, *, deadline=None):
        """Return the canned reply, ignoring the request."""
        return self.response


@pytest.fixture(params=["sync", "async"])
def delete_case(request):
    """Build a container delete that runs once as a sync client and once as async.

    The canned reply is a "204 No Content", which is what a real delete returns:
    success with no body.

    Reading the container is wired to fail outright rather than return anything.
    A delete should never need to look the container up first, and a read that
    crept in would cost the customer a request and could refresh the cache for
    something about to disappear.

    The legacy stand-in fires the customer's hook itself, matching what the real
    legacy path does, so hook behavior can be compared across both engines.
    """
    is_async = request.param == "async"
    mock = AsyncMock if is_async else MagicMock
    backend = _AsyncRustBackend() if is_async else _RustBackend()
    headers = CaseInsensitiveDict({"x-ms-request-charge": "3", "x-ms-activity-id": "delete"})
    backend.response = BackendResponse(status_code=204, headers=headers.copy(), body=b"", diagnostics="delete trace")
    backend.execute = mock(wraps=backend.execute)
    connection = SimpleNamespace(
        _backend=backend, last_response_headers={},
        ReadContainer=mock(side_effect=AssertionError("Python must not fetch deletion metadata")),
        _set_container_properties_cache=MagicMock(),
    )

    def legacy_delete(link, options, **kwargs):
        connection.last_response_headers = headers
        hook = kwargs.get("response_hook")
        if hook:
            hook(headers, None)

    connection.DeleteContainer = mock(side_effect=legacy_delete)
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    return SimpleNamespace(
        database=proxy_type(connection, "db1"),
        connection=connection, backend=backend, is_async=is_async,
        legacy_backend=ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND,
    )


def _delete(case, *args, **kwargs):
    """Call ``database.delete_container`` and wait for it if the client is async."""
    result = case.database.delete_container(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    """Assert nothing was deleted, read, or cached on either engine.

    Used by every test of a refused call. Because a delete cannot be undone,
    "the call was rejected" has to mean nothing at all went out.
    """
    case.backend.execute.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("target_kind", ["name", "dict", "mapping", "proxy", "other_database_proxy"])
def test_delete_accepts_target_forms_and_returns_none(delete_case, legacy, target_kind):
    """However the container is named, the same one is deleted and nothing is returned.

    The target is given five ways: a name, a dictionary, a dictionary-like
    mapping, a container proxy, and a proxy belonging to a *different* database.
    The last is the one that matters -- borrowing a proxy from elsewhere must not
    aim the delete at another database's container.

    The dictionary form carries an internal resource id that is deliberately set
    to a junk value, proving it is not used to address the request.

    The call returns ``None``, and the hook is given ``None`` as the body,
    because a deleted container has no properties to report. Nothing is read
    first and nothing is cached.

    On the Rust path the request carries no body and no item name, since a
    delete targets the container itself, and the hook's headers include the
    diagnostics the engine collected.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    target = "c1"
    if target_kind == "dict":
        target = {"id": "c1", "_rid": "not-an-input-to-rust"}
    elif target_kind == "mapping":
        target = UserDict(id="c1")
    elif target_kind == "proxy":
        target = case.database.get_container_client("c1")
    elif target_kind == "other_database_proxy":
        target = type(case.database)(case.connection, "other").get_container_client("c1")
    hook = MagicMock()
    assert _delete(case, target, response_hook=hook, read_timeout=None) is None
    hook.assert_called_once()
    assert hook.call_args.args[1] is None
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    if legacy:
        case.backend.execute.assert_not_called()
        call = case.connection.DeleteContainer.call_args
        assert call.args == ("dbs/db1/colls/c1",)
        assert "read_timeout" not in call.kwargs
    else:
        case.connection.DeleteContainer.assert_not_called()
        prepared = case.backend.execute.call_args.args[0]
        assert prepared.op == OP_DELETE_CONTAINER
        assert prepared.container_link == "dbs/db1/colls/c1"
        assert prepared.body_bytes == b""
        assert legacy_partition_key_from_request(prepared) == "[]"
        assert prepared.item_id is None
        assert "x-ms-cosmos-sdk-diagnostics" in hook.call_args.args[0]


def test_delete_dispatch_is_registered():
    """Delete is wired to the engine's delete entry point.

    If this mapping were missing or pointed elsewhere, the call would either
    fail to find a route or, worse, run the wrong operation.
    """
    assert OP_TO_BINDING_METHOD[OP_DELETE_CONTAINER] == "delete_container"


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_delete_rejects_obsolete_options(delete_case, legacy, option, value):
    """Retired options are refused on both engines, whatever their value.

    Session token and query metrics raise ``TypeError`` naming the option, even
    when set to ``None`` or ``False``. Quietly accepting a falsey one would let
    a customer keep believing the setting still does something.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError, match=option):
        _delete(case, "c1", **{option: value})
    _assert_no_dispatch(case)


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("value", [False, 0, 0.5, 2, "invalid"])
def test_delete_rejects_socket_timeout(delete_case, legacy, value):
    """The socket-level ``read_timeout`` is not accepted per call, on either engine.

    False, zero, half a second, two seconds, and a string all raise ``TypeError``
    naming the option, so the error points at exactly what to remove. Nothing is
    deleted.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError, match="read_timeout"):
        _delete(case, "c1", read_timeout=value)
    _assert_no_dispatch(case)


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("args, kwargs", [
    ((), {}), (("c1", None), {}), (("c1",), {"container": "c2"}),
])
def test_delete_has_matching_argument_binding(delete_case, legacy, args, kwargs):
    """Calls that do not match the signature fail before anything is deleted, and the
    published signature stays as intended.

    Three mistakes are covered: no container at all, an extra positional value,
    and the container given twice. Each raises before any request goes out.

    The signature itself is then checked: the container is the only positional
    argument, and initial headers must be named. If headers ever became
    positional, a caller passing them second would have that value read as
    something else entirely.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError):
        _delete(case, *args, **kwargs)
    _assert_no_dispatch(case)
    signature = inspect.signature(case.database.delete_container)
    assert list(signature.parameters) == ["container", "initial_headers", "kwargs"]
    assert signature.parameters["initial_headers"].kind == inspect.Parameter.KEYWORD_ONLY


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": 0}, {"timeout": -1},
    {"timeout": float("nan")}, {"timeout": float("inf")}, {"timeout": "10"},
    {"timeout": 2**64 - 1}, {"timeout": 10**400},
    {"connection_timeout": 2}, {"raw_request_hook": lambda request: None},
    {"raw_response_hook": lambda response: None}, {"unknown_option": None},
    {"initial_headers": {"User-Agent": "override"}},
    {"initial_headers": {"x-ms-version": "override"}},
    {"request_options": {"timeout": 10}},
    {"request_options": {Constants.ContainerRID: "unexpected"}},
])
def test_delete_unsupported_rust_settings_never_reach_legacy(delete_case, kwargs):
    """Options the Rust path cannot honor stop the delete instead of moving it to the
    legacy transport.

    Seventeen calls are covered: nine unusable deadlines, a connect timeout, both
    raw hooks, an unknown keyword, two driver-owned headers, and two raw
    request-options dictionaries.

    Each raises ``NotImplementedError`` pointing at the legacy Python client.
    Nothing is deleted, the hook does not run, and the fallback counter does not
    move -- a refusal is not a fallback, and silently running an irreversible
    delete on an engine the customer did not choose is exactly what must not
    happen.
    """
    hook = MagicMock()
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="delete_container.*legacy Python"):
        _delete(delete_case, "c1", response_hook=hook, **kwargs)
    _assert_no_dispatch(delete_case)
    hook.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_delete_forwards_supported_timeout_and_application_headers(delete_case, timeout):
    """A supported deadline and the customer's own header reach the request, and no
    deadline means none is invented.

    When no timeout is given, no deadline setting appears at all, rather than a
    default being filled in on the customer's behalf. When one is given, it
    arrives in seconds exactly as passed.

    Application headers are how customers tag calls for their own tracing, so
    dropping one loses them the link between their logs and this request. No
    read is made along the way.
    """
    assert _delete(delete_case, "c1", timeout=timeout, initial_headers={"x-company-trace": "cleanup"}) is None
    prepared = delete_case.backend.execute.call_args.args[0]
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-company-trace": "cleanup"}).items())
    if timeout is None:
        assert "__overall_timeout_seconds" not in wire_headers(prepared)
    else:
        assert settings_options(prepared)["timeout_seconds"] == timeout
    delete_case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("kwargs, expected", [
    ({}, None),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfNotModified}, ("IfMatch", '"v1"')),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfModified}, ("IfNoneMatch", '"v1"')),
    ({"etag": "unused", "match_condition": MatchConditions.IfPresent}, ("IfMatch", "*")),
    ({"etag": "unused", "match_condition": MatchConditions.IfMissing}, ("IfNoneMatch", "*")),
])
def test_delete_conditions_are_forwarded_without_ignored_warnings(delete_case, legacy, kwargs, expected):
    """A conditional delete carries its condition on both engines, and an
    unconditional one carries none.

    An etag with a not-modified condition becomes a match condition; with a
    modified condition it becomes a none-match condition; presence and absence
    become the wildcard forms, in which case an etag passed alongside is
    correctly ignored because the condition does not depend on a version.

    With no condition at all, neither header appears -- an accidental wildcard
    would change the meaning of the call.

    This is the customer's protection against destroying a container that
    changed since they last looked, so it has to behave identically on both
    engines, and silently: a warning about an ignored etag would send them
    hunting a bug that is not there.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _delete(case, "c1", **kwargs)
    assert not caught
    if legacy:
        call = case.connection.DeleteContainer.call_args
        condition = call.kwargs["options"].get("accessCondition")
        assert condition == ({"type": expected[0], "condition": expected[1]} if expected else None)
        assert "etag" not in call.kwargs
    else:
        headers = case.backend.execute.call_args.args[0].headers
        if expected:
            assert headers["If-Match" if expected[0] == "IfMatch" else "If-None-Match"] == expected[1]
        else:
            assert "If-Match" not in headers
            assert "If-None-Match" not in headers


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("kwargs, error", [
    ({"etag": "v1"}, ValueError),
    ({"match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": MatchConditions.IfModified}, ValueError),
    ({"match_condition": "invalid"}, TypeError),
])
def test_delete_invalid_conditions_fail_before_dispatch(delete_case, legacy, kwargs, error):
    """An incomplete or malformed condition stops the delete.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. Sending any
    of them would delete unconditionally for a customer who believed the call
    was guarded -- and there is no getting the container back.
    """
    if legacy:
        delete_case.connection._backend = delete_case.legacy_backend
    with pytest.raises(error):
        _delete(delete_case, "c1", **kwargs)
    _assert_no_dispatch(delete_case)


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("falsey", [False, True])
def test_delete_hook_runs_once_with_isolated_headers_and_none(delete_case, legacy, falsey):
    """The hook runs once, is handed ``None`` for the body, and cannot change what the
    client records.

    The hook is tried both as an ordinary callable and as one that reports itself
    as false when tested as a boolean. It runs either way, because being callable
    is what matters.

    It is handed ``None`` rather than an empty dictionary, so a customer cannot
    mistake a deleted container for one with no settings. The headers it gets are
    its own copy: it changes the request charge and the client's own record still
    holds the real value.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    seen = []

    class Hook:
        def __bool__(self):
            return not falsey

        def __call__(self, headers, body):
            assert body is None
            assert headers["X-MS-REQUEST-CHARGE"] == "3"
            assert headers is not case.connection.last_response_headers
            headers["x-ms-request-charge"] = "changed"
            seen.append(body)

    assert _delete(case, "c1", response_hook=Hook()) is None
    assert seen == [None]
    assert case.connection.last_response_headers["x-ms-request-charge"] == "3"


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("error", [ValueError("hook"), CosmosResourceNotFoundError(status_code=404)])
def test_delete_hook_errors_do_not_replay_the_delete(delete_case, legacy, error):
    """An error from the customer's hook never causes a second delete.

    The exact exception reaches the caller, the hook ran once, and exactly one
    request was made on whichever engine is in use. The container is already
    gone by this point, so a retry would either fail as not-found or destroy a
    replacement somebody had just created.

    The not-found case is the trap: an error type the SDK would normally read as
    a service reply, raised here from customer code.
    """
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _delete(case, "c1", response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert case.connection.DeleteContainer.call_count == int(legacy)
    assert case.backend.execute.call_count == int(not legacy)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 412, 429, 500])
def test_delete_service_errors_preserve_headers_and_never_fall_back(delete_case, status):
    """Every failure status from the service arrives intact and is not retried on
    legacy.

    Eight statuses are covered, from bad request through conflict and
    precondition-failed to server error. Each keeps its status code and its
    activity id, which is what a customer quotes when asking support what
    happened, and not-found keeps its specific type so it can be caught alone.

    The hook does not run, because nothing succeeded. Nothing is retried -- a
    precondition failure especially must not be tried again, since it might pass
    the second time and destroy exactly what the customer was guarding.
    """
    case = delete_case
    case.backend.response = BackendResponse(
        status_code=status, headers={"x-ms-activity-id": "failed"}, body=b'{"message":"delete failed"}'
    )
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _delete(case, "c1", response_hook=hook)
    assert raised.value.status_code == status
    if status == 404:
        assert isinstance(raised.value, CosmosResourceNotFoundError)
    assert raised.value.headers["x-ms-activity-id"] == "failed"
    hook.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.DeleteContainer.assert_not_called()


@pytest.mark.parametrize("error", [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()])
def test_delete_binding_errors_and_cancellation_are_not_replayed(delete_case, error):
    """A failure inside the Rust engine, including cancellation, is raised as-is and
    not retried on legacy.

    All three cases -- an ordinary error, a capability failure, and cancellation
    -- reach the caller as the same exception object after exactly one attempt,
    with the hook never running.

    Retrying is especially dangerous here: a failure reported to the client does
    not prove the service never carried the delete out, so a second attempt
    could destroy a container that was recreated in the meantime. Cancellation
    must also pass through unchanged, or it stops unwinding and the caller's
    request to stop is ignored.
    """
    case = delete_case
    case.backend.execute.side_effect = error
    hook = MagicMock()
    with pytest.raises(type(error)) as raised:
        _delete(case, "c1", response_hook=hook)
    assert raised.value is error
    hook.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    case.backend.execute.assert_called_once()


def test_explicit_legacy_delete_retains_legacy_transport_options(delete_case):
    """A customer who chose legacy on purpose keeps the transport options only legacy
    supports.

    A sub-second deadline and a connect timeout are refused on the Rust path, but
    here the customer has explicitly asked for legacy, so both are forwarded
    rather than dropped. Dropping them would silently give the call a longer
    deadline than the one asked for.
    """
    case = delete_case
    case.connection._backend = case.legacy_backend
    _delete(case, "c1", timeout=0.5, connection_timeout=2)
    call = case.connection.DeleteContainer.call_args
    assert call.kwargs["timeout"] == 0.5
    assert call.kwargs["connection_timeout"] == 2
    case.backend.execute.assert_not_called()


@pytest.mark.parametrize("link", ["", "dbs/db1", "dbs/db1/colls/", "dbs/db1/colls/c1/docs/i1"])
def test_delete_builder_rejects_malformed_targets(link):
    """A link that does not name a container is refused rather than guessed at.

    The four shapes are the dangerous ones: empty, a database with no container,
    a container link with an empty name, and a link pointing at an item rather
    than a container. Accepting any of them would aim an irreversible delete at
    something other than the intended container.
    """
    with pytest.raises(ValueError):
        build_delete_container_prepared(link, {})


def test_delete_builder_does_not_mutate_options_or_forward_session_token():
    """Building the request tidies the link, leaves out the retired session token, and
    does not edit the caller's options.

    A link with leading and trailing slashes is accepted and normalized, so a
    customer's harmless formatting difference is not an error.

    The session token is left out of the headers while the caller's own
    dictionary still holds it. The SDK reads options; it does not edit them, and
    a caller reusing the same dictionary for a later call must find it intact.
    """
    options = {"sessionToken": "unused", "initialHeaders": {"x-company-trace": "cleanup"}}
    prepared = build_delete_container_prepared("/dbs/db1/colls/c1/", options)
    assert prepared.container_link == "dbs/db1/colls/c1"
    assert "sessionToken" not in wire_headers(prepared)
    assert options["sessionToken"] == "unused"


def test_delete_parser_returns_none_and_does_not_expose_empty_properties():
    """Reading a delete reply yields ``None``, never an empty set of properties.

    A "204 No Content" has no body. The parser could easily turn that into an
    empty dictionary, which a customer would then have to tell apart from a
    container that genuinely has no settings. It returns ``None`` instead, and
    hands the hook ``None`` too.

    The headers given to the hook are also a separate copy from the client's own
    record, so a hook that edits them cannot corrupt what the next call reads.
    """
    connection = SimpleNamespace(last_response_headers={})
    hook = MagicMock()
    response = BackendResponse(status_code=204, headers={"x-ms-request-charge": "1"}, body=b"")
    assert process_delete_response(response, client_connection=connection, response_hook=hook) is None
    hook.assert_called_once()
    assert hook.call_args.args[1] is None
    assert hook.call_args.args[0] is not connection.last_response_headers
