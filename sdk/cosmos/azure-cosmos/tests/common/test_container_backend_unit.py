# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for container backend routing (no network).

Three of ``DatabaseProxy``'s container methods land here. ``create_container``
sends one request. ``list_containers`` and ``query_containers`` each return a
feed, one page at a time.

What these protect, and the customer behavior behind each:

* the request the rust engine is handed. A container create is scoped to a
  database, not to a container -- the container does not exist yet -- so the
  database name rides in ``item_id`` and the definition the caller assembled
  rides in the body. Get either wrong and the container is created in the wrong
  database or with the wrong policies.
* the feed pages carrying the owning database. ``PreparedQuery`` has no field for
  a database name, so the ``dbs/{id}`` link rides in ``container_link``. If the
  path cannot be parsed the gate must say no, so the call stays on the legacy
  path instead of running against nothing.
* the ``DocumentCollections`` envelope. The legacy reader pulls containers out of
  that key; a database feed uses ``Databases``. Getting it wrong yields a
  silently empty list rather than an error, which is the worst kind of wrong.
* routing away from rust when rust cannot honor an option exactly -- a
  sub-second ``timeout``, a socket-level ``read_timeout``, a query in the
  legacy-only string form that goes on the wire as ``text/plain``.
* create rejects obsolete keywords and unsupported Rust calls rather than
  silently switching transports. Conditional-header normalization is preserved.

All fakes, no Cosmos account.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import warnings
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import ServiceRequestError
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _base as base
from azure.cosmos import http_constants
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.contracts import BackendResponse, QueryPage
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._backend.operations import (
    OP_CREATE_CONTAINER,
    OP_LIST_CONTAINERS,
    OP_QUERY_CONTAINERS,
    OP_READ_CONTAINER,
    OP_TO_BINDING_METHOD,
    QUERY_TO_BINDING_METHOD,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_container import (
    build_create_container_prepared,
    build_read_container_prepared,
    is_create_container_rust_eligible,
    is_read_container_rust_eligible,
)
from azure.cosmos._helpers.container_helper import ContainerHelper
from azure.cosmos._helpers._item_context import ResponseHeaderState
from azure.cosmos._helpers._request_headers import flatten_options_to_headers
from azure.cosmos._query_rust_routing import (
    build_list_containers_prepared_query,
    build_query_containers_prepared_query,
    can_use_rust_backend_for_list_containers_page,
    can_use_rust_backend_for_query_containers_page,
)
from azure.cosmos.aio._helpers.container_helper import AsyncContainerHelper
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceExistsError, CosmosResourceNotFoundError
from azure.cosmos.offer import ThroughputProperties
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncConnection,
)
from azure.cosmos._cosmos_client_connection import (
    CosmosClientConnection as SyncConnection,
)
from azure.cosmos.documents import ConnectionPolicy


_COLLECTION = http_constants.ResourceType.Collection


def _created_container_response() -> BackendResponse:
    """Return a canned 201 Created reply carrying a new container body and a request-charge header."""
    # A canned "201 Created" reply: the new container's body plus a
    # request-charge header, used by the fake backends below.
    return BackendResponse(
        status_code=201,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
        body=b'{"id":"c1","_rid":"rid1"}',
    )


