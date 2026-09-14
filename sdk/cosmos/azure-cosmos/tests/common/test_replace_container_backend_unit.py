# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import copy
import inspect
import json
import warnings
from collections import UserDict
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import exceptions
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_REPLACE_CONTAINER, OP_TO_BINDING_METHOD
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._base import _validate_resource
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_container import build_replace_container_prepared
from azure.cosmos.partition_key import PartitionKey
from .test_delete_container_backend_unit import delete_case


PK = PartitionKey(path="/pk")


@pytest.fixture(params=[False, True], ids=["rust", "legacy"])
def replace_case(delete_case, request):
    case = delete_case
    case.legacy = request.param
    case.properties = {
        "id": "c1", "_rid": "rid", "partitionKey": PK,
        "defaultTtl": 3600, "indexingPolicy": {"indexingMode": "consistent"},
    }
    case.headers = CaseInsensitiveDict({"etag": '"v2"', "x-ms-activity-id": "replace", "x-ms-request-charge": "5"})
    case.backend.response = BackendResponse(
        status_code=200, body=json.dumps(case.properties).encode(),
        headers=case.headers.copy(), diagnostics="replacement trace",
    )
    if case.legacy:
        case.connection._backend = case.legacy_backend

    def legacy_replace(link, collection, options, **kwargs):
        _validate_resource(collection)
        assert "response_hook" not in kwargs
        case.connection.last_response_headers = case.headers
        return CosmosDict(copy.deepcopy(case.properties), response_headers=case.headers)

    case.connection.ReplaceContainer = (AsyncMock if case.is_async else MagicMock)(side_effect=legacy_replace)
    return case


