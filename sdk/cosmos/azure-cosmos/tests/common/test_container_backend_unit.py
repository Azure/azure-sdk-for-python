# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Maintained Rust container unit coverage, without legacy implementation imports.

Creation and get-or-create checks protect request preparation, return shapes,
deadlines, hooks, and errors without replay. Read helpers and feed builders
retain their Rust coverage here. Temporary legacy comparisons and private
connection-router checks live in test_container_legacy_unit.py.

All fakes, no Cosmos account.
"""

from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options

import asyncio
import ast
import importlib
import inspect
import json
import warnings
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import partial
from threading import Barrier, Lock
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import ServiceRequestError
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _base as base
from azure.cosmos import http_constants
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import (
    OP_CREATE_CONTAINER,
    OP_LIST_CONTAINERS,
    OP_QUERY_CONTAINERS,
    OP_READ_CONTAINER,
    OP_TO_BINDING_FUNCTION_NAME,
    STATELESS_PAGE_BINDING_FUNCTION_NAMES,
)
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_container import (
    build_create_container_prepared,
    build_read_container_prepared,
    is_create_container_rust_eligible,
    is_read_container_rust_eligible,
)
from azure.cosmos._helpers._container_operations import ContainerHelper
from azure.cosmos._helpers._client_context import (
    ClientOperationDefaults,
    CosmosClientContext,
)
from azure.cosmos._query_rust_routing import (
    build_list_containers_page,
    build_query_containers_page,
    can_use_rust_list_containers,
    can_use_rust_query_containers,
)
from azure.cosmos.aio._helpers._container_operations import AsyncContainerHelper
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import (
    CosmosClientTimeoutError, CosmosHttpResponseError, CosmosResourceExistsError, CosmosResourceNotFoundError,
)
from azure.cosmos.offer import ThroughputProperties


from common.container_backend_stubs import (
    _FakeBackend,
    _AsyncFakeBackend,
    _created_container_response,
    _call_container_create,
    _call_get_or_create,
    make_container_create_case,
    make_container_get_or_create_case,
)


@pytest.fixture(params=["sync", "async"])
def container_create_case(request):
    return make_container_create_case(request.param == "async")


@pytest.fixture(params=[False, True], ids=["existing", "missing"])
def container_get_or_create_case(container_create_case, request):
    return make_container_get_or_create_case(container_create_case, request.param)


@pytest.fixture(params=["create", "existing", "missing"])
def container_create_validation_case(container_create_case, request):
    case = container_create_case
    case.method = "create_container"
    if request.param != "create":
        case = make_container_get_or_create_case(case, request.param == "missing")
        case.method = "create_container_if_not_exists"
    return case


_COLLECTION = http_constants.ResourceType.Collection


def test_container_test_dependencies_do_not_require_legacy_rust(monkeypatch):
    """Reload test helpers and exercise creation with legacy imports forbidden."""
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
        "common.test_container_legacy_unit",
        "common.container_feed_stubs",
    }

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        absolute = (
            resolve_name("." * level + name, globals["__package__"]) if level else name
        )
        requested = {absolute, *(f"{absolute}.{item}" for item in (fromlist or ()))}
        if requested & forbidden:
            raise ImportError(
                f"Rust container tests require legacy code: {requested & forbidden}"
            )
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    shared = Path(__file__).with_name("container_backend_stubs.py")
    helpers = runpy.run_path(str(shared))
    module = runpy.run_path(__file__)
    for is_async in (False, True):
        case = helpers["make_container_create_case"](is_async)
        proxy, properties = module["_call_container_create"](
            case, "c1", PartitionKey("/pk"), return_properties=True
        )
        assert proxy.id == properties["id"] == "c1"
        case.connection.CreateContainer.assert_not_called()
        for missing in (False, True):
            case = helpers["make_container_get_or_create_case"](
                helpers["make_container_create_case"](is_async), missing
            )
            assert module["_call_get_or_create"](case).id == "c1"
            case.connection.ReadContainer.assert_not_called()
            case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_container_create_rejects_obsolete_keywords_rust(
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
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), method=method,
                               response_hook=hook, **{option: value})
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


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
def test_container_create_rejects_nested_obsolete_options_rust(
    container_create_validation_case, option, key, source, other_source, value
):
    case = container_create_validation_case
    kwargs = {source: {key: value}}
    if other_source is not None:
        kwargs[other_source] = {}
    original = deepcopy(kwargs)
    hook = MagicMock()
    with pytest.raises(TypeError, match=option):
        _call_container_create(
            case,
            "c1",
            PartitionKey(path="/pk"),
            method=case.method,
            response_hook=hook,
            **kwargs,
        )
    assert kwargs == original
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_container_create_rejects_non_callable_hook_before_dispatch_rust(
    container_create_validation_case, hook
):
    case = container_create_validation_case
    with pytest.raises(
        TypeError, match=f"{case.method} response_hook must be callable or None"
    ):
        _call_container_create(
            case, "c1", PartitionKey(path="/pk"), method=case.method, response_hook=hook
        )
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


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
def test_container_create_rejects_async_hook_before_dispatch_rust(
    container_create_validation_case, kind
):
    async def hook(_headers, _properties):
        pytest.fail("An asynchronous response hook must not run")

    class AsyncHook:
        async def __call__(self, _headers, _properties):
            pytest.fail("An asynchronous response hook must not run")

    async def generator_hook(_headers, properties):
        pytest.fail("An asynchronous generator hook must not run")
        yield properties

    callable_hook = AsyncHook()
    hooks = {
        "function": hook,
        "method": callable_hook.__call__,
        "partial": partial(hook),
        "callable": callable_hook,
        "partial-callable": partial(callable_hook),
        "async-generator": generator_hook,
    }
    case = container_create_validation_case
    with pytest.raises(
        TypeError, match=f"{case.method} response_hook must be synchronous"
    ):
        _call_container_create(
            case,
            "c1",
            PartitionKey(path="/pk"),
            method=case.method,
            response_hook=hooks[kind],
        )
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize(
    "invalid_kwargs",
    [
        {"request_options": {"sessionToken": None}},
        {"response_hook": False},
    ],
)
def test_container_create_validates_before_gsi_lookup_rust(
    container_create_case, invalid_kwargs
):
    case = container_create_case
    case.database._resolve_gsi_definition = MagicMock(
        side_effect=AssertionError("unexpected source-container lookup")
    )
    with pytest.raises(TypeError):
        _call_container_create(
            case,
            "c1",
            PartitionKey(path="/pk"),
            global_secondary_index={"sourceContainer": "orders"},
            **invalid_kwargs,
        )
    case.database._resolve_gsi_definition.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("extra_args", [(None,), (None, None), (None, None, False), (None, None, None, 400)])
def test_container_create_optional_settings_are_keyword_only_rust(container_create_case, extra_args):
    """Settings past the container name and partition key must be named, not passed
    by position.

    One, two, three, and four extra positional values are all refused with an
    error that says so. Older code passed indexing policy and time to live
    positionally; silently accepting them now would land a customer's values in
    whichever settings happen to sit in those slots today.
    """
    case = container_create_case
    with pytest.raises(TypeError, match="Unexpected positional parameters"):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), *extra_args)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
def test_container_create_retains_manual_runtime_signature_rust(container_create_case, method):
    """Both create methods really do accept open-ended arguments at runtime.

    They take any positional and any keyword arguments and sort them out
    themselves, which is what lets the tests above produce their exact error
    messages. If someone later replaced that with a normal declared signature,
    Python would raise its own wording instead and the careful messages would
    quietly disappear.
    """
    signature = inspect.signature(getattr(container_create_case.database, method))
    assert list(signature.parameters) == ["args", "kwargs"]
    assert signature.parameters["args"].kind == inspect.Parameter.VAR_POSITIONAL
    assert signature.parameters["kwargs"].kind == inspect.Parameter.VAR_KEYWORD


@pytest.mark.parametrize("proxy_type", [DatabaseProxy, AsyncDatabaseProxy])
def test_container_get_or_create_overloads_match_keyword_only_contract_rust(proxy_type):
    """The published signatures agree with the rules the runtime enforces.

    Because get-or-create accepts open-ended arguments at runtime, the two
    declared forms are what customers actually see in editors and docs. Both
    must show only the container name and partition key as positional, show
    settings as keyword-only, and must not still advertise the retired query
    metrics option. Sync and async are both checked.
    """
    tree = ast.parse(inspect.getsource(proxy_type))
    overloads = [
        node for node in tree.body[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "create_container_if_not_exists"
        and any(isinstance(decorator, ast.Name) and decorator.id == "overload"
                for decorator in node.decorator_list)
    ]
    assert len(overloads) == 2
    for overload in overloads:
        assert not overload.args.posonlyargs
        assert [arg.arg for arg in overload.args.args] == ["self", "id", "partition_key"]
        parameters = [arg.arg for arg in overload.args.kwonlyargs]
        assert "indexing_policy" in parameters
        assert "populate_query_metrics" not in parameters


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
def test_container_create_invalid_argument_binding_fails_before_dispatch_rust(
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


@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_argument_binding_preserves_values_and_optional_kwargs_rust(positional_count):
    """Argument parsing returns the name and partition key and leaves the other
    settings behind untouched.

    The two required values are given by position, by keyword, and split between
    the two; all three yield the same pair. A settings keyword passed alongside
    is still there afterwards, so parsing removes only what it claimed and the
    rest goes on to build the container definition.
    """
    from azure.cosmos._helpers._request_container import parse_container_create_args

    values = ("c1", None)
    kwargs = dict(zip(("id", "partition_key")[positional_count:], values[positional_count:]))
    kwargs["default_ttl"] = 60
    assert parse_container_create_args(values[:positional_count], kwargs) == values
    assert kwargs == {"default_ttl": 60}


def test_container_create_argument_binding_does_not_consume_arguments_on_error_rust():
    """A failed parse leaves the caller's arguments exactly as they were.

    Parsing removes what it recognizes as it goes, so a failure partway through
    could leave the dictionary half emptied. If a caller then retried, or
    inspected what they passed, the name would already be gone.
    """
    from azure.cosmos._helpers._request_container import parse_container_create_args

    kwargs = {"id": "c1", "default_ttl": 60}
    with pytest.raises(TypeError, match="partition_key"):
        parse_container_create_args((), kwargs)
    assert kwargs == {"id": "c1", "default_ttl": 60}


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_preserves_required_arguments_and_return_shapes_rust(
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
    args = ("c1", PartitionKey(path="/pk"))
    kwargs = dict(zip(("id", "partition_key")[positional_count:], args[positional_count:]))
    result = _call_container_create(
        case, *args[:positional_count], **kwargs, return_properties=return_properties,
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
    case.connection.CreateContainer.assert_not_called()
    case.backend.execute.assert_called_once()


@pytest.mark.parametrize("partition_key", [None, PartitionKey(path="/pk"), PartitionKey(path=["/tenant", "/user"])])
def test_container_create_preserves_definition_and_none_semantics_rust(container_create_case, partition_key):
    """Every policy the customer set reaches the request body under its wire name,
    and no partition key means no partition key field at all.

    Nine settings are sent at once -- indexing, time to live, unique keys,
    conflict resolution, analytical storage, computed properties, vector
    embeddings, change feed, and full text -- and each has to arrive renamed
    correctly. One that fails to map leaves the container created with a default
    the customer did not choose, while the call reports success.

    Two of the values are minus one, which is a real setting meaning "keep
    forever", not an absence.

    The partition key is tried three ways: absent, a single path, and a
    hierarchical pair of paths. When it is absent the field is left out entirely
    rather than sent as empty, and when present it is expanded into its wire
    form. The hierarchical case matters because those paths must stay in order.
    """
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


@pytest.fixture
def bodyless_create_case(container_create_case, monkeypatch):
    case = container_create_case
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr("azure.cosmos.database.time", clock, raising=False)
    monkeypatch.setattr("azure.cosmos.aio._database.time", clock, raising=False)
    monkeypatch.setattr("azure.cosmos._operation_deadline.time", clock)
    case.clock = clock
    case.operations = []
    case.read_error = None
    case.expire_during_read = False
    case.creation_response = BackendResponse(201, headers=CaseInsensitiveDict({"x-ms-request-charge": "5"}))
    case.read_response = BackendResponse(
        200,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "2"}),
        body=b'{"id":"c1","_rid":"rid1","partitionKey":{"paths":["/pk"],"kind":"Hash"}}',
    )

    def execute(prepared, *, deadline=None):
        case.operations.append((prepared, deadline))
        if prepared.op == OP_CREATE_CONTAINER:
            clock.now += 2
            return case.creation_response
        assert prepared.op == OP_READ_CONTAINER
        if case.read_error is not None:
            raise case.read_error
        clock.now += 4 if case.expire_during_read else 1
        return case.read_response

    case.backend.execute.side_effect = execute
    return case


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("budget", ["unset", "call", "client"])
def test_bodyless_create_returns_proxy_and_reads_only_requested_properties_rust(
    bodyless_create_case, return_properties, budget
):
    case = bodyless_create_case
    kwargs = {"timeout": 5} if budget == "call" else {}
    if budget == "client":
        case.client_context = CosmosClientContext(
            case.backend, defaults=ClientOperationDefaults(operation_timeout_seconds=5)
        )
        case.database._client_context = case.client_context
    hook = MagicMock()
    result = _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        match_condition=MatchConditions.IfMissing,
        return_properties=return_properties,
        response_hook=hook,
        **kwargs,
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy._client_context is case.client_context
    assert [request.op for request, _ in case.operations] == (
        [OP_CREATE_CONTAINER, OP_READ_CONTAINER] if return_properties else [OP_CREATE_CONTAINER]
    )
    assert all(deadline == (None if budget == "unset" else 105.0) for _, deadline in case.operations)
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}
    assert hook.call_args.args[0]["x-ms-request-charge"] == "5"
    if return_properties:
        properties = result[1]
        assert isinstance(properties, CosmosDict)
        assert properties["id"] == "c1"
        assert properties["partitionKey"]["paths"] == ["/pk"]
        assert properties.get_response_headers()["x-ms-request-charge"] == "2"
        headers = wire_headers(case.operations[1][0])
        assert "if-none-match" not in headers
        assert "if-match" not in headers
        case.connection._set_container_properties_cache.assert_called_once()
    else:
        case.connection._set_container_properties_cache.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("option_source", ["kwargs", "request_options", "feed_options"])
@pytest.mark.parametrize("autoscale", [False, True])
def test_bodyless_create_readback_preserves_settings_rust(
    bodyless_create_case, option_source, autoscale
):
    case = bodyless_create_case
    headers = {"x-alpha-trace": "create-flow"}
    if option_source == "kwargs":
        supplied = {
            "excluded_locations": ["West US"],
            "priority": "Low",
            "throughput_bucket": 7,
            "initial_headers": headers,
            "no_response": True,
            "match_condition": MatchConditions.IfMissing,
        }
    else:
        supplied = {
            option_source: {
                "excludedLocations": ["West US"],
                "priorityLevel": "Low",
                "throughputBucket": 7,
                "initialHeaders": headers,
                "responsePayloadOnWriteDisabled": True,
                "accessCondition": {"type": "IfNoneMatch", "condition": "*"},
            }
        }
    original = deepcopy(supplied)
    hook = MagicMock()
    proxy, properties = _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        return_properties=True,
        timeout=5,
        offer_throughput=(
            ThroughputProperties(auto_scale_max_throughput=4000) if autoscale else 400
        ),
        response_hook=hook,
        **supplied,
    )
    assert proxy.id == properties["id"] == "c1"
    assert supplied == original
    assert [request.op for request, _ in case.operations] == [
        OP_CREATE_CONTAINER,
        OP_READ_CONTAINER,
    ]
    assert [deadline for _, deadline in case.operations] == [105.0, 105.0]
    create, read = [request for request, _ in case.operations]
    for request in (create, read):
        assert request.settings.excluded_locations == ("West US",)
        assert request.settings.priority == "Low"
        assert request.settings.throughput_bucket == 7
        assert wire_headers(request)["x-alpha-trace"] == "create-flow"
    assert create.settings.no_response is True
    assert read.settings.no_response is None
    assert wire_headers(create)["if-none-match"] == "*"
    assert "if-none-match" not in wire_headers(read)
    throughput_header = (
        "x-ms-cosmos-offer-autopilot-settings" if autoscale else "x-ms-offer-throughput"
    )
    assert throughput_header in wire_headers(create)
    assert throughput_header not in wire_headers(read)
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("header_source", ["initial_headers", "request_options"])
def test_bodyless_create_readback_preserves_custom_headers_only_rust(
    bodyless_create_case, header_source
):
    case = bodyless_create_case
    headers = {
        "If-Match": '"old"',
        "IF-NONE-MATCH": "*",
        "X-MS-OFFER-THROUGHPUT": "400",
        "X-MS-COSMOS-OFFER-AUTOPILOT-SETTINGS": '{"maxThroughput":4000}',
        "X-MS-OFFER-TYPE": "S3",
        "X-MS-OFFER-IS-RU-PER-MINUTE-THROUGHPUT-ENABLED": "true",
        "x-ms-alpha-trace": "create-flow",
    }
    original = dict(headers)
    _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        return_properties=True,
        **{header_source: headers},
    )
    assert headers == original
    create, read = [request for request, _ in case.operations]
    assert wire_headers(read)["x-ms-alpha-trace"] == "create-flow"
    for name in headers:
        assert name.lower() in wire_headers(create)
        if name != "x-ms-alpha-trace":
            assert name.lower() not in wire_headers(read)


@pytest.mark.parametrize("failure", ["not_found", "cancelled", "expired_before_read", "expired_during_read"])
def test_bodyless_create_read_failure_never_replays_creation_rust(bodyless_create_case, failure):
    case = bodyless_create_case
    if failure == "not_found":
        case.read_error = CosmosResourceNotFoundError(status_code=404)
    elif failure == "cancelled":
        case.read_error = asyncio.CancelledError()
    elif failure == "expired_during_read":
        case.expire_during_read = True

    def hook(_headers, _body):
        if failure == "expired_before_read":
            case.clock.now = 105.0

    error_type = type(case.read_error) if case.read_error is not None else CosmosClientTimeoutError
    with pytest.raises(error_type) as raised:
        _call_container_create(
            case,
            "c1",
            PartitionKey("/pk"),
            match_condition=MatchConditions.IfMissing,
            return_properties=True,
            response_hook=hook,
            timeout=5,
        )
    if case.read_error is not None:
        assert raised.value is case.read_error
    assert [request.op for request, _ in case.operations] == (
        [OP_CREATE_CONTAINER] if failure == "expired_before_read" else [OP_CREATE_CONTAINER, OP_READ_CONTAINER]
    )
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("return_properties", [False, True])
def test_container_create_does_not_hide_nonempty_response_missing_id_rust(bodyless_create_case, return_properties):
    case = bodyless_create_case
    case.creation_response = BackendResponse(201, body=b'{"_rid":"rid1"}')
    with pytest.raises(KeyError, match="id"):
        _call_container_create(case, "c1", PartitionKey("/pk"), return_properties=return_properties)
    assert len(case.operations) == 1


@pytest.mark.parametrize("return_properties", [False, True])
def test_container_create_does_not_treat_304_as_creation_success_rust(bodyless_create_case, return_properties):
    case = bodyless_create_case
    case.creation_response = BackendResponse(304)
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_container_create(case, "c1", PartitionKey("/pk"), return_properties=return_properties, response_hook=hook)
    assert raised.value.status_code == 304
    assert len(case.operations) == 1
    hook.assert_not_called()


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10])
@pytest.mark.parametrize("autoscale", [False, True])
def test_container_create_preserves_throughput_headers_and_deadlines_rust(container_create_case, timeout, autoscale):
    """Throughput, the customer's own header, the bucket, and the deadline all reach
    the request.

    Throughput is set both ways: a fixed amount, which becomes a plain header,
    and an autoscale maximum, which becomes a small settings block. Sending
    the wrong one leaves the container on the wrong billing model, which the
    customer only discovers on their bill.

    The request also proves the shape of a container create: the operation is a
    create, and the *database* name rides in the item field, because the
    container has no name on the service yet and the request is scoped to the
    database it will live in.
    """
    case = container_create_case
    throughput = ThroughputProperties(auto_scale_max_throughput=4000) if autoscale else 400
    _call_container_create(
        case, "c1", PartitionKey(path="/pk"), offer_throughput=throughput, timeout=timeout,
        initial_headers={"x-my-app": "provisioner"}, throughput_bucket=7,
    )
    prepared = case.backend.prepared
    assert prepared.op == OP_CREATE_CONTAINER
    assert prepared.item_id == "db1"
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-my-app": "provisioner"}).items())
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert settings_options(prepared).get("timeout_seconds") == timeout
    if autoscale:
        assert json.loads(wire_headers(prepared)["x-ms-cosmos-offer-autopilot-settings"]) == {"maxThroughput": 4000}
    else:
        assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'
    case.connection.CreateContainer.assert_not_called()


@pytest.fixture
def container_create_gsi_case(container_create_case, monkeypatch):
    """Advance a controlled clock during the source lookup, without network or sleeps."""
    case = container_create_case
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr("azure.cosmos.database.time", clock, raising=False)
    monkeypatch.setattr("azure.cosmos.aio._database.time", clock, raising=False)
    monkeypatch.setattr("azure.cosmos._operation_deadline.time", clock)

    def read(**_kwargs):
        clock.now += 1.0
        return {"_rid": "source-rid"}

    mock_type = (
        AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    )
    case.source = SimpleNamespace(read=mock_type(side_effect=read))
    case.database.get_container_client = MagicMock(return_value=case.source)
    return case


@pytest.mark.parametrize(
    "timeout_source", ["call", "client", "override", "inherited", "unset"]
)
def test_container_create_gsi_shares_deadline_rust(
    container_create_gsi_case, timeout_source
):
    """Source lookup and creation use the same budget, including defaults and outer deadlines."""
    case = container_create_gsi_case
    kwargs = {}
    expected_deadline = 105.0
    if timeout_source in ("client", "override"):
        case.client_context = CosmosClientContext(
            case.backend,
            defaults=ClientOperationDefaults(operation_timeout_seconds=5),
        )
        case.database._client_context = case.client_context
    if timeout_source == "call":
        kwargs["timeout"] = 5
    elif timeout_source == "override":
        kwargs["timeout"] = 3
        expected_deadline = 103.0
    elif timeout_source == "inherited":
        kwargs.update(timeout=10, _item_operation_deadline=104.0)
        expected_deadline = 104.0
    elif timeout_source == "unset":
        expected_deadline = None

    result = _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        global_secondary_index={"sourceCollectionId": "orders"},
        **kwargs,
    )

    assert result.id == "c1"
    expected_lookup_kwargs = (
        {}
        if expected_deadline is None
        else {"_item_operation_deadline": expected_deadline}
    )
    case.source.read.assert_called_once_with(**expected_lookup_kwargs)
    assert case.backend.execute.call_args.kwargs["deadline"] == expected_deadline
    body = json.loads(case.backend.prepared.body_bytes)
    assert body["globalSecondaryIndexDefinition"]["sourceCollectionRid"] == "source-rid"
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("already_expired", [False, True])
def test_container_create_gsi_expired_budget_prevents_creation_rust(
    container_create_gsi_case, already_expired
):
    """An exhausted lookup budget cannot start creation or invoke its success hook."""
    case = container_create_gsi_case
    kwargs = {"timeout": 1}
    if already_expired:
        kwargs["_item_operation_deadline"] = 99.0
    hook = MagicMock()

    with pytest.raises(CosmosClientTimeoutError):
        _call_container_create(
            case,
            "c1",
            PartitionKey("/pk"),
            response_hook=hook,
            global_secondary_index={"sourceCollectionId": "orders"},
            **kwargs,
        )

    assert case.source.read.call_count == int(not already_expired)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("timeout", [0.5, float("nan")])
def test_container_create_gsi_invalid_timeout_prevents_lookup_rust(
    container_create_gsi_case, timeout
):
    """Reject an invalid operation budget before looking up the GSI source."""
    case = container_create_gsi_case
    with pytest.raises(ValueError, match="timeout"):
        _call_container_create(
            case,
            "c1",
            PartitionKey("/pk"),
            timeout=timeout,
            global_secondary_index={"sourceCollectionId": "orders"},
        )
    case.source.read.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("source_missing", [False, True])
@pytest.mark.parametrize(
    "kwargs",
    [
        {"connection_timeout": 1},
        {"connection_timeout": None},
        {"unknown_option": True},
        {"initial_headers": {"User-Agent": "custom"}},
        {"request_options": {"connection_timeout": 1}},
        {"feed_options": {"unknown_option": True}},
        {"request_options": {"timeout": 10}},
    ],
)
def test_container_create_gsi_rejects_options_before_lookup_rust(container_create_gsi_case, kwargs, source_missing):
    case = container_create_gsi_case
    kwargs = deepcopy(kwargs)
    if source_missing:
        case.source.read.side_effect = CosmosResourceNotFoundError(status_code=404)
    original = deepcopy(kwargs)
    hook = MagicMock()
    with pytest.raises(TypeError):
        _call_container_create(
            case,
            "c1",
            PartitionKey("/pk"),
            response_hook=hook,
            global_secondary_index={"sourceCollectionId": "orders"},
            **kwargs,
        )
    assert kwargs == original
    case.source.read.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("option_source", ["request_options", "feed_options"])
def test_container_create_gsi_preserves_prepared_options_rust(container_create_gsi_case, option_source):
    case = container_create_gsi_case
    options = {"initialHeaders": {"x-my-app": "provisioner"}}
    original = deepcopy(options)
    definition = {"sourceCollectionId": "orders"}
    result = _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        global_secondary_index=definition,
        offer_throughput=400,
        excluded_locations=iter(["West US"]),
        **{option_source: options},
    )
    assert result.id == "c1"
    assert options == original
    assert definition == {"sourceCollectionId": "orders"}
    case.source.read.assert_called_once_with()
    case.backend.execute.assert_called_once()
    prepared = case.backend.prepared
    assert prepared.settings.excluded_locations == ("West US",)
    assert wire_headers(prepared)["x-ms-offer-throughput"] == "400"
    assert wire_headers(prepared)["x-my-app"] == "provisioner"
    body = json.loads(prepared.body_bytes)
    expected = {"sourceCollectionId": "orders", "sourceCollectionRid": "source-rid"}
    assert body["globalSecondaryIndexDefinition"] == expected
    assert body["materializedViewDefinition"] == expected
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout": False}, {"timeout": True}, {"timeout": 0}, {"timeout": -1}, {"timeout": 0.5},
        {"timeout": "10"}, {"timeout": float("nan")}, {"timeout": float("inf")},
        {"timeout": 2**64 - 1}, {"timeout": 10**400}, {"connection_timeout": 1},
        {"unknown_option": True}, {"initial_headers": {"User-Agent": "custom"}},
        {"initial_headers": {"X-MS-VERSION": "custom"}}, {"initial_headers": {"Accept": "custom"}},
        {"initial_headers": {"Cache-Control": "custom"}}, {"request_options": {"timeout": 10}},
        {"request_options": {Constants.ContainerRID: "unexpected"}},
    ],
)
def test_container_create_unsupported_calls_never_fall_back_rust(container_create_case, kwargs):
    """Options the Rust path cannot honor stop the create instead of quietly moving
    it to the legacy transport.

    Twenty calls are covered: ten unusable deadlines, a connect timeout, both raw
    hooks, an unknown keyword, four driver-owned headers, and two raw
    request-options dictionaries.

    Unsupported arguments raise ``TypeError``,
    except bad ``timeout`` values, which raise ``ValueError`` because they are
    wrong values rather than something Rust cannot do.
    Nothing is created on either route, the hook does not run, and the fallback
    counter does not move -- a refusal is not a fallback, and counting it as one
    would make the metric useless for judging how much traffic the Rust engine
    actually turns away.
    """
    case = container_create_case
    hook = MagicMock()
    error, message = (
        (ValueError, "timeout must be") if "timeout" in kwargs
        else (TypeError, "create_container.*legacy Python")
    )
    with pytest.raises(error, match=message):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), response_hook=hook, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("operation", ["create_container", "read_container"])
@pytest.mark.parametrize("failure", ["missing_module", "missing_export", "null_export", "non_callable_export"])
def test_container_create_binding_installation_errors_never_fall_back_rust(
    container_create_case, monkeypatch, operation, failure,
):
    """Creation and its GSI lookup report broken bindings before driver acquisition."""
    case = container_create_case
    asynchronous = isinstance(case.database, AsyncDatabaseProxy)
    module = importlib.import_module(
        "azure.cosmos.aio._backend.binding_adapter" if asynchronous else "azure.cosmos._backend.binding_adapter"
    )
    adapter_type = module.AsyncBindingAdapter if asynchronous else module.BindingAdapter
    adapter = adapter_type("https://unused.invalid", master_key="key")
    acquire = AsyncMock() if asynchronous else MagicMock()
    monkeypatch.setattr(adapter, "_ensure_driver_handle", acquire)
    binding_name = operation + ("_async" if asynchronous else "")
    binding = SimpleNamespace()
    if failure == "null_export":
        setattr(binding, binding_name, None)
    elif failure == "non_callable_export":
        setattr(binding, binding_name, 42)
    monkeypatch.setattr(module, "_rust_module", None if failure == "missing_module" else binding)
    case.connection._backend = adapter
    case.connection.ReadContainer = AsyncMock() if asynchronous else MagicMock()
    case.client_context = CosmosClientContext(adapter)
    case.database._client_context = case.client_context
    hook = MagicMock()
    kwargs = {"global_secondary_index": {"sourceCollectionId": "orders"}} if operation == "read_container" else {}
    error_type = ImportError if failure == "missing_module" else RuntimeError
    message = "compiled" if failure == "missing_module" else binding_name
    try:
        with pytest.raises(error_type, match=message):
            _call_container_create(
                case,
                "c1",
                PartitionKey("/pk"),
                response_hook=hook,
                **kwargs,
            )
        acquire.assert_not_called()
        case.connection.ReadContainer.assert_not_called()
        case.connection.CreateContainer.assert_not_called()
        hook.assert_not_called()
    finally:
        closed = adapter.close()
        if inspect.isawaitable(closed):
            asyncio.run(closed)


def test_container_create_keeps_isolated_hook_headers_and_falsey_callable_rust(
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
    assert calls[0][1] is not properties
    assert calls[0][1] == properties
    assert proxy.id == properties["id"]
    assert properties.get_response_headers()["x-ms-request-charge"] == "5.25"
    assert calls[0][0] is not case.connection.last_response_headers


@pytest.mark.parametrize("outcome", ["create", "existing", "missing"])
@pytest.mark.parametrize("return_properties", [False, True])
def test_container_creation_hook_cannot_mutate_result_or_cached_partition_key_rust(
    container_create_case,
    outcome,
    return_properties,
):
    case = container_create_case
    original = {
        "id": "c1", "_rid": "rid1",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
    }
    properties = CosmosDict(
        json.loads(json.dumps(original)),
        response_headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
    )
    case.connection.CreateContainer.return_value = properties
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    case.connection.ReadContainer = mock_type(return_value=properties)
    response = BackendResponse(
        status_code=201 if outcome != "existing" else 200,
        headers=properties.get_response_headers(), body=json.dumps(original).encode(),
    )
    case.backend.execute.side_effect = [response]
    if outcome == "missing":
        case.connection.ReadContainer.side_effect = CosmosResourceNotFoundError(status_code=404)
        case.backend.execute.side_effect = [
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'), response,
        ]
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
        case, "c1", PartitionKey(path="/pk"),
        method="create_container" if outcome == "create" else "create_container_if_not_exists",
        return_properties=return_properties, response_hook=hook,
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
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    assert case.backend.execute.call_count == (2 if outcome == "missing" else 1)


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
def test_container_create_preserves_conditional_headers_rust(
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
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_container_create(case, "c1", PartitionKey(path="/pk"), **kwargs)
    assert caught == []
    headers = wire_headers(case.backend.prepared)
    case.connection.CreateContainer.assert_not_called()
    assert {
        key.lower(): value for key, value in headers.items()
        if key.lower() in ("if-match", "if-none-match")
    } == {key.lower(): value for key, value in expected.items()}


@pytest.mark.parametrize(
    "kwargs, error_type",
    [
        ({"etag": "v1"}, ValueError), ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"etag": "", "match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"etag": "v1", "match_condition": "invalid"}, TypeError),
    ],
)
def test_container_create_invalid_conditions_fail_before_dispatch_rust(container_create_case, kwargs, error_type):
    """An incomplete or malformed condition stops the create.

    An etag with no condition, a condition with no etag, and an empty etag are
    all ``ValueError``; a condition that is not a real match condition is a
    ``TypeError``. Sending any of them would create unconditionally for a
    customer who believed the call was guarded.
    """
    case = container_create_case
    with pytest.raises(error_type):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("failure_source", ["hook", "backend"])
@pytest.mark.parametrize("error_type", [ValueError, NotImplementedError, ServiceRequestError, asyncio.CancelledError])
def test_container_create_errors_never_replay_rust(container_create_case, failure_source, error_type):
    """A failure, wherever it comes from, is raised as-is after exactly one attempt.

    The error is injected in two places -- the customer's hook, which runs after
    the container exists, and the engine itself -- and in four flavors: an
    ordinary error, a capability failure, a transport failure, and cancellation.

    In all eight combinations the same exception object reaches the caller, the
    engine ran once, and the legacy route was never tried. Retrying would risk
    creating the container twice, and a transport failure is exactly the case
    where the client cannot tell whether the first attempt was applied.

    Cancellation must also pass through unchanged, or it stops unwinding and the
    caller's request to stop is ignored.
    """
    case = container_create_case
    error = error_type("create failed")
    hook = MagicMock(side_effect=error if failure_source == "hook" else None)
    if failure_source == "backend":
        case.backend.execute.side_effect = error
    with pytest.raises(error_type) as raised:
        _call_container_create(case, "c1", PartitionKey(path="/pk"), response_hook=hook)
    assert raised.value is error
    assert hook.call_count == (1 if failure_source == "hook" else 0)
    case.backend.execute.assert_called_once()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("status", [400, 403, 404, 409, 412, 429, 500])
def test_container_create_service_errors_preserve_status_and_never_replay_rust(container_create_case, status):
    """Every failure status from the service keeps its meaning and is not retried
    elsewhere.

    Seven statuses are covered, from bad request through conflict and
    precondition-failed to server error. Each keeps its status code, and the two
    that customers routinely catch by type keep their specific types: conflict
    becomes already-exists, which is how "the container is already there" is
    normally handled, and not-found stays not-found.

    The hook does not run, since nothing succeeded, and the legacy route is not
    tried, so a conflict is not turned into a second create attempt.
    """
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


def test_container_get_or_create_still_creates_after_404_rust(container_create_case):
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
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    case.connection.ReadContainer = mock_type(side_effect=missing)
    case.backend.execute.side_effect = [
        BackendResponse(
            status_code=404,
            headers=CaseInsensitiveDict(),
            body=b'{"message":"missing"}',
        ),
        _created_container_response(),
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = _call_container_create(
            case, "c1", PartitionKey(path="/pk"), method="create_container_if_not_exists",
        )
    assert result.id == "c1"
    assert case.backend.execute.call_count == 2
    assert case.backend.execute.call_args.args[0].op == OP_CREATE_CONTAINER
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_get_or_create_preserves_shapes_and_existing_settings_rust(
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
    args = ("c1", PartitionKey(path="/pk"))
    kwargs = dict(zip(("id", "partition_key")[positional_count:], args[positional_count:]))
    hook = MagicMock()
    result = _call_container_create(
        case, *args[:positional_count], **kwargs, method="create_container_if_not_exists",
        default_ttl=99, offer_throughput=400, return_properties=return_properties,
        response_hook=hook, timeout=10,
        initial_headers={"x-company-trace": "setup"},
    )
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1"
    assert proxy._client_context is case.client_context
    assert proxy.container_link == "dbs/db1/colls/c1"
    hook.assert_called_once()
    properties = hook.call_args.args[1]
    assert hook.call_args.args[0]["x-ms-request-charge"] == ("5.25" if case.missing else "2")
    if return_properties:
        assert result[1] is not properties
        assert result[1] == properties
        assert isinstance(properties, CosmosDict)
    if not case.missing:
        assert properties["partitionKey"]["paths"] == ["/original"]
        assert properties["defaultTtl"] == 10
    case.connection._set_container_properties_cache.assert_called_once()
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    operations = [call.args[0] for call in case.backend.execute.call_args_list]
    assert [op.op for op in operations] == (
        [OP_READ_CONTAINER, OP_CREATE_CONTAINER]
        if case.missing
        else [OP_READ_CONTAINER]
    )
    for op in operations:
        assert settings_options(op)["timeout_seconds"] == 10
        assert op.headers["x-company-trace"] == "setup"
    deadlines = [
        call.kwargs["deadline"] for call in case.backend.execute.call_args_list
    ]
    assert deadlines[0] is not None
    assert all(deadline == deadlines[0] for deadline in deadlines)
    assert operations[0].settings.resource.offer_throughput is None
    if case.missing:
        assert json.loads(operations[1].body_bytes)["defaultTtl"] == 99
        assert operations[1].settings.resource.offer_throughput == 400


@pytest.mark.parametrize("source", ["request_options", "feed_options"])
@pytest.mark.parametrize("override", ["absent", "none", "empty", "value"])
def test_container_get_or_create_preserves_nested_headers_rust(
    container_get_or_create_case, monkeypatch, source, override
):
    case = container_get_or_create_case
    nested = {"x-company-trace": "nested", "x-ms-cosmos-priority-level": "Low"}
    kwargs = {source: {"initialHeaders": nested}}
    expected = nested
    if override != "absent":
        top_level = {
            "none": None,
            "empty": {},
            "value": {"x-company-trace": "override"},
        }[override]
        kwargs["initial_headers"] = top_level
        if top_level is not None:
            expected = top_level
    original = deepcopy(kwargs)
    preflight = MagicMock(wraps=is_create_container_rust_eligible)
    monkeypatch.setattr(
        "azure.cosmos._helpers._request_container.is_create_container_rust_eligible",
        preflight,
    )
    assert _call_get_or_create(case, **kwargs).id == "c1"
    assert kwargs == original
    preflight.assert_called_once()
    assert preflight.call_args.args[0]["initialHeaders"] == expected
    operations = [call.args[0] for call in case.backend.execute.call_args_list]
    assert [op.op for op in operations] == (
        [OP_READ_CONTAINER, OP_CREATE_CONTAINER]
        if case.missing
        else [OP_READ_CONTAINER]
    )
    for operation in operations:
        headers = wire_headers(operation)
        for name in nested:
            assert headers.get(name) == expected.get(name)
    case.connection.CreateContainer.assert_not_called()


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
        {
            "retry_write": None,
            "feed_options": {},
            "request_options": {"retry_write": 2},
        },
    ],
)
def test_container_get_or_create_rejects_retry_write_before_read_rust(
    container_get_or_create_case, kwargs
):
    case = container_get_or_create_case
    original = deepcopy(kwargs)
    hook = MagicMock()
    case.database._resolve_gsi_definition = MagicMock(
        side_effect=AssertionError("unexpected source-container lookup")
    )
    with pytest.raises(
        TypeError, match="create_container_if_not_exists.*retry_write.*Rust driver"
    ):
        _call_get_or_create(
            case,
            response_hook=hook,
            global_secondary_index={"sourceContainer": "source"},
            **kwargs,
        )
    assert kwargs == original
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    case.database._resolve_gsi_definition.assert_not_called()
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
def test_container_get_or_create_allows_default_write_retries_rust(
    container_get_or_create_case, kwargs
):
    case = container_get_or_create_case
    original = deepcopy(kwargs)
    assert _call_get_or_create(case, **kwargs).id == "c1"
    assert kwargs == original
    operations = [call.args[0] for call in case.backend.execute.call_args_list]
    assert [op.op for op in operations] == (
        [OP_READ_CONTAINER, OP_CREATE_CONTAINER]
        if case.missing
        else [OP_READ_CONTAINER]
    )
    for operation in operations:
        assert "retry_write" not in settings_options(operation)
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": float("nan")}, {"timeout": float("inf")},
    {"timeout": 2**64}, {"timeout": "10"}, {"connection_timeout": 1},
    {"initial_headers": {"User-Agent": "override"}}, {"unknown_option": None},
    {"populate_quota_info": True}, {"populate_partition_key_range_statistics": False},
    {"request_options": {Constants.ContainerRID: "rid1"}},
])
def test_container_get_or_create_preflights_both_steps_rust(container_get_or_create_case, kwargs):
    """An option the Rust path cannot honor is caught before the first request, not
    between the two.

    Get-or-create can make two requests, so an option that only the create step
    would choke on has to be spotted up front. Otherwise the read goes out, the
    call then fails, and the customer has paid for a request that achieved
    nothing.

    Unsupported options raise ``TypeError`` naming the method; bad ``timeout``
    values raise ``ValueError`` instead. Neither path sends a request, writes
    the cache, or invokes the hook.
    """
    case = container_get_or_create_case
    hook = MagicMock()
    error, message = (
        (ValueError, "timeout must be") if "timeout" in kwargs
        else (TypeError, "create_container_if_not_exists")
    )
    with pytest.raises(error, match=message):
        _call_get_or_create(case, response_hook=hook, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": "invalid"}, TypeError),
    ],
)
def test_container_get_or_create_validates_conditions_before_read_rust(
    container_get_or_create_case, kwargs, error
):
    """A malformed condition is rejected before the read, not after it.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. All three
    are caught before anything goes out, so a call that was never going to work
    does not cost a request or leave the cache holding properties from it.
    """
    case = container_get_or_create_case
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
def test_container_get_or_create_forwards_conditions_without_ignored_warnings_rust(
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
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_get_or_create(case, **kwargs)
    assert not caught
    for call in case.backend.execute.call_args_list:
        assert (
            CaseInsensitiveDict(wire_headers(call.args[0]))[expected[0]] == expected[1]
        )
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [
        CosmosResourceNotFoundError(status_code=404, message="callback failure"),
        CosmosResourceExistsError(status_code=409, message="callback failure"),
        ValueError("callback failure"),
        NotImplementedError("callback failure"),
    ],
)
def test_container_get_or_create_does_not_interpret_hook_errors_as_missing_rust(
    container_get_or_create_case, error
):
    """A not-found raised by the customer's own hook is not mistaken for the
    container being absent.

    This is the trap unique to this method. Get-or-create decides what to do next
    by catching not-found from the read. The hook runs afterwards, in customer
    code, and if it happens to raise the same error type, code that catches too
    broadly would read it as "the container is missing" and create one.

    Each callback exception reaches the caller unchanged, the hook ran once, and no extra
    request was made beyond what the found-or-missing path already required. The
    cache is not written, since the call did not succeed.
    """
    case = container_get_or_create_case
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _call_get_or_create(case, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    case.connection._set_container_properties_cache.assert_not_called()
    assert case.backend.execute.call_count == (2 if case.missing else 1)
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


def test_container_get_or_create_falsey_hook_has_isolated_headers_rust(container_get_or_create_case):
    """A hook that reports itself as false still runs, and cannot reach back into the
    result.

    The hook is handed headers that are not the ones attached to the properties,
    so editing them changes nothing the caller sees. It also replaces the
    client's record of the last response headers outright, imitating another
    request landing on the same client while this one is still finishing.

    Afterwards the properties still carry the request charge from this call --
    whichever of the two paths ran -- rather than a charge belonging to someone
    else's request.
    """
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


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("read_status", [200, 403, 404, 409])
def test_container_get_or_create_recovers_create_conflict_once_rust(
    container_create_case,
    return_properties,
    read_status,
):
    case = container_create_case
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    winner = CosmosDict(
        {"id": "c1", "_rid": "winner", "partitionKey": {"paths": ["/original"]}, "defaultTtl": 10},
        response_headers=CaseInsensitiveDict({"x-ms-activity-id": "winning-read"}),
    )
    missing = CosmosResourceNotFoundError(status_code=404, message="missing")
    conflict = CosmosResourceExistsError(status_code=409, message="created concurrently")
    error_type = {
        403: CosmosHttpResponseError, 404: CosmosResourceNotFoundError, 409: CosmosResourceExistsError,
    }.get(read_status)
    case.backend.execute.side_effect = [
        BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'),
        BackendResponse(
            status_code=409, headers={}, body=b'{"message":"created concurrently"}'
        ),
        BackendResponse(
            status_code=read_status,
            headers=winner.get_response_headers(),
            body=json.dumps(
                winner if error_type is None else {"message": "reread"}
            ).encode(),
        ),
    ]
    seen = []

    def hook(headers, properties):
        assert headers["X-MS-ACTIVITY-ID"] == "winning-read"
        assert properties == winner
        properties["partitionKey"]["paths"].append("/hook-edit")
        seen.append(headers)

    options = dict(
        return_properties=return_properties, response_hook=hook, timeout=10,
        offer_throughput=400, default_ttl=99,
        initial_headers={"x-company-trace": "setup"},
        etag='"v1"', match_condition=MatchConditions.IfNotModified,
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
    operations = [call.args[0] for call in case.backend.execute.call_args_list]
    assert [op.op for op in operations] == [
        OP_READ_CONTAINER,
        OP_CREATE_CONTAINER,
        OP_READ_CONTAINER,
    ]
    assert operations[2] == operations[0]
    deadlines = [
        call.kwargs["deadline"] for call in case.backend.execute.call_args_list
    ]
    assert deadlines[0] is not None and deadlines == [deadlines[0]] * 3
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize(
    "missing,status",
    [
        pytest.param(False, 401, id="read-401"),
        pytest.param(False, 403, id="read-403"),
        pytest.param(False, 409, id="read-409"),
        pytest.param(False, 429, id="read-429"),
        pytest.param(False, 500, id="read-500"),
        pytest.param(True, 401, id="create-401"),
        pytest.param(True, 403, id="create-403"),
        pytest.param(True, 404, id="create-404"),
        pytest.param(True, 409, id="create-409"),
        pytest.param(True, 429, id="create-429"),
        pytest.param(True, 500, id="create-500"),
    ],
)
def test_container_get_or_create_propagates_failures_without_replay_rust(
    container_create_case, missing, status
):
    """A failure at either step reaches the caller with its status intact and is not
    retried.

    Five failure statuses are covered on the initial read and six on creation
    after a not-found read, including a creation-stage 404.

    An initial 404 is not a failure -- it is the signal to create, covered by
    its own test rather than included in this failure matrix.

    A create conflict permits one follow-up read. If that read also fails, its
    error propagates without another create. The hook does not run and nothing
    is cached.
    """
    case = make_container_get_or_create_case(container_create_case, missing)
    error_type = (
        CosmosResourceExistsError
        if status == 409
        else (CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError)
    )
    error = error_type(status_code=status, message="failure")
    replies = []
    if case.missing:
        replies.append(
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}')
        )
    replies.append(
        BackendResponse(status_code=status, headers={}, body=b'{"message":"failure"}')
    )
    if case.missing and status == 409:
        replies.append(
            BackendResponse(status_code=409, headers={}, body=b'{"message":"reread"}')
        )
    case.backend.execute.side_effect = replies
    hook = MagicMock()
    with pytest.raises(error_type) as raised:
        _call_get_or_create(case, response_hook=hook)
    assert raised.value.status_code == status
    hook.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    assert case.backend.execute.call_count == (
        1 + int(case.missing) + int(case.missing and status == 409)
    )
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


def test_concurrent_container_get_or_create_returns_winner_rust(container_create_case):
    case = container_create_case
    asynchronous = isinstance(case.database, AsyncDatabaseProxy)
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
            status_code=status, headers={"x-ms-activity-id": operation},
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
            return reply

        async def run():
            reply = await execute_async(operation)
            return reply
        return run()

    async def binding_execute(prepared, **_kwargs):
        return await dispatch(prepared.op)

    case.backend.execute.side_effect = (
        binding_execute
        if asynchronous
        else lambda prepared, **_k: dispatch(prepared.op)
    )
    hook = MagicMock()

    async def run_all():
        return await asyncio.gather(*[
            case.database.create_container_if_not_exists("c1", PartitionKey(path="/pk"), response_hook=hook)
            for _ in range(8)
        ])

    if asynchronous:
        results = asyncio.run(run_all())
    else:
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: _call_get_or_create(case, response_hook=hook), range(8)))
    assert [result.id for result in results] == ["c1"] * 8
    assert hook.call_count == 8
    assert case.connection._set_container_properties_cache.call_count == 8
    assert reads == 15
    assert case.backend.execute.call_count == 23
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("error", [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()])
def test_container_get_or_create_binding_errors_never_fall_back_rust(container_get_or_create_case, error):
    """A failure inside the Rust engine is raised as-is and never restarted on legacy.

    The error is injected at whichever step comes last, so it lands on the read
    when the container exists and on the create when it does not. All three
    kinds -- an ordinary error, a capability failure, and cancellation -- reach
    the caller unchanged.

    Restarting the whole call on legacy would be worse here than elsewhere: the
    create may already have been applied, so the second attempt could come back
    reporting a conflict for a container the customer had just successfully
    created.
    """
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


@pytest.mark.parametrize(
    "header_source", ["initial_headers", "request_options", "feed_options"]
)
def test_container_get_or_create_distinguishes_bodyless_read_and_create_rust(
    container_get_or_create_case,
    header_source,
):
    """Keep 304 reads empty; read back requested properties after a bodyless create.

    The hook still observes the original response, not the additional properties read.
    """
    case = container_get_or_create_case
    empty = CosmosDict({}, response_headers=CaseInsensitiveDict({"etag": '"v1"'}))
    replies = []
    if case.missing:
        replies.append(
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}')
        )
    replies.append(
        BackendResponse(
            status_code=201 if case.missing else 304,
            headers=empty.get_response_headers(),
            body=b"",
        )
    )
    if case.missing:
        replies.append(
            BackendResponse(
                status_code=200,
                headers=case.existing_properties.get_response_headers(),
                body=json.dumps(case.existing_properties).encode(),
            )
        )
    case.backend.execute.side_effect = replies
    hook = MagicMock()
    kwargs = dict(
        match_condition=MatchConditions.IfMissing,
        return_properties=True,
        response_hook=hook,
    )
    headers = {"x-company-trace": "setup"}
    kwargs[header_source] = (
        headers if header_source == "initial_headers" else {"initialHeaders": headers}
    )
    proxy, properties = _call_get_or_create(case, **kwargs)
    assert proxy.id == "c1"
    for call in case.backend.execute.call_args_list:
        assert wire_headers(call.args[0])["x-company-trace"] == "setup"
    if case.missing:
        assert properties == case.existing_properties
        assert [call.args[0].op for call in case.backend.execute.call_args_list] == [
            OP_READ_CONTAINER,
            OP_CREATE_CONTAINER,
            OP_READ_CONTAINER,
        ]
        assert "if-none-match" not in wire_headers(
            case.backend.execute.call_args.args[0]
        )
    else:
        assert properties == {}
        case.connection.CreateContainer.assert_not_called()
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}


def test_container_get_or_create_preflight_does_not_mutate_caller_options_rust():
    """Preparing the read reports eligibility and builds the read options without
    touching what the caller passed.

    This runs before the request, and the same arguments are needed again for the
    create step that may follow, so consuming or editing them would leave the
    second step working from a changed set.

    The caller's arguments are unchanged afterwards, including the nested headers
    dictionary. The read options carry the condition, correctly translated to its
    wildcard form. Throughput is left out, because provisioning belongs to the
    create and not to merely looking. What remains is only the deadline, which is
    handed on to the transport.
    """
    from copy import deepcopy
    from azure.cosmos._helpers._request_container import prepare_container_get_or_create_read

    kwargs = {"request_options": {"initialHeaders": {"x-company-trace": "setup"}},
              "match_condition": MatchConditions.IfMissing, "etag": "unused", "timeout": 10}
    original = deepcopy(kwargs)
    options, remaining, eligible, _deadline = prepare_container_get_or_create_read(
        kwargs, initial_headers=None, offer_throughput=400
    )
    assert eligible
    assert kwargs == original
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "*"}
    assert "offerThroughput" not in options
    assert remaining == {"timeout": 10}


# --- routing registration ------------------------------------------------


def test_create_container_is_a_single_response_operation_rust():
    """One create, one reply: it is sent through ``execute``, not the paged path."""
    assert OP_TO_BINDING_FUNCTION_NAME[OP_CREATE_CONTAINER] == "create_container"
    assert OP_CREATE_CONTAINER not in STATELESS_PAGE_BINDING_FUNCTION_NAMES


def test_container_feeds_are_paged_operations_rust():
    """Both feeds are sent through ``execute_pages``, never the single-reply path."""
    assert STATELESS_PAGE_BINDING_FUNCTION_NAMES[OP_LIST_CONTAINERS] == "list_containers"
    assert STATELESS_PAGE_BINDING_FUNCTION_NAMES[OP_QUERY_CONTAINERS] == "query_containers"
    assert OP_LIST_CONTAINERS not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_QUERY_CONTAINERS not in OP_TO_BINDING_FUNCTION_NAME


# --- create_container request shape --------------------------------------

@pytest.mark.parametrize("operation", ["read_container", "create_container"])
@pytest.mark.parametrize("suffix", ["", "_async"])
@pytest.mark.parametrize("remaining", [None, 0.125, 1.0])
@pytest.mark.parametrize("include_attempts", [False, True])
def test_container_composed_native_rejects_string_handle_rust(operation, suffix, remaining, include_attempts):
    """Reject string handles; Windows-emulator binding tests cover successful calls with real handles."""
    from azure.cosmos import _rust

    prepared = (
        build_read_container_prepared("dbs/db1/colls/c1", {})
        if operation == "read_container"
        else build_create_container_prepared("dbs/db1", {"id": "c1"}, {})
    )
    native = getattr(_rust, operation + suffix)
    assert inspect.signature(native).parameters["timeout_seconds"].default is None
    assert inspect.signature(native).parameters["include_attempts"].default is False
    with pytest.raises(TypeError, match="_DriverHandle"):
        native("unregistered-container-composed-test", prepared,
               timeout_seconds=remaining, include_attempts=include_attempts)


@pytest.mark.parametrize("operation", ["read_container", "create_container"])
@pytest.mark.parametrize("suffix", ["", "_async"])
@pytest.mark.parametrize("remaining", [0, -1, float("inf"), float("nan")])
def test_container_composed_native_checks_handle_before_remaining_timeout_rust(operation, suffix, remaining):
    """Check the handle first; Windows-emulator binding tests reject invalid budgets with real handles."""
    from azure.cosmos import _rust

    prepared = (
        build_read_container_prepared("dbs/db1/colls/c1", {})
        if operation == "read_container"
        else build_create_container_prepared("dbs/db1", {"id": "c1"}, {})
    )
    with pytest.raises(TypeError, match="_DriverHandle"):
        getattr(_rust, operation + suffix)(
            "unregistered-container-composed-test", prepared, timeout_seconds=remaining
        )


def test_create_container_prepared_names_the_database_and_carries_the_definition_rust():
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
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert json.loads(prepared.body_bytes) == definition
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-custom": "value"}).items())
    assert settings_options(prepared)["timeout_seconds"] == 3.5


def test_create_container_prepared_drops_the_session_token_rust():
    """A collection is a master resource, so the legacy path never attaches a
    session token to this request either. Leaving one in would send a token the
    other engine does not send."""
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"sessionToken": "s1", "offerThroughput": 400},
    )

    assert "sessionToken" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'


def test_create_container_prepared_rejects_a_link_with_no_database_rust():
    """A link with the prefix but no name would otherwise create the container in a
    database literally named ``dbs``."""
    with pytest.raises(ValueError):
        build_create_container_prepared("dbs/", {"id": "c1"}, {})


def test_create_container_prepared_drops_a_null_initial_headers_rust():
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

    assert "initialHeaders" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'


def test_list_containers_sends_no_query_body_rust():
    """A read feed has no SQL. The page adapter refuses a feed op that is not on its
    parameterless list, so leaving ``list_containers`` off it makes every
    ``list_containers`` call fail once it reaches the binding."""
    from azure.cosmos._backend.binding_adapter import build_binding_request_from_page

    request = build_binding_request_from_page(
        build_list_containers_page(
            path="dbs/db1/colls",
            options={},
            req_headers={},
        )
    )

    assert request.body_bytes == b""
    assert request.container_link == "dbs/db1"


def test_query_containers_sends_the_query_body_rust():
    """The query payload must arrive as JSON in ``body_bytes``, not as a URL parameter."""
    from azure.cosmos._backend.binding_adapter import build_binding_request_from_page

    request = build_binding_request_from_page(
        build_query_containers_page(
            path="dbs/db1/colls",
            query_payload={"query": "SELECT * FROM c"},
            options={},
            req_headers={},
        )
    )

    assert json.loads(request.body_bytes) == {"query": "SELECT * FROM c"}


# --- create_container eligibility ----------------------------------------


def test_create_container_is_rust_eligible_for_a_plain_create_rust():
    """A create with only standard options must be routed to the Rust backend."""
    assert is_create_container_rust_eligible({"offerThroughput": 400}, {"timeout": 3.5}) is True


def test_create_container_is_not_rust_eligible_with_an_intended_container_rid_rust():
    """``_base.GetHeaders`` emits ``x-ms-cosmos-intended-collection-rid`` for every
    resource type except ``dbs``, which includes this one. The Rust path has no
    equivalent, so running it there would drop a header legacy sends."""
    assert is_create_container_rust_eligible({Constants.ContainerRID: "rid1"}, {}) is False


# --- create_container routing --------------------------------------------


def test_sync_create_container_routes_to_rust_and_fires_the_hook_once_rust():
    """The coordinator runs the create through the backend, returns the created
    container, records the response headers, and fires ``response_hook`` once."""
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _FakeBackend()
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


def test_async_create_container_routes_to_rust():
    """The async coordinator builds the same request as the sync one. It is separate
    code -- the async backend awaits its request builder -- so it can break alone."""
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    backend = _AsyncFakeBackend()

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


def test_list_containers_prepared_carries_the_owning_database_link_rust():
    """``container_link`` holds a database link, not a container link: the feed is
    scoped to a database and this is the only typed field that can carry it."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_page(
        path=path,
        options={"maxItemCount": 10, "continuation": "ct-1"},
        req_headers={},
    )

    assert prepared.op == OP_LIST_CONTAINERS
    assert prepared.container_link == "dbs/db1"
    assert prepared.max_item_count == 10
    assert prepared.continuation == "ct-1"
    assert prepared.query is None


