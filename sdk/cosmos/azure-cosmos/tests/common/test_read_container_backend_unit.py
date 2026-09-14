# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container-read contracts and real backend dispatch with fake network responses."""

import asyncio
import ast
import copy
import inspect
import json
import warnings
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import exceptions
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_READ_CONTAINER
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from .test_delete_container_backend_unit import delete_case


@pytest.fixture(params=[False, True], ids=["rust", "legacy"])
def read_case(delete_case, request):
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
        case.connection._backend = case.legacy_backend

    def legacy_read(link, options, **kwargs):
        assert "response_hook" not in kwargs
        case.connection.last_response_headers = case.headers.copy()
        return CosmosDict(copy.deepcopy(case.properties), response_headers=case.headers.copy())

    case.connection.ReadContainer = (AsyncMock if case.is_async else MagicMock)(side_effect=legacy_read)
    case.container = case.database.get_container_client("c1")
    return case


def _read(case, *args, **kwargs):
    result = case.container.read(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


def test_sync_async_read_parameter_contracts_match():
    assert inspect.signature(ContainerProxy.read) == inspect.signature(AsyncContainerProxy.read)


@pytest.mark.parametrize(
    "surface,source_file,class_name,method_names",
    [
        ("sync", "test_crud_container.py", "TestCRUDContainerOperations",
         ["test_collection_crud", "test_partitioned_collection"]),
        ("aio", "test_crud_container_async.py", "TestCRUDContainerOperationsAsync",
         ["test_collection_crud_async", "test_partitioned_collection_async",
          "test_partitioned_collection_quota_async"]),
    ],
)
def test_legacy_read_copies_preserve_original_methods(surface, source_file, class_name, method_names):
    tests = Path(__file__).resolve().parents[1]
    copied_text = (tests / "read_container" / surface / "legacy" / "test_crud_container.py").read_text("utf-8")
    source_text = (tests / source_file).read_text("utf-8")

    def methods(text):
        cls = next(node for node in ast.parse(text).body if isinstance(node, ast.ClassDef) and node.name == class_name)
        return {
            node.name: node for node in cls.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        }

    copied, source = methods(copied_text), methods(source_text)
    assert set(copied) == set(method_names)
    for name in method_names:
        assert ast.dump(copied[name], include_attributes=False) == ast.dump(source[name], include_attributes=False), name
        assert f"Source: tests/{source_file}::{class_name}.{name}" in copied_text


@pytest.mark.parametrize("args", [(None,), (None, True), (None, True, True)])
def test_all_settings_require_keywords(read_case, args):
    with pytest.raises(TypeError):
        _read(read_case, *args)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_obsolete_options_rejected_by_presence(read_case, option, value):
    response_hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _read(read_case, response_hook=response_hook, **{option: value})
    response_hook.assert_not_called()
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("value", [0, False, 2])
def test_socket_timeout_rejected(read_case, value):
    with pytest.raises(TypeError, match="read_timeout"):
        _read(read_case, read_timeout=value)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("quota", [None, False, True])
@pytest.mark.parametrize("statistics", [None, False, True])
def test_metadata_flags_and_none_timeout_preserve_backend(read_case, quota, statistics):
    case = read_case
    before = rust_compatibility_fallback_count()
    result = _read(
        case, populate_quota_info=quota, populate_partition_key_range_statistics=statistics,
        read_timeout=None,
    )
    assert isinstance(result, CosmosDict)
    assert result == case.properties
    assert rust_compatibility_fallback_count() == before
    case.connection._set_container_properties_cache.assert_called_once()
    if case.legacy:
        case.backend.execute.assert_not_called()
        call = case.connection.ReadContainer.call_args
        assert "read_timeout" not in call.kwargs
        options = call.kwargs["options"]
    else:
        case.connection.ReadContainer.assert_not_called()
        prepared = case.backend.execute.call_args.args[0]
        assert prepared.op == OP_READ_CONTAINER
        assert prepared.container_link == "dbs/db1/colls/c1"
        assert prepared.body_bytes == b""
        options = prepared.headers
    for name, value in [("populateQuotaInfo", quota), ("populatePartitionKeyRangeStatistics", statistics)]:
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
def test_conditions_preserved_without_unused_etag_fallback(read_case, kwargs, expected):
    case = read_case
    before = rust_compatibility_fallback_count()
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter("always")
        _read(case, **kwargs)
    assert not notices
    assert rust_compatibility_fallback_count() == before
    if case.legacy:
        call = case.connection.ReadContainer.call_args
        assert "etag" not in call.kwargs
        assert call.kwargs["options"].get("accessCondition") == (
            {"type": expected[0], "condition": expected[1]} if expected else None
        )
    else:
        case.connection.ReadContainer.assert_not_called()
        if expected:
            headers = case.backend.execute.call_args.args[0].headers
            assert headers["If-Match" if expected[0] == "IfMatch" else "If-None-Match"] == expected[1]


@pytest.mark.parametrize("kwargs,error", [
    ({"etag": "v1"}, ValueError),
    ({"match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": MatchConditions.IfModified}, ValueError),
    ({"match_condition": "invalid"}, TypeError),
])
def test_invalid_conditions_do_not_dispatch(read_case, kwargs, error):
    with pytest.raises(error):
        _read(read_case, **kwargs)
    _assert_no_dispatch(read_case)


@pytest.mark.parametrize("timeout", [None, 1, 1.25, 10])
def test_supported_timeout(read_case, timeout):
    case = read_case
    _read(case, timeout=timeout)
    if not case.legacy:
        headers = case.backend.execute.call_args.args[0].headers
        assert headers.get(Constants.OVERALL_TIMEOUT_SECONDS) == timeout
        case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": float("nan")},
    {"timeout": float("inf")}, {"timeout": "10"},
    {"connection_timeout": 2}, {"raw_request_hook": lambda request: None},
    {"initial_headers": {"User-Agent": "custom"}},
])
def test_unsupported_rust_settings_never_replay(read_case, kwargs):
    case = read_case
    if case.legacy:
        _read(case, **kwargs)
        case.backend.execute.assert_not_called()
        return
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="ContainerProxy.read"):
        _read(case, **kwargs)
    _assert_no_dispatch(case)
    assert rust_compatibility_fallback_count() == before


def test_response_hook_cannot_mutate_results_or_cached_properties(read_case):
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


def test_false_valued_response_hook_is_called_once(read_case):
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
def test_response_hook_error_is_not_retried_or_cached(read_case, error_type):
    case = read_case
    error = (error_type(status_code=404, message="response hook failed")
             if error_type is exceptions.CosmosResourceNotFoundError else error_type("response hook failed"))
    response_hook = MagicMock(side_effect=error)
    before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as caught:
        _read(case, response_hook=response_hook)
    assert caught.value is error
    response_hook.assert_called_once()
    case.connection._set_container_properties_cache.assert_not_called()
    (case.connection.ReadContainer if case.legacy else case.backend.execute).assert_called_once()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("status", [403, 404, 412])
def test_service_errors_have_no_success_response_hook(read_case, status):
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


def test_binding_failure_never_replays(read_case):
    case = read_case
    if case.legacy:
        pytest.skip("Rust binding failures do not apply to explicit legacy selection")
    case.backend.execute.side_effect = NotImplementedError("binding capability")
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError):
        _read(case)
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    assert rust_compatibility_fallback_count() == before


def test_async_cancellation_is_not_replayed(read_case):
    case = read_case
    if not case.is_async or case.legacy:
        pytest.skip("Async Rust cancellation case")
    case.backend.execute.side_effect = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        _read(case)
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