def _replace(case, *args, **kwargs):
    result = case.database.replace_container(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    case.backend.execute.assert_not_called()
    case.connection.ReplaceContainer.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("kind", ["name", "dict", "mapping", "proxy", "other_database_proxy"])
@pytest.mark.parametrize("return_properties", [False, True])
def test_target_ownership_returns_and_rust_dispatch(replace_case, kind, return_properties):
    case = replace_case
    target = "c1"
    if kind == "dict":
        target = {"id": "c1", "defaultTtl": 10, "indexingPolicy": {"indexingMode": "none"}}
    elif kind == "mapping":
        target = UserDict(id="c1")
    elif kind == "proxy":
        target = case.database.get_container_client("c1")
    elif kind == "other_database_proxy":
        target = type(case.database)(case.connection, "other").get_container_client("c1")
    result = _replace(case, target, PK, default_ttl=3600, return_properties=return_properties, read_timeout=None)
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1" and proxy.container_link == "dbs/db1/colls/c1"
    assert proxy.client_connection is case.connection
    assert proxy._item_context is case.database._item_context
    if return_properties:
        assert isinstance(result[1], CosmosDict)
        assert result[1]["defaultTtl"] == 3600
        assert result[1].get_response_headers()["etag"] == '"v2"'
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_called_once()
    if case.legacy:
        case.backend.execute.assert_not_called()
        call = case.connection.ReplaceContainer.call_args
        assert call.args == ("dbs/db1/colls/c1",)
        assert "read_timeout" not in call.kwargs
        body = call.kwargs["collection"]
    else:
        case.connection.ReplaceContainer.assert_not_called()
        prepared = case.backend.execute.call_args.args[0]
        assert prepared.op == OP_REPLACE_CONTAINER
        assert prepared.container_link == "dbs/db1/colls/c1"
        assert prepared.partition_key_header == "[]" and prepared.item_id is None
        body = json.loads(prepared.body_bytes)
    assert body == {"id": "c1", "partitionKey": PK, "defaultTtl": 3600}


def test_all_replacement_fields_preserved_without_mutating_inputs(replace_case):
    options = {
        "indexing_policy": {"indexingMode": "consistent", "includedPaths": [{"path": "/*"}]},
        "default_ttl": 0,
        "conflict_resolution_policy": {"mode": "LastWriterWins", "conflictResolutionPath": "/ts"},
        "analytical_storage_ttl": -1,
        "computed_properties": [{"name": "lowerName", "query": "SELECT VALUE LOWER(c.name) FROM c"}],
        "full_text_policy": {"defaultLanguage": "en-US", "fullTextPaths": []},
        "vector_embedding_policy": {"vectorEmbeddings": []},
    }
    original = copy.deepcopy(options)
    _replace(replace_case, container="c1", partition_key=PK, **options)
    body = (replace_case.connection.ReplaceContainer.call_args.kwargs["collection"] if replace_case.legacy
            else json.loads(replace_case.backend.execute.call_args.args[0].body_bytes))
    assert body == dict(
        id="c1", partitionKey=PK, indexingPolicy=options["indexing_policy"], defaultTtl=0,
        conflictResolutionPolicy=options["conflict_resolution_policy"], analyticalStorageTtl=-1,
        computedProperties=options["computed_properties"], fullTextPolicy=options["full_text_policy"],
        vectorEmbeddingPolicy=options["vector_embedding_policy"],
    )
    assert options == original


@pytest.mark.parametrize("args,kwargs", [
    ((), {}), (("c1",), {}), ((), {"partition_key": PK}),
    (("c1", PK), {"container": "other"}), (("c1", PK), {"partition_key": PK}),
    (("c1", PK, {}), {}), (("c1", PK, {}, 60), {}),
])
def test_invalid_argument_binding_fails_before_dispatch(replace_case, args, kwargs):
    with pytest.raises(TypeError):
        _replace(replace_case, *args, **kwargs)
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True])
def test_retired_keywords_rejected_by_presence(replace_case, option, value):
    with pytest.raises(TypeError, match=option):
        _replace(replace_case, "c1", PK, **{option: value})
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("value", [False, 0, 0.5, 2])
def test_per_call_read_timeout_rejected(replace_case, value):
    with pytest.raises(TypeError, match="read_timeout"):
        _replace(replace_case, "c1", PK, read_timeout=value)
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": 0}, {"timeout": -1},
    {"timeout": float("nan")}, {"timeout": float("inf")}, {"timeout": "10"},
    {"timeout": 2**64 - 1}, {"timeout": 10**400},
    {"connection_timeout": 2}, {"raw_request_hook": lambda request: None},
    {"raw_response_hook": lambda response: None}, {"unknown_option": None},
    {"initial_headers": {"User-Agent": "override"}}, {"initial_headers": {"x-ms-version": "override"}},
    {"request_options": {"timeout": 10}},
])
def test_unsupported_rust_options_never_fall_back(replace_case, kwargs):
    case = replace_case
    if case.legacy:
        pytest.skip("Rust-specific eligibility")
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="replace_container.*legacy Python"):
        _replace(case, "c1", PK, **kwargs)
    _assert_no_dispatch(case)
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_supported_timeouts_and_application_headers(replace_case, timeout):
    case = replace_case
    _replace(case, "c1", PK, timeout=timeout, initial_headers={"x-company-trace": "replace"})
    if not case.legacy:
        headers = case.backend.execute.call_args.args[0].headers
        assert headers["initialHeaders"] == {"x-company-trace": "replace"}
        assert headers.get("__overall_timeout_seconds") == timeout
    case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("kwargs,expected", [
    ({}, None),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfNotModified}, ("IfMatch", '"v1"')),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfModified}, ("IfNoneMatch", '"v1"')),
    ({"etag": "unused", "match_condition": MatchConditions.IfPresent}, ("IfMatch", "*")),
    ({"etag": "unused", "match_condition": MatchConditions.IfMissing}, ("IfNoneMatch", "*")),
])
def test_conditions_forwarded_without_ignored_warnings(replace_case, kwargs, expected):
    case = replace_case
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _replace(case, "c1", PK, **kwargs)
    assert not caught
    if case.legacy:
        call = case.connection.ReplaceContainer.call_args
        assert "etag" not in call.kwargs
        assert call.kwargs["options"].get("accessCondition") == (
            {"type": expected[0], "condition": expected[1]} if expected else None
        )
    elif expected:
        headers = case.backend.execute.call_args.args[0].headers
        assert headers["If-Match" if expected[0] == "IfMatch" else "If-None-Match"] == expected[1]