def test_query_containers_prepared_carries_the_query_and_the_database_link_rust():
    """The prepared query must name the owning database and carry the full query string and parameters."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_query_containers_page(
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


def test_container_feed_headers_keep_the_customers_own_headers_rust():
    """A plain header the customer set survives into the nested ``initialHeaders``
    entry the binding forwards verbatim. Left flat it would be dropped by the
    option-key translation on the Rust side."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_page(
        path=path,
        options={"initialHeaders": {"x-custom-tag": "value"}},
        req_headers={"x-custom-tag": "value"},
    )

    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-custom-tag": "value"}).items())


# --- feed eligibility -----------------------------------------------------


def _list_gate(path="dbs/db1/colls", options=None, kwargs=None, resource_type=_COLLECTION):
    """Thin wrapper over ``can_use_rust_list_containers`` so test cases read cleanly."""
    return can_use_rust_list_containers(
        path=path,
        options=options or {},
        kwargs=kwargs or {},
        is_query_plan=False,
        resource_type=resource_type,
    )


def test_list_containers_page_is_rust_eligible_for_a_plain_feed_rust():
    """A feed page with no special options must be eligible for the Rust backend."""
    assert _list_gate() is True


def test_list_containers_page_is_not_eligible_when_the_path_names_no_database_rust():
    """Without a database name the Rust page has nothing to run against, so the call
    belongs on legacy rather than failing."""
    assert _list_gate(path="dbs//colls") is False
    assert _list_gate(path="dbs/db1/docs") is False