class _RustBackend(CosmosBackend):
    """Stand-in rust backend: records the request it was handed and returns a
    canned reply, so a test can check what would have gone on the wire."""
    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    def execute(self, prepared):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in rust backend: records the request it was handed and returns
    a canned reply.

    Subclasses the real ``AsyncCosmosBackend`` and overrides only ``execute``, so
    the engine-selection and legacy-fallback logic under test is the shipping one
    rather than a copy of it that could drift.
    """
    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    async def execute(self, prepared):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


@pytest.fixture(params=["sync", "async"])
def container_create_case(request):
    is_async = request.param == "async"
    backend = _AsyncRustBackend() if is_async else _RustBackend()
    mock_type = AsyncMock if is_async else MagicMock
    backend.execute = mock_type(wraps=backend.execute)
    headers = CaseInsensitiveDict({"x-ms-request-charge": "5.25"})
    properties = CosmosDict({"id": "c1", "_rid": "rid1"}, response_headers=headers)
    connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        CreateContainer=mock_type(return_value=properties),
        _set_container_properties_cache=MagicMock(),
    )
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    item_context = object()
    return SimpleNamespace(
        database=proxy_type(connection, "db1", _item_context=item_context),
        connection=connection,
        backend=backend,
        item_context=item_context,
        legacy_backend=ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND,
    )


def _call_container_create(case, *args, method="create_container", **kwargs):
    result = getattr(case.database, method)(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_container_create_rejects_obsolete_keywords(container_create_case, use_legacy, method, option, value):
    case = container_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), method=method,
                               response_hook=hook, **{option: value})
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
@pytest.mark.parametrize("timeout", [False, 0.5, 1, "invalid"])
def test_container_create_rejects_per_call_socket_timeout(container_create_case, use_legacy, method, timeout):
    case = container_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError, match="read_timeout"):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), method=method, read_timeout=timeout)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("extra_args", [(None,), (None, None), (None, None, False), (None, None, None, 400)])
def test_container_create_optional_settings_are_keyword_only(container_create_case, extra_args):
    case = container_create_case
    with pytest.raises(TypeError, match="Unexpected positional parameters"):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), *extra_args)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
def test_container_create_retains_manual_runtime_signature(container_create_case, method):
    signature = inspect.signature(getattr(container_create_case.database, method))
    assert list(signature.parameters) == ["args", "kwargs"]
    assert signature.parameters["args"].kind == inspect.Parameter.VAR_POSITIONAL
    assert signature.parameters["kwargs"].kind == inspect.Parameter.VAR_KEYWORD


@pytest.mark.parametrize("proxy_type", [DatabaseProxy, AsyncDatabaseProxy])
def test_container_get_or_create_overloads_match_keyword_only_contract(proxy_type):
    from typing import get_overloads

    overloads = get_overloads(proxy_type.create_container_if_not_exists)
    assert len(overloads) == 2
    for overload in overloads:
        parameters = inspect.signature(overload).parameters
        positional = [name for name, param in parameters.items()
                      if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD]
        assert positional == ["self", "id", "partition_key"]
        assert parameters["indexing_policy"].kind == inspect.Parameter.KEYWORD_ONLY
        assert "populate_query_metrics" not in parameters


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
@pytest.mark.parametrize(
    "args, kwargs, message",
    [
        ((), {}, "missing required argument: 'id'"),
        ((), {"partition_key": None}, "missing required argument: 'id'"),
        ((), {"id": "c1"}, "missing required argument: 'partition_key'"),
        (("c1",), {}, "missing required argument: 'partition_key'"),
        (("c1",), {"id": "c1", "partition_key": None}, "multiple values for argument 'id'"),
        (("c1", None), {"id": "other"}, "multiple values for argument 'id'"),
        (("c1", None), {"partition_key": None}, "multiple values for argument 'partition_key'"),
        (("c1", None), {"partition_key": PartitionKey(path="/pk")}, "multiple values for argument 'partition_key'"),
        (("c1", None, {}), {}, "Unexpected positional parameters"),
    ],
)
def test_container_create_invalid_argument_binding_fails_before_dispatch(
    container_create_case, use_legacy, method, args, kwargs, message
):
    case = container_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    hook = MagicMock()
    original_kwargs = dict(kwargs)
    before = rust_compatibility_fallback_count()
    with pytest.raises(TypeError) as raised:
        _call_container_create(case, *args, **kwargs, method=method, response_hook=hook)
    assert "{}()".format(method) in str(raised.value)
    assert message in str(raised.value)
    assert kwargs == original_kwargs
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_argument_binding_preserves_values_and_optional_kwargs(positional_count):
    from azure.cosmos._helpers._request_container import parse_container_create_args

    values = ("c1", None)
    kwargs = dict(zip(("id", "partition_key")[positional_count:], values[positional_count:]))
    kwargs["default_ttl"] = 60
    assert parse_container_create_args(values[:positional_count], kwargs) == values
    assert kwargs == {"default_ttl": 60}


def test_container_create_argument_binding_does_not_consume_arguments_on_error():
    from azure.cosmos._helpers._request_container import parse_container_create_args

    kwargs = {"id": "c1", "default_ttl": 60}
    with pytest.raises(TypeError, match="partition_key"):
        parse_container_create_args((), kwargs)
    assert kwargs == {"id": "c1", "default_ttl": 60}


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_preserves_required_arguments_and_return_shapes(
    container_create_case, use_legacy, return_properties, positional_count
):
    case = container_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    args = ("c1", PartitionKey(path="/pk"))
    kwargs = dict(zip(("id", "partition_key")[positional_count:], args[positional_count:]))
    result = _call_container_create(
        case, *args[:positional_count], **kwargs, return_properties=return_properties, read_timeout=None,
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy._item_context is case.item_context
    assert proxy.container_link == "dbs/db1/colls/c1"
    if return_properties:
        assert len(result) == 2
        assert isinstance(result[1], CosmosDict)
        assert result[1]["id"] == proxy.id
        assert result[1].get_response_headers()["x-ms-request-charge"] == "5.25"
    case.connection._set_container_properties_cache.assert_called_once()
    if use_legacy:
        case.backend.execute.assert_not_called()
        assert "read_timeout" not in case.connection.CreateContainer.call_args.kwargs
    else:
        case.connection.CreateContainer.assert_not_called()
        case.backend.execute.assert_called_once()


@pytest.mark.parametrize("partition_key", [None, PartitionKey(path="/pk"), PartitionKey(path=["/tenant", "/user"])])
def test_container_create_preserves_definition_and_none_semantics(container_create_case, partition_key):
    case = container_create_case
    policies = {
        "indexing_policy": {"indexingMode": "consistent", "automatic": False},
        "default_ttl": -1,
        "unique_key_policy": {"uniqueKeys": [{"paths": ["/code"]}]},
        "conflict_resolution_policy": {"mode": "LastWriterWins", "conflictResolutionPath": "/version"},
        "analytical_storage_ttl": -1,
        "computed_properties": [{"name": "total", "query": "SELECT VALUE c.price * c.quantity FROM c"}],
        "vector_embedding_policy": {"vectorEmbeddings": [{"path": "/vector", "dataType": "float32",
                                                        "dimensions": 8, "distanceFunction": "cosine"}]},
        "change_feed_policy": {"retentionDuration": 10},
        "full_text_policy": {"defaultLanguage": "en-US", "fullTextPaths": [{"path": "/text", "language": "en-US"}]},
    }
    _call_container_create(case, "c1", partition_key, **policies)
    body = json.loads(case.backend.prepared.body_bytes)
    expected = {"id": "c1"}
    for option, field in (
        ("indexing_policy", "indexingPolicy"), ("default_ttl", "defaultTtl"),
        ("unique_key_policy", "uniqueKeyPolicy"), ("conflict_resolution_policy", "conflictResolutionPolicy"),
        ("analytical_storage_ttl", "analyticalStorageTtl"), ("computed_properties", "computedProperties"),
        ("vector_embedding_policy", "vectorEmbeddingPolicy"), ("change_feed_policy", "changeFeedPolicy"),
        ("full_text_policy", "fullTextPolicy"),
    ):
        expected[field] = policies[option]
    if partition_key is not None:
        expected["partitionKey"] = dict(partition_key)
    assert body == expected


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10])
@pytest.mark.parametrize("autoscale", [False, True])
def test_container_create_preserves_throughput_headers_and_deadlines(container_create_case, timeout, autoscale):
    case = container_create_case
    throughput = ThroughputProperties(auto_scale_max_throughput=4000) if autoscale else 400
    _call_container_create(
        case, "c1", PartitionKey(path="/pk"), offer_throughput=throughput, timeout=timeout,
        initial_headers={"x-my-app": "provisioner"}, throughput_bucket=7,
    )
    prepared = case.backend.prepared
    assert prepared.op == OP_CREATE_CONTAINER
    assert prepared.item_id == "db1"
    assert prepared.headers["initialHeaders"] == {"x-my-app": "provisioner"}
    assert prepared.headers["throughputBucket"] == 7
    assert prepared.headers.get(Constants.OVERALL_TIMEOUT_SECONDS) == timeout
    if autoscale:
        assert json.loads(prepared.headers["autoUpgradePolicy"]) == {"maxThroughput": 4000}
    else:
        assert prepared.headers["offerThroughput"] == 400
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout": False}, {"timeout": True}, {"timeout": 0}, {"timeout": -1}, {"timeout": 0.5},
        {"timeout": "10"}, {"timeout": float("nan")}, {"timeout": float("inf")},
        {"timeout": 2**64 - 1}, {"timeout": 10**400}, {"connection_timeout": 1},
        {"raw_request_hook": lambda request: None}, {"raw_response_hook": lambda response: None},
        {"unknown_option": True}, {"initial_headers": {"User-Agent": "custom"}},
        {"initial_headers": {"X-MS-VERSION": "custom"}}, {"initial_headers": {"Accept": "custom"}},
        {"initial_headers": {"Cache-Control": "custom"}}, {"request_options": {"timeout": 10}},
        {"request_options": {Constants.ContainerRID: "unexpected"}},
    ],
)
def test_container_create_unsupported_calls_never_fall_back(container_create_case, kwargs):
    case = container_create_case
    before = rust_compatibility_fallback_count()
    hook = MagicMock()
    with pytest.raises(NotImplementedError, match="create_container.*legacy Python"):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), response_hook=hook, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("use_legacy", [False, True])
def test_container_create_keeps_isolated_hook_headers_and_falsey_callable(container_create_case, use_legacy):
    case = container_create_case
    if use_legacy:
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
        case, "c1", PartitionKey(path="/pk"), return_properties=True, response_hook=Hook(),
    )
    assert len(calls) == 1
    assert calls[0][1] is properties
    assert proxy.id == properties["id"]
    assert properties.get_response_headers()["x-ms-request-charge"] == "5.25"
    assert calls[0][0] is not case.connection.last_response_headers


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
        ({"if_match": "v1"}, {"If-Match": "v1"}), ({"if_none_match": "v1"}, {"If-None-Match": "v1"}),
    ],
)
def test_container_create_preserves_conditional_headers(container_create_case, use_legacy, kwargs, expected):
    case = container_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_container_create(case, "c1", PartitionKey(path="/pk"), **kwargs)
    assert caught == []
    if use_legacy:
        call = case.connection.CreateContainer.call_args
        headers = flatten_options_to_headers(call.kwargs["options"])
        assert "etag" not in call.kwargs
    else:
        headers = case.backend.prepared.headers
        case.connection.CreateContainer.assert_not_called()
    assert {key: headers[key] for key in ("If-Match", "If-None-Match") if key in headers} == expected


@pytest.mark.parametrize(
    "kwargs, error_type",
    [
        ({"etag": "v1"}, ValueError), ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"etag": "", "match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"etag": "v1", "match_condition": "invalid"}, TypeError),
    ],
)
def test_container_create_invalid_conditions_fail_before_dispatch(container_create_case, kwargs, error_type):
    case = container_create_case
    with pytest.raises(error_type):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("failure_source", ["hook", "backend"])
@pytest.mark.parametrize("error_type", [ValueError, NotImplementedError, ServiceRequestError, asyncio.CancelledError])
def test_container_create_errors_never_replay(container_create_case, failure_source, error_type):
    case = container_create_case
    error = error_type("create failed")
    hook = MagicMock(side_effect=error if failure_source == "hook" else None)
    if failure_source == "backend":
        case.backend.execute.side_effect = error
    before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as raised:
        _call_container_create(case, "c1", PartitionKey(path="/pk"), response_hook=hook)
    assert raised.value is error
    assert hook.call_count == (1 if failure_source == "hook" else 0)
    case.backend.execute.assert_called_once()
    case.connection.CreateContainer.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("status", [400, 403, 404, 409, 412, 429, 500])
def test_container_create_service_errors_preserve_status_and_never_replay(container_create_case, status):
    case = container_create_case
    case.backend.response = BackendResponse(
        status_code=status, headers=CaseInsensitiveDict({"x-ms-activity-id": "failed"}),
        body=b'{"message":"create failed"}',
    )
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_container_create(case, "c1", PartitionKey(path="/pk"), response_hook=hook)
    assert raised.value.status_code == status
    if status == 409:
        assert isinstance(raised.value, CosmosResourceExistsError)
    if status == 404:
        assert isinstance(raised.value, CosmosResourceNotFoundError)
    hook.assert_not_called()
    case.backend.execute.assert_called_once()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True])
def test_container_get_or_create_still_creates_after_404(container_create_case, use_legacy):
    case = container_create_case
    missing = CosmosResourceNotFoundError(status_code=404, message="missing")
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    case.connection.ReadContainer = mock_type(side_effect=missing)
    if use_legacy:
        case.connection._backend = case.legacy_backend
    else:
        case.backend.execute.side_effect = [
            BackendResponse(status_code=404, headers=CaseInsensitiveDict(), body=b'{"message":"missing"}'),
            _created_container_response(),
        ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = _call_container_create(
            case, "c1", PartitionKey(path="/pk"), method="create_container_if_not_exists",
        )
    assert result.id == "c1"
    if use_legacy:
        case.connection.CreateContainer.assert_called_once()
        assert "sessionToken" not in case.connection.CreateContainer.call_args.kwargs["options"]
        assert "populateQueryMetrics" not in case.connection.CreateContainer.call_args.kwargs["options"]
    else:
        assert case.backend.execute.call_count == 2
        assert case.backend.execute.call_args.args[0].op == OP_CREATE_CONTAINER
        case.connection.CreateContainer.assert_not_called()


@pytest.fixture(params=[False, True], ids=["existing", "missing"])
def container_get_or_create_case(container_create_case, request):
    case = container_create_case
    case.missing = request.param
    case.existing_properties = CosmosDict(
        {"id": "c1", "_rid": "rid1", "partitionKey": {"paths": ["/original"]}, "defaultTtl": 10},
        response_headers=CaseInsensitiveDict({"x-ms-request-charge": "2"}),
    )
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    if case.missing:
        case.connection.ReadContainer = mock_type(
            side_effect=CosmosResourceNotFoundError(status_code=404, message="missing")
        )
        case.backend.execute.side_effect = [
            BackendResponse(status_code=404, headers=CaseInsensitiveDict(), body=b'{"message":"missing"}'),
            _created_container_response(),
        ]
    else:
        case.connection.ReadContainer = mock_type(return_value=case.existing_properties)
        case.backend.execute.side_effect = [
            BackendResponse(status_code=200, headers=case.existing_properties.get_response_headers(),
                            body=json.dumps(case.existing_properties).encode()),
        ]
    return case


def _call_get_or_create(case, **kwargs):
    return _call_container_create(
        case, "c1", PartitionKey(path="/pk"), method="create_container_if_not_exists", **kwargs
    )


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_get_or_create_preserves_shapes_and_existing_settings(
    container_get_or_create_case, use_legacy, return_properties, positional_count
):
    case = container_get_or_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    args = ("c1", PartitionKey(path="/pk"))
    kwargs = dict(zip(("id", "partition_key")[positional_count:], args[positional_count:]))
    hook = MagicMock()
    result = _call_container_create(
        case, *args[:positional_count], **kwargs, method="create_container_if_not_exists",
        default_ttl=99, offer_throughput=400, return_properties=return_properties,
        read_timeout=None, response_hook=hook, timeout=10,
        initial_headers={"x-company-trace": "setup"},
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy._item_context is case.item_context
    assert proxy.container_link == "dbs/db1/colls/c1"
    hook.assert_called_once()
    properties = hook.call_args.args[1]
    assert hook.call_args.args[0]["x-ms-request-charge"] == ("5.25" if case.missing else "2")
    if return_properties:
        assert result[1] is properties
        assert isinstance(properties, CosmosDict)
    if not case.missing:
        assert properties["partitionKey"]["paths"] == ["/original"]
        assert properties["defaultTtl"] == 10
    case.connection._set_container_properties_cache.assert_called_once()
    if use_legacy:
        case.backend.execute.assert_not_called()
        read = case.connection.ReadContainer.call_args
        assert "offerThroughput" not in read.kwargs["options"]
        assert "read_timeout" not in read.kwargs
        assert "response_hook" not in read.kwargs
        assert read.kwargs["timeout"] == 10
        assert case.connection.CreateContainer.call_count == int(case.missing)
        if case.missing:
            create = case.connection.CreateContainer.call_args
            assert create.kwargs["collection"]["defaultTtl"] == 99
            assert create.kwargs["options"]["offerThroughput"] == 400
    else:
        case.connection.ReadContainer.assert_not_called()
        case.connection.CreateContainer.assert_not_called()
        operations = [call.args[0] for call in case.backend.execute.call_args_list]
        assert [op.op for op in operations] == (
            [OP_READ_CONTAINER, OP_CREATE_CONTAINER] if case.missing else [OP_READ_CONTAINER]
        )
        for op in operations:
            assert op.headers["__overall_timeout_seconds"] == 10
            assert op.headers["initialHeaders"]["x-company-trace"] == "setup"
        assert "offerThroughput" not in operations[0].headers
        if case.missing:
            assert json.loads(operations[1].body_bytes)["defaultTtl"] == 99
            assert operations[1].headers["offerThroughput"] == 400


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": float("nan")}, {"timeout": float("inf")},
    {"timeout": 2**64}, {"timeout": "10"}, {"connection_timeout": 1},
    {"raw_request_hook": lambda request: None}, {"raw_response_hook": lambda response: None},
    {"initial_headers": {"User-Agent": "override"}}, {"unknown_option": None},
    {"populate_quota_info": True}, {"populate_partition_key_range_statistics": False},
    {"request_options": {Constants.ContainerRID: "rid1"}},
])
def test_container_get_or_create_preflights_both_steps(container_get_or_create_case, kwargs):
    case = container_get_or_create_case
    hook = MagicMock()
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="create_container_if_not_exists"):
        _call_get_or_create(case, response_hook=hook, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    hook.assert_not_called()
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("kwargs, error", [
    ({"etag": "v1"}, ValueError),
    ({"match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": "invalid"}, TypeError),
])
def test_container_get_or_create_validates_conditions_before_read(
    container_get_or_create_case, use_legacy, kwargs, error
):
    case = container_get_or_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(error):
        _call_get_or_create(case, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("kwargs, expected", [
    ({"match_condition": MatchConditions.IfModified, "etag": '"v1"'}, ("If-None-Match", '"v1"')),
    ({"match_condition": MatchConditions.IfNotModified, "etag": '"v1"'}, ("If-Match", '"v1"')),
    ({"match_condition": MatchConditions.IfMissing, "etag": "unused"}, ("If-None-Match", "*")),
    ({"match_condition": MatchConditions.IfPresent, "etag": "unused"}, ("If-Match", "*")),
])
def test_container_get_or_create_forwards_conditions_without_ignored_warnings(
    container_get_or_create_case, use_legacy, kwargs, expected
):
    case = container_get_or_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_get_or_create(case, **kwargs)
    assert not caught
    if use_legacy:
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
    else:
        for call in case.backend.execute.call_args_list:
            assert CaseInsensitiveDict(call.args[0].headers)[expected[0]] == expected[1]
        case.connection.ReadContainer.assert_not_called()
        case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("error", [
    CosmosResourceNotFoundError(status_code=404, message="callback failure"),
    ValueError("callback failure"),
])
def test_container_get_or_create_does_not_interpret_hook_errors_as_missing(
    container_get_or_create_case, use_legacy, error
):
    case = container_get_or_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _call_get_or_create(case, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    case.connection._set_container_properties_cache.assert_not_called()
    if use_legacy:
        case.backend.execute.assert_not_called()
        case.connection.ReadContainer.assert_called_once()
        assert case.connection.CreateContainer.call_count == int(case.missing)
    else:
        assert case.backend.execute.call_count == (2 if case.missing else 1)
        case.connection.ReadContainer.assert_not_called()
        case.connection.CreateContainer.assert_not_called()


def test_container_get_or_create_falsey_hook_has_isolated_headers(container_get_or_create_case):
    case = container_get_or_create_case
    seen = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, properties):
            assert headers is not properties.get_response_headers()
            headers["X-MS-REQUEST-CHARGE"] = "changed"
            case.connection.last_response_headers = {"x-ms-request-charge": "another request"}
            seen.append(properties)

    _, properties = _call_get_or_create(case, return_properties=True, response_hook=Hook())
    assert seen == [properties]
    assert properties.get_response_headers()["x-ms-request-charge"] == ("5.25" if case.missing else "2")


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("status", [401, 403, 404, 409, 429, 500])
def test_container_get_or_create_propagates_failures_without_replay(
    container_get_or_create_case, use_legacy, status
):
    case = container_get_or_create_case
    if not case.missing and status == 404:
        pytest.skip("A genuine initial 404 is the create branch, covered separately.")
    error_type = CosmosResourceExistsError if status == 409 else (
        CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError
    )
    error = error_type(status_code=status, message="failure")
    if use_legacy:
        case.connection._backend = case.legacy_backend
        target = case.connection.CreateContainer if case.missing else case.connection.ReadContainer
        target.side_effect = error
    else:
        replies = []
        if case.missing:
            replies.append(BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'))
        replies.append(BackendResponse(status_code=status, headers={}, body=b'{"message":"failure"}'))
        case.backend.execute.side_effect = replies
    hook = MagicMock()
    with pytest.raises(error_type) as raised:
        _call_get_or_create(case, response_hook=hook)
    assert raised.value.status_code == status
    hook.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    if use_legacy:
        case.connection.ReadContainer.assert_called_once()
        assert case.connection.CreateContainer.call_count == int(case.missing)
    else:
        assert case.backend.execute.call_count == (2 if case.missing else 1)
        case.connection.ReadContainer.assert_not_called()
        case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("error", [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()])
def test_container_get_or_create_binding_errors_never_fall_back(container_get_or_create_case, error):
    case = container_get_or_create_case
    replies = []
    if case.missing:
        replies.append(BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'))
    case.backend.execute.side_effect = replies + [error]
    with pytest.raises(type(error)) as raised:
        _call_get_or_create(case)
    assert raised.value is error
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    assert case.backend.execute.call_count == (2 if case.missing else 1)


@pytest.mark.parametrize("use_legacy", [False, True])
def test_container_get_or_create_preserves_bodyless_conditional_results(container_get_or_create_case, use_legacy):
    case = container_get_or_create_case
    empty = CosmosDict({}, response_headers=CaseInsensitiveDict({"etag": '"v1"'}))
    if use_legacy:
        case.connection._backend = case.legacy_backend
        target = case.connection.CreateContainer if case.missing else case.connection.ReadContainer
        target.return_value = empty
    else:
        replies = []
        if case.missing:
            replies.append(BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'))
        replies.append(BackendResponse(status_code=201 if case.missing else 304, headers=empty.get_response_headers(),
                                       body=b""))
        case.backend.execute.side_effect = replies
    hook = MagicMock()
    kwargs = dict(match_condition=MatchConditions.IfMissing, return_properties=True, response_hook=hook)
    if case.missing:
        with pytest.raises(KeyError, match="id"):
            _call_get_or_create(case, **kwargs)
    else:
        proxy, properties = _call_get_or_create(case, **kwargs)
        assert proxy.id == "c1"
        assert properties == {}
        case.connection.CreateContainer.assert_not_called()
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}


def test_container_get_or_create_explicit_legacy_keeps_transport_options(container_get_or_create_case):
    case = container_get_or_create_case
    case.connection._backend = case.legacy_backend
    _call_get_or_create(case, timeout=0.5, connection_timeout=2)
    case.backend.execute.assert_not_called()
    calls = [case.connection.ReadContainer.call_args]
    if case.missing:
        calls.append(case.connection.CreateContainer.call_args)
    for call in calls:
        assert call.kwargs["timeout"] == 0.5
        assert call.kwargs["connection_timeout"] == 2


def test_container_get_or_create_preflight_does_not_mutate_caller_options():
    from copy import deepcopy
    from azure.cosmos._helpers._request_container import prepare_container_get_or_create_read

    kwargs = {"request_options": {"initialHeaders": {"x-company-trace": "setup"}},
              "match_condition": MatchConditions.IfMissing, "etag": "unused", "timeout": 10}
    original = deepcopy(kwargs)
    options, remaining, eligible = prepare_container_get_or_create_read(
        kwargs, initial_headers=None, offer_throughput=400
    )
    assert eligible
    assert kwargs == original
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "*"}
    assert "offerThroughput" not in options
    assert remaining == {"timeout": 10}


# --- dispatch registration ------------------------------------------------


def test_create_container_is_a_single_response_operation():
    """One create, one reply: it dispatches through ``execute``, not the paged path."""
    assert OP_TO_BINDING_METHOD[OP_CREATE_CONTAINER] == "create_container"
    assert OP_CREATE_CONTAINER not in QUERY_TO_BINDING_METHOD


def test_container_feeds_are_paged_operations():
    """Both feeds dispatch through ``execute_pages``, never the single-reply path."""
    assert QUERY_TO_BINDING_METHOD[OP_LIST_CONTAINERS] == "list_containers"
    assert QUERY_TO_BINDING_METHOD[OP_QUERY_CONTAINERS] == "query_containers"
    assert OP_LIST_CONTAINERS not in OP_TO_BINDING_METHOD
    assert OP_QUERY_CONTAINERS not in OP_TO_BINDING_METHOD


# --- create_container request shape --------------------------------------


def test_create_container_prepared_names_the_database_and_carries_the_definition():
    """The database name rides in ``item_id`` because the container has no id yet,
    and the whole definition -- partition key, indexing policy, TTL -- rides in the
    body. Scope is account-shaped: empty container link, ``"[]"`` partition header."""
    definition = {
        "id": "c1",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash"},
        "defaultTtl": 60,
    }
    prepared = build_create_container_prepared(
        "dbs/db1",
        definition,
        {"offerThroughput": 400, "initialHeaders": {"x-custom": "value"}},
        kwargs={"timeout": 3.5},
    )

    assert prepared.op == OP_CREATE_CONTAINER
    assert prepared.item_id == "db1"
    assert prepared.container_link == ""
    assert prepared.partition_key_header == "[]"
    assert json.loads(prepared.body_bytes) == definition
    assert prepared.headers["offerThroughput"] == 400
    assert prepared.headers["initialHeaders"] == {"x-custom": "value"}
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 3.5


def test_create_container_prepared_drops_the_session_token():
    """A collection is a master resource, so the legacy path never attaches a
    session token to this request either. Leaving one in would send a token the
    other engine does not send."""
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"sessionToken": "s1", "offerThroughput": 400},
    )

    assert "sessionToken" not in prepared.headers
    assert prepared.headers["offerThroughput"] == 400


def test_create_container_prepared_rejects_a_link_with_no_database():
    """A link with the prefix but no name would otherwise create the container in a
    database literally named ``dbs``."""
    with pytest.raises(ValueError):
        build_create_container_prepared("dbs/", {"id": "c1"}, {})


def test_create_container_prepared_drops_a_null_initial_headers():
    """``create_container_if_not_exists`` forwards ``initial_headers=None`` unguarded
    when it falls through to the create, which puts a ``None`` in the options. That
    is not a header value -- copying it through makes the binding reject the whole
    request with a type error, so a customer who never passed any headers cannot
    create a container at all."""
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"initialHeaders": None, "offerThroughput": 400},
    )

    assert "initialHeaders" not in prepared.headers
    assert prepared.headers["offerThroughput"] == 400


def test_list_containers_sends_no_query_body():
    """A read feed has no SQL. The page adapter refuses a feed op that is not on its
    parameterless list, so leaving ``list_containers`` off it makes every
    ``list_containers`` call fail once it reaches the binding."""
    from azure.cosmos._backend.rust import _binding_request_from_page

    request = _binding_request_from_page(
        build_list_containers_prepared_query(
            path="dbs/db1/colls",
            options={},
            req_headers={},
        )
    )

    assert request.body_bytes == b""
    assert request.container_link == "dbs/db1"


def test_query_containers_sends_the_query_body():
    """The query payload must arrive as JSON in ``body_bytes``, not as a URL parameter."""
    from azure.cosmos._backend.rust import _binding_request_from_page

    request = _binding_request_from_page(
        build_query_containers_prepared_query(
            path="dbs/db1/colls",
            query_payload={"query": "SELECT * FROM c"},
            options={},
            req_headers={},
        )
    )

    assert json.loads(request.body_bytes) == {"query": "SELECT * FROM c"}


# --- create_container eligibility ----------------------------------------


def test_create_container_is_rust_eligible_for_a_plain_create():
    """A create with only standard options must be routed to the Rust backend."""
    assert is_create_container_rust_eligible({"offerThroughput": 400}, {"timeout": 3.5}) is True


def test_create_container_is_not_rust_eligible_with_a_read_timeout():
    """A per-call socket timeout cannot run on the Rust create path."""
    assert is_create_container_rust_eligible({}, {"read_timeout": 2}) is False


def test_create_container_is_not_rust_eligible_with_an_intended_container_rid():
    """``_base.GetHeaders`` emits ``x-ms-cosmos-intended-collection-rid`` for every
    resource type except ``dbs``, which includes this one. The rust path has no
    equivalent, so running it there would drop a header legacy sends."""
    assert is_create_container_rust_eligible({Constants.ContainerRID: "rid1"}, {}) is False


# --- create_container routing --------------------------------------------


def test_sync_create_container_routes_to_rust_and_fires_the_hook_once():
    """The coordinator runs the create through the backend, returns the created
    container, records the response headers, and fires ``response_hook`` once."""
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _RustBackend()
    hooks = []

    result = ContainerHelper(connection, backend).create_container(
        "dbs/db1",
        {"id": "c1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_CREATE_CONTAINER
    assert backend.prepared.item_id == "db1"
    connection.CreateContainer.assert_not_called()
    assert connection.last_response_headers["x-ms-request-charge"] == "5.25"
    assert len(hooks) == 1
    assert hooks[0][1] == {"id": "c1", "_rid": "rid1"}


def test_sync_create_container_explicit_legacy_helper_preserves_read_timeout():
    """The legacy call gets the definition and options unchanged, and the hook still
    fires exactly once with the same shape as on the rust path."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        CreateContainer=MagicMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = ContainerHelper(connection, LEGACY_BACKEND).create_container(
        "dbs/db1",
        {"id": "c1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hooks.append((headers, body)),
        kwargs={"read_timeout": 2},
    )

    assert result == legacy_body
    call = connection.CreateContainer.call_args
    assert call.kwargs["database_link"] == "dbs/db1"
    assert call.kwargs["collection"] == {"id": "c1"}
    assert call.kwargs["read_timeout"] == 2
    assert len(hooks) == 1
    assert hooks[0][0] == legacy_headers
    assert hooks[0][1] == legacy_body