@pytest.mark.parametrize("kwargs,error", [
    ({"etag": "v1"}, ValueError), ({"match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": MatchConditions.IfModified}, ValueError), ({"match_condition": "invalid"}, TypeError),
])
def test_invalid_conditions_fail_before_dispatch(replace_case, kwargs, error):
    with pytest.raises(error):
        _replace(replace_case, "c1", PK, **kwargs)
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("falsey", [False, True])
def test_hooks_cannot_change_headers_body_or_cached_properties(replace_case, falsey):
    case = replace_case
    calls = []

    class Hook:
        def __bool__(self):
            return not falsey

        def __call__(self, headers, body):
            assert headers["ETAG"] == '"v2"'
            headers["etag"] = "changed"
            body["id"] = "wrong"
            body["indexingPolicy"]["indexingMode"] = "none"
            body.get_response_headers()["etag"] = "body-header-change"
            calls.append(body)

    proxy, properties = _replace(case, "c1", PK, return_properties=True, response_hook=Hook())
    assert len(calls) == 1 and proxy.id == "c1"
    assert properties["indexingPolicy"]["indexingMode"] == "consistent"
    assert properties.get_response_headers()["etag"] == '"v2"'
    assert case.connection.last_response_headers["etag"] == '"v2"'


@pytest.mark.parametrize("error", [ValueError("hook"), exceptions.CosmosResourceNotFoundError(status_code=404)])
def test_hook_errors_never_replay_replacement(replace_case, error):
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _replace(replace_case, "c1", PK, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert replace_case.backend.execute.call_count == int(not replace_case.legacy)
    assert replace_case.connection.ReplaceContainer.call_count == int(replace_case.legacy)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 412, 429, 500])
def test_rust_errors_preserve_status_and_do_not_call_hook(replace_case, status):
    case = replace_case
    if case.legacy:
        pytest.skip("Rust response mapping")
    case.backend.response = BackendResponse(
        status_code=status, body=b'{"message":"replacement failed"}', headers={"x-ms-activity-id": "error"},
    )
    hook = MagicMock()
    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        _replace(case, "c1", PK, response_hook=hook)
    assert raised.value.status_code == status
    assert raised.value.headers["x-ms-activity-id"] == "error"
    if status == 404:
        assert isinstance(raised.value, exceptions.CosmosResourceNotFoundError)
    hook.assert_not_called()
    case.connection.ReplaceContainer.assert_not_called()


@pytest.mark.parametrize("error", [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()])
def test_binding_failures_and_cancellation_do_not_replay(replace_case, error):
    case = replace_case
    if case.legacy:
        pytest.skip("Rust binding failures")
    case.backend.execute.side_effect = error
    with pytest.raises(type(error)) as raised:
        _replace(case, "c1", PK)
    assert raised.value is error
    case.backend.execute.assert_called_once()
    case.connection.ReplaceContainer.assert_not_called()


def test_builder_registration_and_invalid_links():
    assert OP_TO_BINDING_METHOD[OP_REPLACE_CONTAINER] == "replace_container"
    for link in ["", "dbs/db1", "dbs/db1/colls/", "dbs/db1/colls/c1/docs/i1"]:
        with pytest.raises(ValueError):
            build_replace_container_prepared(link, {"id": "c1", "partitionKey": PK}, {})
    options = {"sessionToken": "ignored", "initialHeaders": {"x-company-trace": "replace"}}
    prepared = build_replace_container_prepared("/dbs/db1/colls/c1/", {"id": "c1", "partitionKey": PK}, options)
    assert prepared.container_link == "dbs/db1/colls/c1"
    assert "sessionToken" not in prepared.headers and options["sessionToken"] == "ignored"