def test_list_containers_page_is_not_eligible_for_another_resource_type_rust():
    """The database and item feeds have their own gates and their own binding entry
    points; this one must not claim them."""
    assert _list_gate(resource_type=http_constants.ResourceType.Database) is False


def test_query_containers_page_is_rust_eligible_for_a_dict_query_rust():
    """A dict-form query (``application/query+json``) must be routed to the Rust backend."""
    assert can_use_rust_query_containers(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is True


def test_query_containers_page_is_not_eligible_for_a_string_query_rust():
    """The legacy-only SqlQuery mode posts a bare string as ``text/plain`` while the
    driver always posts ``application/query+json``. Different bytes on the wire, so
    that case stays on legacy."""
    assert can_use_rust_query_containers(
        path="dbs/db1/colls",
        query_payload="SELECT * FROM c",
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is False


def test_query_containers_page_is_not_eligible_for_a_query_plan_rust():
    """A query-plan request must stay on legacy; Rust has no query-plan endpoint for containers."""
    assert can_use_rust_query_containers(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=True,
        resource_type=_COLLECTION,
    ) is False


# --- public method behavior ----------------------------------------------


# --- container read -------------------------------------------------------


def _read_container_response() -> BackendResponse:
    """Return a canned 200 OK reply carrying a container body with a partition key."""
    return BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
        body=b'{"id":"c1","_rid":"rid1","partitionKey":{"paths":["/pk"],"kind":"Hash"}}',
    )


def test_read_container_prepared_carries_both_names_rust():
    """The driver reads a container by name, so the request has to name the database
    and the container. Both come out of the one link the proxy holds."""
    prepared = build_read_container_prepared("dbs/db1/colls/c1", {})

    assert prepared.op == OP_READ_CONTAINER
    assert prepared.container_link == "dbs/db1/colls/c1"


def test_read_container_prepared_accepts_a_link_with_slashes_rust():
    """Leading and trailing slashes in the link must be stripped before the request is built."""
    prepared = build_read_container_prepared("/dbs/db1/colls/c1/", {})

    assert prepared.container_link == "dbs/db1/colls/c1"


@pytest.mark.parametrize(
    "link",
    ["dbs/db1", "dbs/db1/colls", "dbs/db1/colls/", "dbs//colls/c1", "colls/c1"],
)
def test_read_container_prepared_rejects_a_link_missing_either_name_rust(link):
    """A half-formed link would reach the service as a request for a container
    literally named ``colls``, and the not-found that came back would say nothing
    about the real problem."""
    with pytest.raises(ValueError):
        build_read_container_prepared(link, {})


def test_read_container_prepared_drops_the_session_token_rust():
    """A container is a master resource, so neither engine sends a session token on
    this read. Sending one on Rust only would be a difference between the two."""
    prepared = build_read_container_prepared(
        "dbs/db1/colls/c1",
        {"sessionToken": "0:1#22"},
    )

    assert "sessionToken" not in wire_headers(prepared)


def test_read_container_is_rust_eligible_for_a_plain_read_rust():
    """A read with no special options must be eligible for the Rust backend."""
    assert is_read_container_rust_eligible({}, {}) is True


@pytest.mark.parametrize(
    "option",
    ["populatePartitionKeyRangeStatistics", "populateQuotaInfo"],
)
def test_read_container_is_rust_eligible_when_statistics_were_asked_for_rust(option):
    """The binding forwards both metadata flags and preserves their returned data."""
    assert is_read_container_rust_eligible({option: True}, {}) is True


def test_sync_read_container_routes_to_rust_and_fires_the_hook_once_rust():
    """The helper must use Rust, return the container, and fire ``response_hook`` exactly once."""
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _FakeBackend(_read_container_response())
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


def test_async_read_container_routes_to_rust():
    """Async read must use the Rust backend without falling through to the legacy path."""
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    backend = _AsyncFakeBackend(_read_container_response())

    result = asyncio.run(
        AsyncContainerHelper(connection, backend).read_container(
            "dbs/db1/colls/c1",
            {},
        )
    )

    assert result["id"] == "c1"
    assert backend.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()


# --- asynchronous response hooks ------------------------------------------


def test_async_create_container_fires_the_hook_once_on_the_rust_path_rust():
    """The async Rust create calls the customer's response hook exactly once."""
    connection = SimpleNamespace(
        CreateContainer=AsyncMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncFakeBackend()).create_container(
            "dbs/db1",
            {"id": "c1"},
            {},
            response_hook=lambda headers, body: hooks.append((headers, body)),
        )
    )

    assert len(hooks) == 1
    assert hooks[0][1] is not result
    assert hooks[0][1] == result
    assert hooks[0][0] == result.get_response_headers()
    connection.CreateContainer.assert_not_called()


def test_async_read_container_fires_the_hook_once_on_the_rust_path_rust():
    """Async Rust read must fire the customer's response hook exactly once with the real headers."""
    connection = SimpleNamespace(
        ReadContainer=AsyncMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    hooks = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncFakeBackend(_read_container_response())).read_container(
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