def test_async_create_container_routes_to_rust():
    """The async coordinator builds the same request as the sync one. It is separate
    code -- the async backend awaits its request builder -- so it can break alone."""
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _AsyncRustBackend()

    result = asyncio.run(
        AsyncContainerHelper(connection, backend).create_container(
            "dbs/db1",
            {"id": "c1"},
            {"offerThroughput": 400},
        )
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_CREATE_CONTAINER
    assert backend.prepared.item_id == "db1"
    connection.CreateContainer.assert_not_called()


# --- feed request shape ---------------------------------------------------


def test_list_containers_prepared_carries_the_owning_database_link():
    """``container_link`` holds a database link, not a container link: the feed is
    scoped to a database and this is the only typed field that can carry it."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_prepared_query(
        path=path,
        options={"maxItemCount": 10, "continuation": "ct-1"},
        req_headers={},
    )

    assert prepared.op == OP_LIST_CONTAINERS
    assert prepared.container_link == "dbs/db1"
    assert prepared.max_item_count == 10
    assert prepared.continuation == "ct-1"
    assert prepared.query is None


def test_query_containers_prepared_carries_the_query_and_the_database_link():
    """The prepared query must name the owning database and carry the full query string and parameters."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_query_containers_prepared_query(
        path=path,
        query_payload={
            "query": "SELECT * FROM c WHERE c.id=@id",
            "parameters": [{"name": "@id", "value": "c1"}],
        },
        options={},
        req_headers={},
    )

    assert prepared.op == OP_QUERY_CONTAINERS
    assert prepared.container_link == "dbs/db1"
    assert prepared.query == "SELECT * FROM c WHERE c.id=@id"
    assert prepared.parameters == ({"name": "@id", "value": "c1"},)


