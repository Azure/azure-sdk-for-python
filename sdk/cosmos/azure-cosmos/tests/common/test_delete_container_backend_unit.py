# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Maintained Rust deletion coverage with no legacy implementation imports.

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

Public-method cases run against sync and async Rust paths. Disposable legacy
comparisons live in test_delete_container_legacy_unit.py, not in this suite.

All fakes, no Cosmos account.
"""

from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options
import asyncio
import inspect
import warnings
from collections import UserDict
from copy import deepcopy
from functools import partial
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from azure.core import MatchConditions

from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import (
    OP_DELETE_CONTAINER,
    OP_TO_BINDING_FUNCTION_NAME,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_container import build_delete_container_prepared
from azure.cosmos._helpers._response_parse import process_delete_response
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError


from common.delete_container_backend_stubs import (
    _call_container_delete,
    _assert_no_request_sent,
    make_delete_case,
)


@pytest.fixture(params=["sync", "async"])
def delete_case(request):
    return make_delete_case(request.param == "async")


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("status", [204, 503], ids=["success", "failure"])
def test_delete_dependencies_do_not_require_legacy_rust(
    monkeypatch, asynchronous, status
):
    """Exercise deletion with retiring imports blocked and methods absent."""
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
        "common.test_delete_container_legacy_unit",
        "common.test_container_legacy_unit",
    }

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        absolute = (
            resolve_name("." * level + name, globals["__package__"]) if level else name
        )
        requested = {absolute, *(f"{absolute}.{item}" for item in (fromlist or ()))}
        if requested & forbidden:
            raise ImportError(
                f"Rust deletion tests require legacy code: {requested & forbidden}"
            )
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    common = Path(__file__).parent
    runpy.run_path(str(common / "container_backend_stubs.py"))
    helpers = runpy.run_path(str(common / "delete_container_backend_stubs.py"))
    module = runpy.run_path(__file__)
    case = helpers["make_delete_case"](asynchronous)
    del case.connection.DeleteContainer
    del case.connection.ReadContainer
    case.backend.response = BackendResponse(
        status_code=status,
        headers={"x-ms-activity-id": "delete"},
        body=b"" if status == 204 else b'{"message":"unavailable"}',
    )
    hook = MagicMock()
    if status == 204:
        assert module["_call_container_delete"](case, "c1", response_hook=hook) is None
        hook.assert_called_once()
        assert hook.call_args.args[1] is None
    else:
        with pytest.raises(CosmosHttpResponseError) as raised:
            module["_call_container_delete"](case, "c1", response_hook=hook)
        assert raised.value.status_code == status
        hook.assert_not_called()
    case.backend.execute.assert_called_once()


@pytest.mark.parametrize(
    "target_kind", ["name", "dict", "mapping", "proxy", "other_database_proxy"]
)
def test_delete_accepts_target_forms_and_returns_none_rust(delete_case, target_kind):
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
    target = "c1"
    if target_kind == "dict":
        target = {"id": "c1", "_rid": "not-an-input-to-rust"}
    elif target_kind == "mapping":
        target = UserDict(id="c1")
    elif target_kind == "proxy":
        target = case.database.get_container_client("c1")
    elif target_kind == "other_database_proxy":
        target = type(case.database)(case.connection, "other").get_container_client(
            "c1"
        )
    hook = MagicMock()
    assert _call_container_delete(case, target, response_hook=hook) is None
    hook.assert_called_once()
    assert hook.call_args.args[1] is None
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    prepared = case.backend.execute.call_args.args[0]
    assert prepared.op == OP_DELETE_CONTAINER
    assert prepared.container_link == "dbs/db1/colls/c1"
    assert prepared.body_bytes == b""
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert prepared.item_id is None
    assert "x-ms-cosmos-sdk-diagnostics" in hook.call_args.args[0]


def test_delete_dispatch_is_registered_rust():
    """Delete is wired to the engine's delete entry point.

    If this mapping were missing or pointed elsewhere, the call would either
    fail to find a route or, worse, run the wrong operation.
    """
    assert OP_TO_BINDING_FUNCTION_NAME[OP_DELETE_CONTAINER] == "delete_container"


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_delete_rejects_obsolete_options_rust(delete_case, option, value):
    """Retired options are refused on both Rust-backed clients, whatever their value.

    Session token and query metrics raise ``TypeError`` naming the option, even
    when set to ``None`` or ``False``. Quietly accepting a falsey one would let
    a customer keep believing the setting still does something.
    """
    case = delete_case
    with pytest.raises(TypeError, match=option):
        _call_container_delete(case, "c1", **{option: value})
    _assert_no_request_sent(case)


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
        ("request_options", None),
        ("feed_options", None),
        ("request_options", "feed_options"),
        ("feed_options", "request_options"),
    ],
)
@pytest.mark.parametrize("value", [None, False, "unused"])
def test_delete_rejects_nested_obsolete_options_before_dispatch_rust(
    delete_case, option, key, source, other_source, value
):
    kwargs = {source: {key: value}}
    if other_source is not None:
        kwargs[other_source] = {}
    original = deepcopy(kwargs)
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _call_container_delete(delete_case, "c1", response_hook=hook, **kwargs)
    assert kwargs == original
    _assert_no_request_sent(delete_case)
    hook.assert_not_called()


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_delete_rejects_non_callable_hook_before_dispatch_rust(delete_case, hook):
    with pytest.raises(
        TypeError, match="delete_container response_hook must be callable or None"
    ):
        _call_container_delete(delete_case, "c1", response_hook=hook)
    _assert_no_request_sent(delete_case)


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
def test_delete_rejects_async_hook_before_dispatch_rust(delete_case, kind):
    async def hook(_headers, _body):
        pytest.fail("An asynchronous response hook must not run")

    class AsyncHook:
        def __bool__(self):
            return False

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
    with pytest.raises(
        TypeError, match="delete_container response_hook must be synchronous"
    ):
        _call_container_delete(delete_case, "c1", response_hook=hooks[kind])
    _assert_no_request_sent(delete_case)


@pytest.mark.parametrize(
    "args, kwargs", [((), {}), (("c1", None), {}), (("c1",), {"container": "c2"})]
)
def test_delete_has_matching_argument_binding_rust(delete_case, args, kwargs):
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
    with pytest.raises(TypeError):
        _call_container_delete(case, *args, **kwargs)
    _assert_no_request_sent(case)
    signature = inspect.signature(case.database.delete_container)
    assert list(signature.parameters) == ["container", "initial_headers", "kwargs"]
    assert (
        signature.parameters["initial_headers"].kind == inspect.Parameter.KEYWORD_ONLY
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout": 0.5},
        {"timeout": False},
        {"timeout": 0},
        {"timeout": -1},
        {"timeout": float("nan")},
        {"timeout": float("inf")},
        {"timeout": "10"},
        {"timeout": 2**64 - 1},
        {"timeout": 10**400},
        {"connection_timeout": 2},
        {"unknown_option": None},
        {"initial_headers": {"User-Agent": "override"}},
        {"initial_headers": {"x-ms-version": "override"}},
        {"request_options": {"timeout": 10}},
        {"request_options": {Constants.ContainerRID: "unexpected"}},
    ],
)
def test_delete_unsupported_rust_settings_never_reach_core_python_rust(
    delete_case, kwargs
):
    """Options the Rust path cannot honor stop the delete instead of moving it to the
    legacy transport.

    The cases cover nine unusable deadlines, a connect timeout, an unknown
    keyword, two driver-owned headers, and two raw request-options dictionaries.

    Each unsupported setting raises ``TypeError`` without legacy fallback,
    except the bad deadlines, which raise ``ValueError`` because they are wrong
    values rather than something Rust cannot do.
    Nothing is deleted and the hook does not run. Silently running an irreversible
    delete on an engine the customer did not choose is exactly what must not
    happen.
    """
    hook = MagicMock()
    error, message = (
        (ValueError, "timeout must be")
        if "timeout" in kwargs
        else (TypeError, "delete_container.*legacy Python")
    )
    with pytest.raises(error, match=message):
        _call_container_delete(delete_case, "c1", response_hook=hook, **kwargs)
    _assert_no_request_sent(delete_case)
    hook.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"retry_write": 0},
        {"retry_write": False},
        {"retry_write": 2},
        {"request_options": {"retry_write": 0}},
        {"feed_options": {"retry_write": False}},
        {"retry_write": None, "request_options": {"retry_write": 2}},
        {"request_options": {}, "feed_options": {"retry_write": 0}},
        {
            "request_options": {"retry_write": None},
            "feed_options": {"retry_write": False},
        },
    ],
)
def test_delete_rejects_retry_write_before_dispatch_rust(delete_case, kwargs):
    original = deepcopy(kwargs)
    hook = MagicMock()
    with pytest.raises(TypeError, match="delete_container.*retry_write.*Rust driver"):
        _call_container_delete(delete_case, "c1", response_hook=hook, **kwargs)
    assert kwargs == original
    _assert_no_request_sent(delete_case)
    hook.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"retry_write": None},
        {"request_options": {"retry_write": None}},
        {"feed_options": {"retry_write": None}},
        {
            "retry_write": None,
            "request_options": {"retry_write": None},
            "feed_options": {"retry_write": None},
        },
    ],
)
def test_delete_allows_default_write_retries_rust(delete_case, kwargs):
    assert _call_container_delete(delete_case, "c1", **kwargs) is None
    delete_case.backend.execute.assert_called_once()
    prepared = delete_case.backend.execute.call_args.args[0]
    assert "retry_write" not in settings_options(prepared)
    delete_case.connection.DeleteContainer.assert_not_called()


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_delete_forwards_supported_timeout_and_application_headers_rust(
    delete_case, timeout
):
    """A supported deadline and the customer's own header reach the request, and no
    deadline means none is invented.

    When no timeout is given, no deadline setting appears at all, rather than a
    default being filled in on the customer's behalf. When one is given, it
    arrives in seconds exactly as passed.

    Application headers are how customers tag calls for their own tracing, so
    dropping one loses them the link between their logs and this request. No
    read is made along the way.
    """
    assert (
        _call_container_delete(
            delete_case,
            "c1",
            timeout=timeout,
            initial_headers={"x-company-trace": "cleanup"},
        )
        is None
    )
    prepared = delete_case.backend.execute.call_args.args[0]
    assert all(
        wire_headers(prepared).get(key.lower()) == str(value)
        for key, value in ({"x-company-trace": "cleanup"}).items()
    )
    if timeout is None:
        assert "__overall_timeout_seconds" not in wire_headers(prepared)
    else:
        assert settings_options(prepared)["timeout_seconds"] == timeout
    delete_case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, None),
        (
            {"etag": '"v1"', "match_condition": MatchConditions.IfNotModified},
            ("IfMatch", '"v1"'),
        ),
        (
            {"etag": '"v1"', "match_condition": MatchConditions.IfModified},
            ("IfNoneMatch", '"v1"'),
        ),
        (
            {"etag": "unused", "match_condition": MatchConditions.IfPresent},
            ("IfMatch", "*"),
        ),
        (
            {"etag": "unused", "match_condition": MatchConditions.IfMissing},
            ("IfNoneMatch", "*"),
        ),
    ],
)
def test_delete_conditions_are_forwarded_without_ignored_warnings_rust(
    delete_case, kwargs, expected
):
    """A conditional delete carries its condition on both Rust-backed clients, and an
    unconditional one carries none.

    An etag with a not-modified condition becomes a match condition; with a
    modified condition it becomes a none-match condition; presence and absence
    become the wildcard forms, in which case an etag passed alongside is
    correctly ignored because the condition does not depend on a version.

    With no condition at all, neither header appears -- an accidental wildcard
    would change the meaning of the call.

    This is the customer's protection against destroying a container that
    changed since they last looked, so it has to behave identically on both
    clients, and silently: a warning about an ignored etag would send them
    hunting a bug that is not there.
    """
    case = delete_case
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_container_delete(case, "c1", **kwargs)
    assert not caught
    prepared = case.backend.execute.call_args.args[0]
    condition = prepared.settings.item
    if expected:
        assert (
            getattr(
                condition, "if_match" if expected[0] == "IfMatch" else "if_none_match"
            )
            == expected[1]
        )
        assert (
            getattr(
                condition, "if_none_match" if expected[0] == "IfMatch" else "if_match"
            )
            is None
        )
    else:
        assert condition.if_match is None
        assert condition.if_none_match is None
    assert not {"if-match", "if-none-match"}.intersection(
        (key.lower() for key in prepared.headers)
    )


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"match_condition": "invalid"}, TypeError),
    ],
)
def test_delete_invalid_conditions_fail_before_dispatch_rust(
    delete_case, kwargs, error
):
    """An incomplete or malformed condition stops the delete.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. Sending any
    of them would delete unconditionally for a customer who believed the call
    was guarded -- and there is no getting the container back.
    """
    with pytest.raises(error):
        _call_container_delete(delete_case, "c1", **kwargs)
    _assert_no_request_sent(delete_case)


@pytest.mark.parametrize("falsey", [False, True])
def test_delete_hook_runs_once_with_isolated_headers_and_none_rust(delete_case, falsey):
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

    assert _call_container_delete(case, "c1", response_hook=Hook()) is None
    assert seen == [None]
    assert case.connection.last_response_headers["x-ms-request-charge"] == "3"


@pytest.mark.parametrize(
    "error",
    [
        ValueError("hook"),
        NotImplementedError("hook"),
        CosmosResourceNotFoundError(status_code=404),
    ],
)
def test_delete_hook_errors_do_not_replay_the_delete_rust(delete_case, error):
    """An error from the customer's hook never causes a second delete.

    The exact exception reaches the caller, the hook ran once, and exactly one
    request was made through Rust. The container is already
    gone by this point, so a retry would either fail as not-found or destroy a
    replacement somebody had just created.

    The not-found case is the trap: an error type the SDK would normally read as
    a service reply, raised here from customer code.
    """
    case = delete_case
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _call_container_delete(case, "c1", response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert case.connection.DeleteContainer.call_count == 0
    assert case.backend.execute.call_count == 1


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 412, 429, 500])
def test_delete_service_errors_preserve_headers_and_never_fall_back_rust(
    delete_case, status
):
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
        status_code=status,
        headers={"x-ms-activity-id": "failed"},
        body=b'{"message":"delete failed"}',
    )
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_container_delete(case, "c1", response_hook=hook)
    assert raised.value.status_code == status
    if status == 404:
        assert isinstance(raised.value, CosmosResourceNotFoundError)
    assert raised.value.headers["x-ms-activity-id"] == "failed"
    hook.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.DeleteContainer.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()],
)
def test_delete_binding_errors_and_cancellation_are_not_replayed_rust(
    delete_case, error
):
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
        _call_container_delete(case, "c1", response_hook=hook)
    assert raised.value is error
    hook.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    case.backend.execute.assert_called_once()


@pytest.mark.parametrize(
    "link", ["", "dbs/db1", "dbs/db1/colls/", "dbs/db1/colls/c1/docs/i1"]
)
def test_delete_builder_rejects_malformed_targets_rust(link):
    """A link that does not name a container is refused rather than guessed at.

    The four shapes are the dangerous ones: empty, a database with no container,
    a container link with an empty name, and a link pointing at an item rather
    than a container. Accepting any of them would aim an irreversible delete at
    something other than the intended container.
    """
    with pytest.raises(ValueError):
        build_delete_container_prepared(link, {})


def test_delete_builder_does_not_mutate_options_or_forward_session_token_rust():
    """Building the request tidies the link, leaves out the retired session token, and
    does not edit the caller's options.

    A link with leading and trailing slashes is accepted and normalized, so a
    customer's harmless formatting difference is not an error.

    The session token is left out of the headers while the caller's own
    dictionary still holds it. The SDK reads options; it does not edit them, and
    a caller reusing the same dictionary for a later call must find it intact.
    """
    options = {
        "sessionToken": "unused",
        "initialHeaders": {"x-company-trace": "cleanup"},
    }
    prepared = build_delete_container_prepared("/dbs/db1/colls/c1/", options)
    assert prepared.container_link == "dbs/db1/colls/c1"
    assert "sessionToken" not in wire_headers(prepared)
    assert options["sessionToken"] == "unused"


def test_delete_parser_returns_none_and_does_not_expose_empty_properties_rust():
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
    response = BackendResponse(
        status_code=204, headers={"x-ms-request-charge": "1"}, body=b""
    )
    assert (
        process_delete_response(
            response, client_connection=connection, response_hook=hook
        )
        is None
    )
    hook.assert_called_once()
    assert hook.call_args.args[1] is None
    assert hook.call_args.args[0] is not connection.last_response_headers
