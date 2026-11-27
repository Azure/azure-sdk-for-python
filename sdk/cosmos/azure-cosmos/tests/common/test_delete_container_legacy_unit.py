# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Disposable legacy deletion comparisons; run with --include-legacy-tests.

Maintained Rust tests do not import this module.
"""

import inspect
import warnings
from collections import UserDict
from unittest.mock import MagicMock

import pytest
from azure.core import MatchConditions
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common.delete_container_backend_stubs import (
    _call_container_delete,
    _assert_no_request_sent,
    make_delete_case,
)


@pytest.fixture(params=["sync", "async"])
def delete_case(request):
    case = make_delete_case(request.param == "async")
    case.legacy_backend = ASYNC_LEGACY_BACKEND if case.is_async else LEGACY_BACKEND

    def legacy_delete(_link, _options=None, **kwargs):
        headers = case.backend.response.headers
        case.connection.last_response_headers = headers
        hook = kwargs.get("response_hook")
        if hook:
            hook(headers, None)

    case.connection.DeleteContainer.side_effect = legacy_delete
    return case


@pytest.mark.parametrize(
    "target_kind", ["name", "dict", "mapping", "proxy", "other_database_proxy"]
)
def test_delete_accepts_target_forms_and_returns_none_legacy(delete_case, target_kind):
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
    case.connection._backend = case.legacy_backend
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
    case.backend.execute.assert_not_called()
    call = case.connection.DeleteContainer.call_args
    assert call.args == ("dbs/db1/colls/c1",)


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_delete_rejects_obsolete_options_legacy(delete_case, option, value):
    """Retired options are refused on both engines, whatever their value.

    Session token and query metrics raise ``TypeError`` naming the option, even
    when set to ``None`` or ``False``. Quietly accepting a falsey one would let
    a customer keep believing the setting still does something.
    """
    case = delete_case
    case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError, match=option):
        _call_container_delete(case, "c1", **{option: value})
    _assert_no_request_sent(case)


@pytest.mark.parametrize(
    "args, kwargs", [((), {}), (("c1", None), {}), (("c1",), {"container": "c2"})]
)
def test_delete_has_matching_argument_binding_legacy(delete_case, args, kwargs):
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
    case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError):
        _call_container_delete(case, *args, **kwargs)
    _assert_no_request_sent(case)
    signature = inspect.signature(case.database.delete_container)
    assert list(signature.parameters) == ["container", "initial_headers", "kwargs"]
    assert (
        signature.parameters["initial_headers"].kind == inspect.Parameter.KEYWORD_ONLY
    )


def test_delete_preserves_explicit_legacy_retry_write_legacy(delete_case):
    delete_case.connection._backend = delete_case.legacy_backend
    assert _call_container_delete(delete_case, "c1", retry_write=2) is None
    delete_case.backend.execute.assert_not_called()
    delete_case.connection.DeleteContainer.assert_called_once()
    options = delete_case.connection.DeleteContainer.call_args.kwargs["options"]
    assert options[Constants.Kwargs.RETRY_WRITE] == 2


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
def test_delete_conditions_are_forwarded_without_ignored_warnings_legacy(
    delete_case, kwargs, expected
):
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
    case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_container_delete(case, "c1", **kwargs)
    assert not caught
    call = case.connection.DeleteContainer.call_args
    condition = call.kwargs["options"].get("accessCondition")
    assert condition == (
        {"type": expected[0], "condition": expected[1]} if expected else None
    )
    assert "etag" not in call.kwargs


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"match_condition": "invalid"}, TypeError),
    ],
)
def test_delete_invalid_conditions_fail_before_dispatch_legacy(
    delete_case, kwargs, error
):
    """An incomplete or malformed condition stops the delete.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. Sending any
    of them would delete unconditionally for a customer who believed the call
    was guarded -- and there is no getting the container back.
    """
    delete_case.connection._backend = delete_case.legacy_backend
    with pytest.raises(error):
        _call_container_delete(delete_case, "c1", **kwargs)
    _assert_no_request_sent(delete_case)


@pytest.mark.parametrize("falsey", [False, True])
def test_delete_hook_runs_once_with_isolated_headers_and_none_legacy(
    delete_case, falsey
):
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
def test_delete_hook_errors_do_not_replay_the_delete_legacy(delete_case, error):
    """An error from the customer's hook never causes a second delete.

    The exact exception reaches the caller, the hook ran once, and exactly one
    request was made on whichever engine is in use. The container is already
    gone by this point, so a retry would either fail as not-found or destroy a
    replacement somebody had just created.

    The not-found case is the trap: an error type the SDK would normally read as
    a service reply, raised here from customer code.
    """
    case = delete_case
    case.connection._backend = case.legacy_backend
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _call_container_delete(case, "c1", response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert case.connection.DeleteContainer.call_count == 1
    assert case.backend.execute.call_count == 0


def test_explicit_core_python_delete_retains_core_python_transport_options_legacy(
    delete_case,
):
    """A customer who chose legacy on purpose keeps the transport options only legacy
    supports.

    A connect timeout is refused on the Rust path, but here the customer has
    explicitly asked for legacy, so it and the deadline are forwarded rather
    than dropped. Dropping the deadline would silently give the call a longer
    one than the one asked for.
    """
    case = delete_case
    case.connection._backend = case.legacy_backend
    _call_container_delete(case, "c1", timeout=1.5, connection_timeout=2)
    call = case.connection.DeleteContainer.call_args
    assert call.kwargs["timeout"] == 1.5
    assert call.kwargs["connection_timeout"] == 2
    case.backend.execute.assert_not_called()