def test_container_feed_headers_keep_the_customers_own_headers():
    """A plain header the customer set survives into the nested ``initialHeaders``
    entry the binding forwards verbatim. Left flat it would be dropped by the
    option-key translation on the rust side."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_prepared_query(
        path=path,
        options={"initialHeaders": {"x-custom-tag": "value"}},
        req_headers={"x-custom-tag": "value"},
    )

    assert prepared.headers["initialHeaders"] == {"x-custom-tag": "value"}


# --- feed eligibility -----------------------------------------------------


def _list_gate(path="dbs/db1/colls", options=None, kwargs=None, resource_type=_COLLECTION):
    """Thin wrapper over ``can_use_rust_backend_for_list_containers_page`` so test cases read cleanly."""
    return can_use_rust_backend_for_list_containers_page(
        path=path,
        options=options or {},
        kwargs=kwargs or {},
        is_query_plan=False,
        resource_type=resource_type,
    )


def test_list_containers_page_is_rust_eligible_for_a_plain_feed():
    """A feed page with no special options must be eligible for the Rust backend."""
    assert _list_gate() is True


def test_list_containers_page_is_not_eligible_when_the_path_names_no_database():
    """Without a database name the rust page has nothing to run against, so the call
    belongs on legacy rather than failing."""
    assert _list_gate(path="dbs//colls") is False
    assert _list_gate(path="dbs/db1/docs") is False


def test_list_containers_page_is_not_eligible_for_another_resource_type():
    """The database and item feeds have their own gates and their own binding entry
    points; this one must not claim them."""
    assert _list_gate(resource_type=http_constants.ResourceType.Database) is False


def test_list_containers_page_is_not_eligible_with_a_read_timeout():
    """A socket-level timeout or sub-second timeout must stay on the legacy path."""
    assert _list_gate(kwargs={"read_timeout": 2}) is False
    assert _list_gate(options={Constants.Kwargs.TIMEOUT: 0.5}) is False


def test_query_containers_page_is_rust_eligible_for_a_dict_query():
    """A dict-form query (``application/query+json``) must be routed to the Rust backend."""
    assert can_use_rust_backend_for_query_containers_page(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is True


def test_query_containers_page_is_not_eligible_for_a_string_query():
    """The legacy-only SqlQuery mode posts a bare string as ``text/plain`` while the
    driver always posts ``application/query+json``. Different bytes on the wire, so
    that case stays on legacy."""
    assert can_use_rust_backend_for_query_containers_page(
        path="dbs/db1/colls",
        query_payload="SELECT * FROM c",
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is False


def test_query_containers_page_is_not_eligible_for_a_query_plan():
    """A query-plan request must stay on legacy; Rust has no query-plan endpoint for containers."""
    assert can_use_rust_backend_for_query_containers_page(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=True,
        resource_type=_COLLECTION,
    ) is False


# --- public method behavior ----------------------------------------------


def test_create_container_preserves_conditional_headers_without_ignored_warnings():
    """Conditional options still reach the builder, without misleading warnings."""
    from azure.core import MatchConditions
    from azure.cosmos.database import DatabaseProxy
    from azure.cosmos.partition_key import PartitionKey

    captured = {}

    def fake_create_container(self, database_link, definition, request_options, *, response_hook=None, kwargs=None):
        """Capture the arguments so the test can inspect what the public method forwarded."""
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
    assert captured["request_options"]["accessCondition"] == {"type": "IfMatch", "condition": "e1"}
    assert "sessionToken" not in captured["request_options"]
    assert "session_token" not in captured["kwargs"]
    assert "etag" not in captured["kwargs"]
    assert "match_condition" not in captured["kwargs"]
    assert captured["definition"]["id"] == "c1"


def test_create_container_still_rejects_an_etag_without_a_match_condition():
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
        with pytest.raises(ValueError, match="'etag' specified without 'match_condition'"):
            proxy.create_container("c1", PartitionKey(path="/pk"), etag="e1")


# --- end-to-end feed dispatch --------------------------------------------
#
# The gates and builders above are only half of it. The other half is the
# dispatch inside the client connection that picks them: it tells a container
# feed apart from a database feed and an item feed by resource type alone, and a
# wrong arm there sends the call to the wrong binding entry point. These drive
# the real dispatch with a fake backend.


class _CapturingPagedBackend(CosmosBackend):
    """Records the paged request it was handed and yields one canned page."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body to yield and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    def execute_pages(self, prepared):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield QueryPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    def execute(self, prepared):
        """Fail immediately — a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


class _CapturingAsyncPagedBackend(AsyncCosmosBackend):
    """Record the page request produced by asynchronous container methods."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    async def execute_pages(self, prepared):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield QueryPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    async def execute(self, prepared):
        """Fail immediately — a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


def _new_sync_connection() -> SyncConnection:
    """Build a minimal ``SyncConnection`` with no live transport, for dispatch tests."""
    conn = SyncConnection.__new__(SyncConnection)
    conn._response_state = ResponseHeaderState()
    conn._backend = LEGACY_BACKEND
    conn._query_compatibility_mode = SyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.resource_tokens = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_executor = None
    return conn


def _new_async_connection() -> AsyncConnection:
    """Build a minimal ``AsyncConnection`` with no live transport, for dispatch tests."""
    conn = AsyncConnection.__new__(AsyncConnection)
    conn._response_state = ResponseHeaderState()
    conn._backend = ASYNC_LEGACY_BACKEND
    conn._query_compatibility_mode = AsyncConnection._QueryCompatibilityMode.Query
    conn.default_headers = {}
    conn.connection_policy = ConnectionPolicy()
    conn._global_endpoint_manager = MagicMock()
    conn._routing_map_provider = MagicMock()
    conn.pipeline_client = MagicMock()
    conn._CosmosClientConnection__container_properties_cache = {}
    conn.last_response_headers = CaseInsensitiveDict()
    conn.session = None
    conn.UseMultipleWriteLocations = False
    conn.master_key = None
    conn.resource_tokens = None
    conn.aad_credentials = None
    conn.client_id = None
    conn.availability_strategy = None
    conn.availability_strategy_max_concurrency = None
    return conn


_CONTAINER_PAGE = b'{"DocumentCollections":[{"id":"c1"},{"id":"c2"}]}'


def test_sync_list_containers_dispatches_to_the_container_feed():
    """The read-feed arm keyed on ``Collection`` builds a container page carrying
    the owning database, and the containers come back out of the
    ``DocumentCollections`` envelope. A database feed uses ``Databases``; reading
    the wrong key yields an empty list instead of an error."""
    conn = _new_sync_connection()
    backend = _CapturingPagedBackend(_CONTAINER_PAGE)
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


def test_sync_query_containers_dispatches_to_the_container_query_feed():
    """The query arm keys on ``Collection`` and a query payload, producing a ``OP_QUERY_CONTAINERS`` request."""
    conn = _new_sync_connection()
    backend = _CapturingPagedBackend(_CONTAINER_PAGE)
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


def test_async_list_containers_dispatches_to_the_container_feed():
    """The async dispatch is separate code with its own arm, so it can break alone."""
    async def _run():
        """Drive the async dispatch arm for a list feed so it can be verified independently."""
        conn = _new_async_connection()
        backend = _CapturingAsyncPagedBackend(_CONTAINER_PAGE)
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


def test_async_query_containers_dispatches_to_the_container_query_feed():
    """The async query arm builds an ``OP_QUERY_CONTAINERS`` request, separate from the list arm."""
    async def _run():
        """Drive the async dispatch for a query feed."""
        conn = _new_async_connection()
        backend = _CapturingAsyncPagedBackend(_CONTAINER_PAGE)
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


# --- container read -------------------------------------------------------


def _read_container_response() -> BackendResponse:
    """Return a canned 200 OK reply carrying a container body with a partition key."""
    return BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
        body=b'{"id":"c1","_rid":"rid1","partitionKey":{"paths":["/pk"],"kind":"Hash"}}',
    )


def test_read_container_prepared_carries_both_names():
    """The driver reads a container by name, so the request has to name the database
    and the container. Both come out of the one link the proxy holds."""
    prepared = build_read_container_prepared("dbs/db1/colls/c1", {})

    assert prepared.op == OP_READ_CONTAINER
    assert prepared.container_link == "dbs/db1/colls/c1"


def test_read_container_prepared_accepts_a_link_with_slashes():
    """Leading and trailing slashes in the link must be stripped before the request is built."""
    prepared = build_read_container_prepared("/dbs/db1/colls/c1/", {})

    assert prepared.container_link == "dbs/db1/colls/c1"


@pytest.mark.parametrize(
    "link",
    ["dbs/db1", "dbs/db1/colls", "dbs/db1/colls/", "dbs//colls/c1", "colls/c1"],
)
def test_read_container_prepared_rejects_a_link_missing_either_name(link):
    """A half-formed link would reach the service as a request for a container
    literally named ``colls``, and the not-found that came back would say nothing
    about the real problem."""
    with pytest.raises(ValueError):
        build_read_container_prepared(link, {})


def test_read_container_prepared_drops_the_session_token():
    """A container is a master resource, so neither engine sends a session token on
    this read. Sending one on rust only would be a difference between the two."""
    prepared = build_read_container_prepared(
        "dbs/db1/colls/c1",
        {"sessionToken": "0:1#22"},
    )

    assert "sessionToken" not in prepared.headers


def test_read_container_is_rust_eligible_for_a_plain_read():
    """A read with no special options must be eligible for the Rust backend."""
    assert is_read_container_rust_eligible({}, {}) is True


@pytest.mark.parametrize(
    "option",
    ["populatePartitionKeyRangeStatistics", "populateQuotaInfo"],
)
def test_read_container_is_rust_eligible_when_statistics_were_asked_for(option):
    """The binding forwards both metadata flags and preserves their returned data."""
    assert is_read_container_rust_eligible({option: True}, {}) is True


def test_sync_read_container_routes_to_rust_and_fires_the_hook_once():
    """The helper must use Rust, return the container, and fire ``response_hook`` exactly once."""
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _RustBackend(_read_container_response())
    hooks = []

    result = ContainerHelper(connection, backend).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hooks.append((headers, body)),
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()
    assert connection.last_response_headers["x-ms-request-charge"] == "1.0"
    assert len(hooks) == 1


def test_sync_read_container_explicit_legacy_helper_preserves_read_timeout():
    """Explicit legacy helper calls retain transport options; public reads reject them."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        ReadContainer=MagicMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = ContainerHelper(connection, LEGACY_BACKEND).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hooks.append((headers, body)),
        kwargs={"read_timeout": 2},
    )

    assert result == legacy_body
    call = connection.ReadContainer.call_args
    assert call.args[0] == "dbs/db1/colls/c1"
    assert call.kwargs["read_timeout"] == 2
    assert len(hooks) == 1


