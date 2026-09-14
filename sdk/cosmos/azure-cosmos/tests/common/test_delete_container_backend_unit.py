# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Container deletion routing and public contracts without network requests."""
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
from azure.cosmos._helpers._response_parse import parse_delete_response
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError


class _RustBackend(CosmosBackend):
    name = "rust"

    def execute(self, prepared):
        return self.response


class _AsyncRustBackend(AsyncCosmosBackend):
    name = "rust"

    async def execute(self, prepared):
        return self.response


@pytest.fixture(params=["sync", "async"])
def delete_case(request):
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
    result = case.database.delete_container(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    case.backend.execute.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("target_kind", ["name", "dict", "mapping", "proxy", "other_database_proxy"])
def test_delete_accepts_target_forms_and_returns_none(delete_case, legacy, target_kind):
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
        assert prepared.partition_key_header == "[]"
        assert prepared.item_id is None
        assert "x-ms-cosmos-sdk-diagnostics" in hook.call_args.args[0]


def test_delete_dispatch_is_registered():
    assert OP_TO_BINDING_METHOD[OP_DELETE_CONTAINER] == "delete_container"


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_delete_rejects_obsolete_options(delete_case, legacy, option, value):
    case = delete_case
    if legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError, match=option):
        _delete(case, "c1", **{option: value})
    _assert_no_dispatch(case)


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("value", [False, 0, 0.5, 2, "invalid"])
def test_delete_rejects_socket_timeout(delete_case, legacy, value):
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
    hook = MagicMock()
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="delete_container.*legacy Python"):
        _delete(delete_case, "c1", response_hook=hook, **kwargs)
    _assert_no_dispatch(delete_case)
    hook.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_delete_forwards_supported_timeout_and_application_headers(delete_case, timeout):
    assert _delete(delete_case, "c1", timeout=timeout, initial_headers={"x-company-trace": "cleanup"}) is None
    prepared = delete_case.backend.execute.call_args.args[0]
    assert prepared.headers["initialHeaders"] == {"x-company-trace": "cleanup"}
    if timeout is None:
        assert "__overall_timeout_seconds" not in prepared.headers
    else:
        assert prepared.headers["__overall_timeout_seconds"] == timeout
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
    if legacy:
        delete_case.connection._backend = delete_case.legacy_backend
    with pytest.raises(error):
        _delete(delete_case, "c1", **kwargs)
    _assert_no_dispatch(delete_case)


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("falsey", [False, True])
def test_delete_hook_runs_once_with_isolated_headers_and_none(delete_case, legacy, falsey):
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
    case = delete_case
    case.connection._backend = case.legacy_backend
    _delete(case, "c1", timeout=0.5, connection_timeout=2)
    call = case.connection.DeleteContainer.call_args
    assert call.kwargs["timeout"] == 0.5
    assert call.kwargs["connection_timeout"] == 2
    case.backend.execute.assert_not_called()


@pytest.mark.parametrize("link", ["", "dbs/db1", "dbs/db1/colls/", "dbs/db1/colls/c1/docs/i1"])
def test_delete_builder_rejects_malformed_targets(link):
    with pytest.raises(ValueError):
        build_delete_container_prepared(link, {})


def test_delete_builder_does_not_mutate_options_or_forward_session_token():
    options = {"sessionToken": "unused", "initialHeaders": {"x-company-trace": "cleanup"}}
    prepared = build_delete_container_prepared("/dbs/db1/colls/c1/", options)
    assert prepared.container_link == "dbs/db1/colls/c1"
    assert "sessionToken" not in prepared.headers
    assert options["sessionToken"] == "unused"


def test_delete_parser_returns_none_and_does_not_expose_empty_properties():
    connection = SimpleNamespace(last_response_headers={})
    hook = MagicMock()
    response = BackendResponse(status_code=204, headers={"x-ms-request-charge": "1"}, body=b"")
    assert parse_delete_response(response, client_connection=connection, response_hook=hook) is None
    hook.assert_called_once()
    assert hook.call_args.args[1] is None
    assert hook.call_args.args[0] is not connection.last_response_headers