def test_read_container_does_not_pass_the_hook_to_the_legacy_call():
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
        kwargs={"read_timeout": 2, "response_hook": lambda *a: hooks.append("legacy")},
    )

    assert "response_hook" not in connection.ReadContainer.call_args.kwargs
    assert hooks == [{"id": "c1"}]


def test_async_read_container_routes_to_rust():
    """Async read must use the Rust backend without falling through to the legacy path."""
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _AsyncRustBackend(_read_container_response())

    result = asyncio.run(
        AsyncContainerHelper(connection, backend).read_container(
            "dbs/db1/colls/c1",
            {},
        )
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()


# --- async legacy fallback -------------------------------------------------
#
# ``AsyncContainerHelper`` is a separate module from the sync helper: it awaits
# its request builder and its legacy call. The rust-path tests above prove the
# request it builds; these prove the other branch -- that an option rust cannot
# honor still reaches the legacy call, and that the hook fires exactly once with
# the response's own headers on that branch too. Without them the async legacy
# arm is the one code path in this family with no coverage at all.


def test_async_create_container_explicit_legacy_helper_preserves_read_timeout():
    """Explicit legacy helper selection keeps its internal timeout plumbing."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        CreateContainer=AsyncMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, ASYNC_LEGACY_BACKEND).create_container(
            "dbs/db1",
            {"id": "c1"},
            {"offerThroughput": 400},
            response_hook=lambda headers, body: hooks.append((headers, body)),
            kwargs={"read_timeout": 2},
        )
    )

    assert result == legacy_body
    call = connection.CreateContainer.call_args
    assert call.kwargs["database_link"] == "dbs/db1"
    assert call.kwargs["collection"] == {"id": "c1"}
    assert call.kwargs["options"] == {"offerThroughput": 400}
    assert call.kwargs["read_timeout"] == 2
    assert "response_hook" not in call.kwargs
    assert len(hooks) == 1
    assert hooks[0][0] == legacy_headers
    assert hooks[0][1] == legacy_body


def test_async_read_container_explicit_legacy_helper_preserves_read_timeout():
    """Explicit legacy helper calls retain transport options and one response hook."""
    legacy_headers = CaseInsensitiveDict({"x-ms-request-charge": "1.0"})
    legacy_body = CosmosDict({"id": "c1", "_rid": "legacy"}, response_headers=legacy_headers)
    connection = SimpleNamespace(
        ReadContainer=AsyncMock(return_value=legacy_body),
        last_response_headers=legacy_headers,
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, ASYNC_LEGACY_BACKEND).read_container(
            "dbs/db1/colls/c1",
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
            kwargs={"read_timeout": 2, "response_hook": lambda *a: hooks.append("legacy")},
        )
    )

    assert result == legacy_body
    call = connection.ReadContainer.call_args
    assert call.args[0] == "dbs/db1/colls/c1"
    assert call.kwargs["read_timeout"] == 2
    # The helper owns the hook, so the legacy pipeline must not get a copy and
    # fire it a second time.
    assert "response_hook" not in call.kwargs
    assert len(hooks) == 1
    assert hooks[0][0] == legacy_headers


def test_async_create_container_fires_the_hook_once_on_the_rust_path():
    """The async Rust create calls the customer's response hook exactly once."""
    connection = SimpleNamespace(
        CreateContainer=AsyncMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncRustBackend()).create_container(
            "dbs/db1",
            {"id": "c1"},
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
        )
    )

    assert len(hooks) == 1
    assert hooks[0][1] is result
    assert hooks[0][0] == result.get_response_headers()
    connection.CreateContainer.assert_not_called()


def test_async_read_container_fires_the_hook_once_on_the_rust_path():
    """Async Rust read must fire the customer's response hook exactly once with the real headers."""
    connection = SimpleNamespace(
        ReadContainer=AsyncMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncRustBackend(_read_container_response())).read_container(
            "dbs/db1/colls/c1",
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
        )
    )

    assert len(hooks) == 1
    assert hooks[0][1] == result
    assert hooks[0][1] is not result
    assert hooks[0][0] == result.get_response_headers()
    connection.ReadContainer.assert_not_called()
