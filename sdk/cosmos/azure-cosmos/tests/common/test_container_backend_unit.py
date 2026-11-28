# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for creating, reading, listing and querying containers.

These tests use fakes and need no Cosmos DB account.

Terms used in this file:

- Container create: a call to ``create_container``.
- Get-or-create: a call to ``create_container_if_not_exists``. It reads the
  container first and creates it only if the read finds nothing.
- Response hook: the optional ``response_hook`` function a caller passes. The
  SDK calls it with the response headers and the result.
- Fake sender: a test object (``case.backend``) that stands in for the part of
  the SDK that sends requests. Its ``execute`` method records calls instead of
  sending them.
- Connection object: the object the client uses to reach the service. Here its
  methods are mocks, so a test can check they were never called.
- Obsolete option: an option that no longer has any effect, such as
  ``session_token`` or ``populate_query_metrics``. Passing one raises ``TypeError``.
- Global secondary index: a container filled from another container, called
  the source container. Creating one first looks up the source container.
- Empty-body create: a create whose response has no body.
- Follow-up read: the container read the SDK sends after an empty-body create
  when the caller passes ``return_properties=True``, to get the settings.
- Deadline: the time by which the whole call must finish. It comes from the
  ``timeout`` keyword or the client's default operation timeout.
- Compiled module: the part of the SDK that sends most requests to the service.
- Connection setup: the step, run once per client, that gets the compiled
  module ready to talk to the service.
- Internal id: the ``_rid`` value the service gives each container.
- Prepared request: the request object (``prepared``) the SDK builds before
  sending a request.
- Handle: the object that connection setup creates. Each compiled-module
  function takes it as its first argument.
- Supported: a request the compiled module can send. Each support check
  returns ``True`` or ``False``.
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
    """Runs each test once with a sync client and once with an async client."""
    return make_container_create_case(request.param == "async")


@pytest.fixture(params=[False, True], ids=["existing", "missing"])
def container_get_or_create_case(container_create_case, request):
    """Runs each test once with an existing container and once with a missing one."""
    return make_container_get_or_create_case(container_create_case, request.param)


@pytest.fixture(params=["create", "existing", "missing"])
def container_create_validation_case(container_create_case, request):
    """Runs each test against container create, get-or-create with an existing
    container, and get-or-create with a missing one.

    It sets ``case.method`` to the method to call.
    """
    case = container_create_case
    case.method = "create_container"
    if request.param != "create":
        case = make_container_get_or_create_case(case, request.param == "missing")
        case.method = "create_container_if_not_exists"
    return case


_COLLECTION = http_constants.ResourceType.Collection


def test_container_tests_do_not_import_old_request_code_rust(monkeypatch):
    """These tests and their helpers still load and run when the older request
    modules cannot be imported.
    """
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
    """``create_container`` and ``create_container_if_not_exists`` reject
    ``session_token`` and ``populate_query_metrics``.

    The option has no effect, so passing it raises ``TypeError`` naming the option,
    for every value including ``None`` and ``False``. No request is sent and the
    response hook is not called.
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
def test_container_create_rejects_obsolete_options_in_option_dicts_rust(
    container_create_validation_case, option, key, source, other_source, value
):
    """The same options are rejected when given inside ``request_options`` or
    ``feed_options`` under their header names ``sessionToken`` and
    ``populateQueryMetrics``.

    This includes passing both dicts with the option in only one of them. The
    caller's dicts are not changed, no request is sent, no container settings are
    cached, and the response hook is not called.
    """
    case = container_create_validation_case
    kwargs = {source: {key: value}}
    if other_source is not None:
        kwargs[other_source] = {}
    kwargs_before = deepcopy(kwargs)
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
    assert kwargs == kwargs_before
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_container_create_rejects_non_callable_hook_before_sending_rust(
    container_create_validation_case, hook
):
    """A ``response_hook`` that is not a function, such as ``False``, ``0``, a
    string or a dict, raises ``TypeError`` before any request is sent.
    """
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
def test_container_create_rejects_async_hook_before_sending_rust(
    container_create_validation_case, kind
):
    """An async response hook raises ``TypeError`` before any request is sent.

    Covered: an async function, an async method, an object with an async
    ``__call__``, both of those wrapped in ``functools.partial``, and an async
    generator function.
    """
    async def async_function_hook(_headers, _properties):
        pytest.fail("An asynchronous response hook must not run")

    class AsyncHook:
        async def __call__(self, _headers, _properties):
            pytest.fail("An asynchronous response hook must not run")

    async def generator_hook(_headers, properties):
        pytest.fail("An asynchronous generator hook must not run")
        yield properties

    async_hook_object = AsyncHook()
    hooks_by_kind = {
        "function": async_function_hook,
        "method": async_hook_object.__call__,
        "partial": partial(async_function_hook),
        "callable": async_hook_object,
        "partial-callable": partial(async_hook_object),
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
            response_hook=hooks_by_kind[kind],
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
def test_container_create_validates_arguments_before_source_container_lookup_rust(
    container_create_case, invalid_kwargs
):
    """When creating a global secondary index, bad arguments are rejected before
    the SDK looks up the source container.

    Covered: an obsolete option and a non-callable response hook.
    """
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
    """Only the container name and partition key may be passed by position.

    One to four extra positional values raise ``TypeError``. Older SDK versions
    accepted settings such as ``indexing_policy`` and ``default_ttl`` by
    position, so callers that still do this get a clear error.
    """
    case = container_create_case
    with pytest.raises(TypeError, match="Unexpected positional parameters"):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), *extra_args)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
def test_container_create_methods_accept_any_arguments_at_runtime_rust(container_create_case, method):
    """Both create methods are declared as ``(*args, **kwargs)`` and check the
    arguments themselves.

    That check produces the error messages tested in this file. With a normal
    signature, Python would raise its own, different messages.
    """
    signature = inspect.signature(getattr(container_create_case.database, method))
    assert list(signature.parameters) == ["args", "kwargs"]
    assert signature.parameters["args"].kind == inspect.Parameter.VAR_POSITIONAL
    assert signature.parameters["kwargs"].kind == inspect.Parameter.VAR_KEYWORD


@pytest.mark.parametrize("proxy_type", [DatabaseProxy, AsyncDatabaseProxy])
def test_container_get_or_create_typed_signatures_match_runtime_rules_rust(proxy_type):
    """The two ``@overload`` signatures of ``create_container_if_not_exists`` match
    what the method accepts at runtime.

    These signatures are what editors show. Only ``id`` and ``partition_key`` are
    positional, other settings such as ``indexing_policy`` are keyword-only, and
    ``populate_query_metrics`` is not listed. Sync and async clients are both
    checked.
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
def test_container_create_invalid_arguments_fail_before_sending_rust(
    container_create_case, method, args, kwargs, message
):
    """Calls with missing, repeated or extra arguments raise ``TypeError`` before
    any request is sent.

    The message names the method called and the problem. Covered: no arguments, a
    missing ``id``, a missing ``partition_key``, ``id`` or ``partition_key`` given
    both by position and by keyword, and a third positional value. The caller's
    keyword arguments are not changed and the response hook is not called.
    """
    case = container_create_case
    hook = MagicMock()
    kwargs_before = dict(kwargs)
    with pytest.raises(TypeError) as raised:
        _call_container_create(case, *args, **kwargs, method=method, response_hook=hook)
    assert "{}()".format(method) in str(raised.value)
    assert message in str(raised.value)
    assert kwargs == kwargs_before
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_argument_parsing_returns_name_and_partition_key_rust(positional_count):
    """``parse_container_create_args`` returns the container name and partition key
    and removes them from the keyword arguments.

    They can be passed both by position, both by keyword, or the name by position
    and the partition key by keyword. Other settings such as ``default_ttl`` are
    left in place.
    """
    from azure.cosmos._helpers._request_container import parse_container_create_args

    expected = ("c1", None)
    kwargs = dict(zip(("id", "partition_key")[positional_count:], expected[positional_count:]))
    kwargs["default_ttl"] = 60
    assert parse_container_create_args(expected[:positional_count], kwargs) == expected
    assert kwargs == {"default_ttl": 60}


def test_container_create_argument_parsing_leaves_arguments_unchanged_on_error_rust():
    """When ``partition_key`` is missing, parsing raises ``TypeError`` and leaves the
    keyword arguments unchanged, because the SDK checks all arguments before
    removing any.
    """
    from azure.cosmos._helpers._request_container import parse_container_create_args

    kwargs = {"id": "c1", "default_ttl": 60}
    with pytest.raises(TypeError, match="partition_key"):
        parse_container_create_args((), kwargs)
    assert kwargs == {"id": "c1", "default_ttl": 60}


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_returns_same_result_however_arguments_are_passed_rust(
    container_create_case, return_properties, positional_count
):
    """A create returns the same result whether the name and partition key are
    passed by position, by keyword or both.

    The returned container client points at ``dbs/db1/colls/c1`` and shares the
    client's settings. With ``return_properties=True`` the call returns the client
    and the container settings, including the request charge header. The container
    settings are cached once.
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
def test_container_create_sends_every_setting_in_request_body_rust(container_create_case, partition_key):
    """All nine container settings reach the request body under their service
    names.

    The settings are indexing policy, default time to live, unique keys, conflict
    resolution, analytical storage time to live, computed properties, vector
    embeddings, change feed and full text. Two of the values are -1, which is a
    valid setting and must be sent. With no partition key the body has no
    ``partitionKey`` field. A single-path key and a two-path (hierarchical) key
    are both sent in full.
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
def empty_body_create_case(container_create_case, monkeypatch):
    """Sets up an empty-body create and a fake clock.

    The clock starts at 100 seconds. The create moves it forward 2 seconds and the
    follow-up read 1 second, or 4 seconds when ``case.expire_during_read`` is set.
    ``case.operations`` records each request with its deadline. Set
    ``case.read_error`` to make the read fail.
    """
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
@pytest.mark.parametrize("timeout_source", ["unset", "call", "client"])
def test_empty_body_create_reads_container_only_when_properties_requested_rust(
    empty_body_create_case, return_properties, timeout_source
):
    """With ``return_properties=False`` only the create is sent. With
    ``return_properties=True`` the SDK also sends a follow-up read and returns its
    settings and request charge.

    Both requests share one deadline, whether it comes from ``timeout``, the client
    default, or is not set. The follow-up read does not send the create's match
    condition. The response hook is called once, with the create's headers and an
    empty body. Container settings are cached only when they were read.
    """
    case = empty_body_create_case
    kwargs = {"timeout": 5} if timeout_source == "call" else {}
    if timeout_source == "client":
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
    assert all(deadline == (None if timeout_source == "unset" else 105.0) for _, deadline in case.operations)
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
def test_empty_body_create_follow_up_read_keeps_read_settings_rust(
    empty_body_create_case, option_source, autoscale
):
    """The follow-up read keeps the read settings from the create call: excluded
    regions, priority, throughput bucket and custom headers.

    It drops the create-only settings: ``no_response``, the match condition and
    the throughput. Covered: settings given as keywords and inside
    ``request_options`` or ``feed_options``, with fixed and autoscale throughput.
    The caller's options are not changed.
    """
    case = empty_body_create_case
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
    supplied_before = deepcopy(supplied)
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
    assert supplied == supplied_before
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
def test_empty_body_create_follow_up_read_keeps_only_custom_headers_rust(
    empty_body_create_case, header_source
):
    """Match headers and throughput headers given in ``initial_headers`` or
    ``request_options`` are sent on the create but not on the follow-up read,
    whatever their letter case.

    A custom header such as ``x-ms-alpha-trace`` is sent on both. The caller's
    headers are not changed.
    """
    case = empty_body_create_case
    headers = {
        "If-Match": '"old"',
        "IF-NONE-MATCH": "*",
        "X-MS-OFFER-THROUGHPUT": "400",
        "X-MS-COSMOS-OFFER-AUTOPILOT-SETTINGS": '{"maxThroughput":4000}',
        "X-MS-OFFER-TYPE": "S3",
        "X-MS-OFFER-IS-RU-PER-MINUTE-THROUGHPUT-ENABLED": "true",
        "x-ms-alpha-trace": "create-flow",
    }
    headers_before = dict(headers)
    _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        return_properties=True,
        **{header_source: headers},
    )
    assert headers == headers_before
    create, read = [request for request, _ in case.operations]
    assert wire_headers(read)["x-ms-alpha-trace"] == "create-flow"
    for name in headers:
        assert name.lower() in wire_headers(create)
        if name != "x-ms-alpha-trace":
            assert name.lower() not in wire_headers(read)


@pytest.mark.parametrize("failure", ["not_found", "cancelled", "expired_before_read", "expired_during_read"])
def test_empty_body_create_read_failure_does_not_resend_create_rust(empty_body_create_case, failure):
    """If the follow-up read fails, the error reaches the caller and the create is
    not sent again.

    Covered: the read returns 404, the read is cancelled, the deadline passes
    before the read, and the deadline passes during the read. The last two raise
    ``CosmosClientTimeoutError``.
    """
    case = empty_body_create_case
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
def test_container_create_raises_when_response_body_has_no_id_rust(empty_body_create_case, return_properties):
    """If the create response has a body without an ``id``, the call raises
    ``KeyError`` instead of falling back to the requested name.

    Only one request is sent.
    """
    case = empty_body_create_case
    case.creation_response = BackendResponse(201, body=b'{"_rid":"rid1"}')
    with pytest.raises(KeyError, match="id"):
        _call_container_create(case, "c1", PartitionKey("/pk"), return_properties=return_properties)
    assert len(case.operations) == 1


@pytest.mark.parametrize("return_properties", [False, True])
def test_container_create_treats_304_response_as_error_rust(empty_body_create_case, return_properties):
    """A 304 (not modified) response to a create raises ``CosmosHttpResponseError``
    with status 304.

    No follow-up read is sent and the response hook is not called.
    """
    case = empty_body_create_case
    case.creation_response = BackendResponse(304)
    hook = MagicMock()
    with pytest.raises(CosmosHttpResponseError) as raised:
        _call_container_create(case, "c1", PartitionKey("/pk"), return_properties=return_properties, response_hook=hook)
    assert raised.value.status_code == 304
    assert len(case.operations) == 1
    hook.assert_not_called()


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10])
@pytest.mark.parametrize("autoscale", [False, True])
def test_container_create_sends_throughput_headers_and_timeout_rust(container_create_case, timeout, autoscale):
    """A create sends the throughput, custom headers, throughput bucket and timeout.

    A fixed throughput goes in ``x-ms-offer-throughput``, and an autoscale maximum
    goes in ``x-ms-cosmos-offer-autopilot-settings``. The request names the
    database the container is created in, ``db1``.
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
    assert all(
        wire_headers(prepared).get(key.lower()) == str(value)
        for key, value in ({"x-my-app": "provisioner"}).items()
    )
    assert wire_headers(prepared)["x-ms-cosmos-throughput-bucket"] == '7'
    assert settings_options(prepared).get("timeout_seconds") == timeout
    if autoscale:
        assert json.loads(wire_headers(prepared)["x-ms-cosmos-offer-autopilot-settings"]) == {"maxThroughput": 4000}
    else:
        assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'
    case.connection.CreateContainer.assert_not_called()


@pytest.fixture
def container_create_gsi_case(container_create_case, monkeypatch):
    """Sets up a global secondary index create with a fake clock.

    The clock starts at 100 seconds. Looking up the source container moves it
    forward 1 second and returns the internal id ``source-rid``.
    """
    case = container_create_case
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr("azure.cosmos.database.time", clock, raising=False)
    monkeypatch.setattr("azure.cosmos.aio._database.time", clock, raising=False)
    monkeypatch.setattr("azure.cosmos._operation_deadline.time", clock)

    def read_source_container(**_kwargs):
        clock.now += 1.0
        return {"_rid": "source-rid"}

    mock_type = (
        AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    )
    case.source = SimpleNamespace(read=mock_type(side_effect=read_source_container))
    case.database.get_container_client = MagicMock(return_value=case.source)
    return case


@pytest.mark.parametrize(
    "timeout_source", ["call", "client", "override", "inherited", "unset"]
)
def test_container_create_gsi_shares_deadline_rust(
    container_create_gsi_case, timeout_source
):
    """The source container lookup and the create share one deadline.

    Covered: ``timeout=5`` on the call (deadline 105), a client default of 5
    seconds (105), a call ``timeout=3`` that overrides the client default (103), a
    deadline passed in by an outer call (104), and no timeout (no deadline). The
    outer deadline of 104 wins over ``timeout=10`` because it is earlier. The
    internal id from the lookup is sent in the create request body.
    """
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
def test_container_create_gsi_expired_deadline_prevents_create_rust(
    container_create_gsi_case, already_expired
):
    """If the deadline passes, the call raises ``CosmosClientTimeoutError``, the
    create is not sent and the response hook is not called.

    With ``timeout=1`` the lookup uses the whole second, so the call times out
    after the lookup. With a deadline already in the past, the lookup is not sent
    either.
    """
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
    """An invalid ``timeout`` raises ``ValueError`` before the source container
    lookup.

    A timeout must be a number of seconds from 1 up to, but not including, 2**64.
    Covered: 0.5 and NaN.
    """
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
    """Options the SDK cannot send raise ``TypeError`` before the source container
    lookup, whether or not the source container exists.

    Covered: ``connection_timeout``, an unknown keyword, a ``User-Agent`` header,
    and the same kinds of options inside ``request_options`` or ``feed_options``,
    including ``timeout``. The caller's arguments are not changed and the response
    hook is not called.
    """
    case = container_create_gsi_case
    kwargs = deepcopy(kwargs)
    if source_missing:
        case.source.read.side_effect = CosmosResourceNotFoundError(status_code=404)
    kwargs_before = deepcopy(kwargs)
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
    assert kwargs == kwargs_before
    case.source.read.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    hook.assert_not_called()


@pytest.mark.parametrize("option_source", ["request_options", "feed_options"])
def test_container_create_gsi_keeps_options_after_lookup_rust(container_create_gsi_case, option_source):
    """Options given on the call are still sent on the create after the lookup.

    These are the custom header from ``request_options`` or ``feed_options``, the
    throughput and the excluded regions. The excluded regions are given as an
    iterator, which can only be read once. The body has the index definition with
    the source container's internal id, under both
    ``globalSecondaryIndexDefinition`` and ``materializedViewDefinition``. The
    caller's options and index definition are not changed.
    """
    case = container_create_gsi_case
    options = {"initialHeaders": {"x-my-app": "provisioner"}}
    options_before = deepcopy(options)
    index_definition = {"sourceCollectionId": "orders"}
    result = _call_container_create(
        case,
        "c1",
        PartitionKey("/pk"),
        global_secondary_index=index_definition,
        offer_throughput=400,
        excluded_locations=iter(["West US"]),
        **{option_source: options},
    )
    assert result.id == "c1"
    assert options == options_before
    assert index_definition == {"sourceCollectionId": "orders"}
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
def test_container_create_rejects_unsupported_options_before_sending_rust(container_create_case, kwargs):
    """Options the SDK cannot send raise an error, and nothing is sent.

    A bad ``timeout`` raises ``ValueError``: ``False``, ``True``, 0, -1, 0.5, a
    string, NaN, infinity, 2**64 - 1 and 10**400. 2**64 - 1 fails because it
    becomes 2**64 as a float. Other options raise ``TypeError``:
    ``connection_timeout``, an unknown keyword, the ``User-Agent``,
    ``X-MS-VERSION``, ``Accept`` and ``Cache-Control`` headers, ``timeout`` inside
    ``request_options``, and an internal container id inside ``request_options``.
    The response hook is not called.
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
def test_container_create_reports_broken_compiled_module_before_connection_setup_rust(
    container_create_case, monkeypatch, operation, failure,
):
    """A create fails with a clear error when the compiled module is missing or
    broken, before connection setup and before anything is sent.

    A missing module raises ``ImportError``. A missing function, a function set to
    ``None``, or a value that is not a function raises ``RuntimeError`` naming the
    function. The ``read_container`` case adds a global secondary index, so the
    failure happens at the source container lookup.
    """
    case = container_create_case
    asynchronous = isinstance(case.database, AsyncDatabaseProxy)
    sender_module = importlib.import_module(
        "azure.cosmos.aio._backend.binding_adapter" if asynchronous else "azure.cosmos._backend.binding_adapter"
    )
    sender_type = sender_module.AsyncBindingAdapter if asynchronous else sender_module.BindingAdapter
    sender = sender_type("https://unused.invalid", master_key="key")
    connection_setup = AsyncMock() if asynchronous else MagicMock()
    monkeypatch.setattr(sender, "_ensure_driver_handle", connection_setup)
    function_name = operation + ("_async" if asynchronous else "")
    fake_compiled_module = SimpleNamespace()
    if failure == "null_export":
        setattr(fake_compiled_module, function_name, None)
    elif failure == "non_callable_export":
        setattr(fake_compiled_module, function_name, 42)
    monkeypatch.setattr(sender_module, "_rust_module", None if failure == "missing_module" else fake_compiled_module)
    case.connection._backend = sender
    case.connection.ReadContainer = AsyncMock() if asynchronous else MagicMock()
    case.client_context = CosmosClientContext(sender)
    case.database._client_context = case.client_context
    hook = MagicMock()
    kwargs = {"global_secondary_index": {"sourceCollectionId": "orders"}} if operation == "read_container" else {}
    error_type = ImportError if failure == "missing_module" else RuntimeError
    message = "compiled" if failure == "missing_module" else function_name
    try:
        with pytest.raises(error_type, match=message):
            _call_container_create(
                case,
                "c1",
                PartitionKey("/pk"),
                response_hook=hook,
                **kwargs,
            )
        connection_setup.assert_not_called()
        case.connection.ReadContainer.assert_not_called()
        case.connection.CreateContainer.assert_not_called()
        hook.assert_not_called()
    finally:
        closed = sender.close()
        if inspect.isawaitable(closed):
            asyncio.run(closed)


def test_container_create_calls_falsy_hook_with_its_own_headers_copy_rust(
    container_create_case,
):
    """A response hook is called even when the hook object is falsy, meaning
    ``bool(hook)`` is ``False``.

    It is called once. It gets a copy of the returned container settings and its
    own copy of the headers. Changing the request charge in the hook's headers does
    not change the headers on the returned settings. The hook's headers are not the
    same object as the connection object's ``last_response_headers``.
    """
    case = container_create_case
    hook_calls = []

    class FalsyHook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert headers["X-MS-REQUEST-CHARGE"] == "5.25"
            assert isinstance(body, CosmosDict)
            hook_calls.append((headers, body))
            headers["x-ms-request-charge"] = "changed"
            assert body.get_response_headers()["x-ms-request-charge"] == "5.25"

    proxy, properties = _call_container_create(
        case, "c1", PartitionKey(path="/pk"), return_properties=True, response_hook=FalsyHook(),
    )
    assert len(hook_calls) == 1
    assert hook_calls[0][1] is not properties
    assert hook_calls[0][1] == properties
    assert proxy.id == properties["id"]
    assert properties.get_response_headers()["x-ms-request-charge"] == "5.25"
    assert hook_calls[0][0] is not case.connection.last_response_headers


@pytest.mark.parametrize("outcome", ["create", "existing", "missing"])
@pytest.mark.parametrize("return_properties", [False, True])
def test_container_create_hook_cannot_change_result_or_cached_partition_key_rust(
    container_create_case,
    outcome,
    return_properties,
):
    """Changes the response hook makes to its body or headers do not reach the
    returned settings or the cached partition key.

    Covered: a create, a get-or-create on an existing container, and a
    get-or-create on a missing one, with and without ``return_properties``.
    Container settings are cached once. Later changes to the body the hook
    received do not change the cache either.
    """
    case = container_create_case
    container_settings = {
        "id": "c1", "_rid": "rid1",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
    }
    properties = CosmosDict(
        json.loads(json.dumps(container_settings)),
        response_headers=CaseInsensitiveDict({"x-ms-request-charge": "5.25"}),
    )
    case.connection.CreateContainer.return_value = properties
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    case.connection.ReadContainer = mock_type(return_value=properties)
    response = BackendResponse(
        status_code=201 if outcome != "existing" else 200,
        headers=properties.get_response_headers(), body=json.dumps(container_settings).encode(),
    )
    case.backend.execute.side_effect = [response]
    if outcome == "missing":
        case.connection.ReadContainer.side_effect = CosmosResourceNotFoundError(status_code=404)
        case.backend.execute.side_effect = [
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'), response,
        ]
    hook_bodies = []

    def hook(headers, body):
        assert isinstance(body, CosmosDict)
        assert body == container_settings
        assert headers["X-MS-REQUEST-CHARGE"] == "5.25"
        hook_bodies.append(body)
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
    assert cached["partitionKey"] == container_settings["partitionKey"]
    assert len(hook_bodies) == 1
    hook_bodies[0]["partitionKey"]["paths"].append("/later-edit")
    assert cached["partitionKey"] == container_settings["partitionKey"]
    if return_properties:
        assert result[1] == container_settings
        assert result[1] is not hook_bodies[0]
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
def test_container_create_sends_match_condition_headers_rust(
    container_create_case, kwargs, expected
):
    """``etag`` and ``match_condition`` become the right ``If-Match`` or
    ``If-None-Match`` header, with no warning.

    Covered: no condition; an etag with ``IfNotModified`` and with ``IfModified``;
    ``IfPresent`` and ``IfMissing`` alone, which send ``*``; the same two with an
    etag, which is ignored; and the ``if_match`` and ``if_none_match`` keywords.
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
def test_container_create_invalid_conditions_fail_before_sending_rust(container_create_case, kwargs, error_type):
    """An incomplete or invalid condition raises an error before anything is sent.

    An etag with no condition, ``IfNotModified`` or ``IfModified`` with no etag,
    and an empty etag raise ``ValueError``. A condition that is not a
    ``MatchConditions`` value raises ``TypeError``.
    """
    case = container_create_case
    with pytest.raises(error_type):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("failure_source", ["hook", "sender"])
@pytest.mark.parametrize("error_type", [ValueError, NotImplementedError, ServiceRequestError, asyncio.CancelledError])
def test_container_create_errors_are_raised_unchanged_and_not_retried_rust(
    container_create_case, failure_source, error_type
):
    """An error from the response hook or from the fake sender reaches the caller as
    the same object, and the fake sender is called only once.

    Covered: ``ValueError``, ``NotImplementedError``, ``ServiceRequestError`` (the
    service could not be reached) and ``asyncio.CancelledError``.
    """
    case = container_create_case
    error = error_type("create failed")
    hook = MagicMock(side_effect=error if failure_source == "hook" else None)
    if failure_source == "sender":
        case.backend.execute.side_effect = error
    with pytest.raises(error_type) as raised:
        _call_container_create(case, "c1", PartitionKey(path="/pk"), response_hook=hook)
    assert raised.value is error
    assert hook.call_count == (1 if failure_source == "hook" else 0)
    case.backend.execute.assert_called_once()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("status", [400, 403, 404, 409, 412, 429, 500])
def test_container_create_service_errors_keep_status_and_are_not_retried_rust(container_create_case, status):
    """An error status from the service raises ``CosmosHttpResponseError`` with that
    status, and the fake sender is called only once.

    Covered: 400, 403, 404, 409, 412, 429 and 500. A 409 raises
    ``CosmosResourceExistsError`` and a 404 raises ``CosmosResourceNotFoundError``.
    The response hook is not called.
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


def test_container_get_or_create_creates_container_when_read_returns_404_rust(container_create_case):
    """When the read returns 404, get-or-create creates the container.

    The fake sender is called twice, and the second call is the create.
    """
    case = container_create_case
    not_found_error = CosmosResourceNotFoundError(status_code=404, message="missing")
    mock_type = AsyncMock if isinstance(case.database, AsyncDatabaseProxy) else MagicMock
    case.connection.ReadContainer = mock_type(side_effect=not_found_error)
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
def test_container_get_or_create_returns_same_result_and_keeps_existing_settings_rust(
    container_get_or_create_case, return_properties, positional_count
):
    """Get-or-create returns the same result however the arguments are passed, and
    does not change a container that already exists.

    The name and partition key are passed by position, by keyword or both, with and
    without ``return_properties``. When the container exists, the returned settings
    are the existing ones (partition key path ``/original``, time to live 10), not
    the values passed to the call. The response hook is called once with the
    request charge of the last request: 2 for the read, 5.25 for the create.
    Throughput is sent only on the create. The ``timeout``, the deadline and the
    custom header are the same on both requests. Container settings are cached
    once.
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
def test_container_get_or_create_sends_headers_from_option_dicts_rust(
    container_get_or_create_case, monkeypatch, source, override
):
    """Headers given as ``initialHeaders`` inside ``request_options`` or
    ``feed_options`` are sent on the read and on the create.

    A top-level ``initial_headers`` replaces them when it is set, even to an empty
    dict; ``initial_headers=None`` does not. The create options are checked once,
    before the read. The caller's arguments are not changed.
    """
    case = container_get_or_create_case
    nested_headers = {"x-company-trace": "nested", "x-ms-cosmos-priority-level": "Low"}
    kwargs = {source: {"initialHeaders": nested_headers}}
    expected = nested_headers
    if override != "absent":
        top_level_headers = {
            "none": None,
            "empty": {},
            "value": {"x-company-trace": "override"},
        }[override]
        kwargs["initial_headers"] = top_level_headers
        if top_level_headers is not None:
            expected = top_level_headers
    kwargs_before = deepcopy(kwargs)
    create_options_check = MagicMock(wraps=is_create_container_rust_eligible)
    monkeypatch.setattr(
        "azure.cosmos._helpers._request_container.is_create_container_rust_eligible",
        create_options_check,
    )
    assert _call_get_or_create(case, **kwargs).id == "c1"
    assert kwargs == kwargs_before
    create_options_check.assert_called_once()
    assert create_options_check.call_args.args[0]["initialHeaders"] == expected
    operations = [call.args[0] for call in case.backend.execute.call_args_list]
    assert [op.op for op in operations] == (
        [OP_READ_CONTAINER, OP_CREATE_CONTAINER]
        if case.missing
        else [OP_READ_CONTAINER]
    )
    for operation in operations:
        headers = wire_headers(operation)
        for name in nested_headers:
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
    """Any ``retry_write`` value other than ``None`` raises ``TypeError`` before the
    read, because the SDK handles write retries itself.

    This covers the keyword and the same option inside ``request_options`` or
    ``feed_options``, including when another place sets it to ``None``. Nothing is
    sent, the source container is not looked up, no settings are cached, the
    response hook is not called, and the caller's arguments are not changed.
    """
    case = container_get_or_create_case
    kwargs_before = deepcopy(kwargs)
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
    assert kwargs == kwargs_before
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
def test_container_get_or_create_accepts_retry_write_none_rust(
    container_get_or_create_case, kwargs
):
    """Leaving out ``retry_write``, or setting it to ``None`` as a keyword or inside
    ``request_options`` or ``feed_options``, is accepted.

    No ``retry_write`` setting is sent on the read or the create, and the caller's
    arguments are not changed.
    """
    case = container_get_or_create_case
    kwargs_before = deepcopy(kwargs)
    assert _call_get_or_create(case, **kwargs).id == "c1"
    assert kwargs == kwargs_before
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
def test_container_get_or_create_checks_create_options_before_read_rust(container_get_or_create_case, kwargs):
    """Options the SDK cannot send raise an error before the read, even when only
    the create would fail on them.

    A bad ``timeout`` raises ``ValueError``: 0.5, ``False``, NaN, infinity, 2**64
    and a string. Other options raise ``TypeError`` naming the method:
    ``connection_timeout``, a ``User-Agent`` header, an unknown keyword,
    ``populate_quota_info``, ``populate_partition_key_range_statistics`` and an
    internal container id in ``request_options``. Nothing is sent, no settings are
    cached, and the response hook is not called.
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
    """An incomplete or invalid condition raises an error before the read.

    An etag with no condition and ``IfNotModified`` with no etag raise
    ``ValueError``. A condition that is not a ``MatchConditions`` value raises
    ``TypeError``. Nothing is sent and no settings are cached.
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
def test_container_get_or_create_sends_match_condition_on_every_request_rust(
    container_get_or_create_case, kwargs, expected
):
    """A valid condition is sent on every request the call makes, with no warning.

    When the container is missing, that means both the read and the create.
    Covered: ``IfModified`` and ``IfNotModified`` with an etag, and ``IfMissing``
    and ``IfPresent``, which send ``*`` and ignore the etag.
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
def test_container_get_or_create_hook_errors_are_not_treated_as_not_found_rust(
    container_get_or_create_case, error
):
    """An error raised by the response hook is not treated as "container not found".

    Get-or-create catches a not-found error from the read to decide whether to
    create the container. The hook runs later. If it raises any error, including
    not-found or conflict, that error reaches the caller unchanged. The hook runs
    once, no extra requests are sent, the connection object is not used, and the
    container settings are not cached.
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


def test_container_get_or_create_calls_falsy_hook_with_its_own_headers_copy_rust(container_get_or_create_case):
    """A response hook that evaluates as false is still called, and it cannot
    change the result.

    The hook gets its own copy of the headers, so editing them does not change the
    headers on the returned properties. The hook also replaces the client's last
    response headers, as if another request finished on the same client at the
    same time. The returned properties still show the request charge from this
    call.
    """
    case = container_get_or_create_case
    hook_results = []

    class FalsyHook:
        def __bool__(self):
            return False

        def __call__(self, headers, properties):
            assert headers is not properties.get_response_headers()
            headers["X-MS-REQUEST-CHARGE"] = "changed"
            case.connection.last_response_headers = {"x-ms-request-charge": "another request"}
            hook_results.append(properties)

    _, properties = _call_get_or_create(case, return_properties=True, response_hook=FalsyHook())
    assert hook_results == [properties]
    assert properties.get_response_headers()["x-ms-request-charge"] == ("5.25" if case.missing else "2")


@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("read_status", [200, 403, 404, 409])
def test_container_get_or_create_reads_again_once_after_create_conflict_rust(
    container_create_case,
    return_properties,
    read_status,
):
    """If the create gets a conflict, the SDK reads the container once more.

    A conflict means another caller created the container between the read and
    the create. The SDK sends the same read request again, with the same deadline
    as the first two requests, and does not send the create again.

    - If that read succeeds, the caller gets the container. The response hook is
      called once with that read's headers and result. Changes the hook makes do
      not reach the cached settings.
    - If that read fails with 403, 404 or 409, the error reaches the caller. The
      hook is not called and nothing is cached.
    """
    case = container_create_case
    other_callers_container = CosmosDict(
        {"id": "c1", "_rid": "winner", "partitionKey": {"paths": ["/original"]}, "defaultTtl": 10},
        response_headers=CaseInsensitiveDict({"x-ms-activity-id": "winning-read"}),
    )
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
            headers=other_callers_container.get_response_headers(),
            body=json.dumps(
                other_callers_container if error_type is None else {"message": "reread"}
            ).encode(),
        ),
    ]
    hook_headers = []

    def hook(headers, properties):
        assert headers["X-MS-ACTIVITY-ID"] == "winning-read"
        assert properties == other_callers_container
        properties["partitionKey"]["paths"].append("/hook-edit")
        hook_headers.append(headers)

    call_kwargs = dict(
        return_properties=return_properties, response_hook=hook, timeout=10,
        offer_throughput=400, default_ttl=99,
        initial_headers={"x-company-trace": "setup"},
        etag='"v1"', match_condition=MatchConditions.IfNotModified,
    )
    if error_type is not None:
        with pytest.raises(error_type) as raised:
            _call_get_or_create(case, **call_kwargs)
        assert raised.value.status_code == read_status
        assert not hook_headers
        case.connection._set_container_properties_cache.assert_not_called()
    else:
        result = _call_get_or_create(case, **call_kwargs)
        proxy = result[0] if return_properties else result
        assert proxy.id == "c1"
        assert proxy._client_context is case.client_context
        if return_properties:
            assert result[1] == other_callers_container
        assert len(hook_headers) == 1
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
def test_container_get_or_create_raises_failures_without_retry_rust(
    container_create_case, missing, status
):
    """A failed read or create raises an error with the service's status code, and
    the request is not retried.

    The read is tested with 401, 403, 409, 429 and 500. The create, sent after the
    read returns 404, is tested with 401, 403, 404, 409, 429 and 500. A 404 from
    the first read is not a failure: it tells the SDK to create the container, and
    it has its own test.

    A 409 from the create is a conflict, so the SDK reads the container once more.
    In this test that read also fails, and its error reaches the caller without
    another create. In every case the response hook is not called and nothing is
    cached.
    """
    case = make_container_get_or_create_case(container_create_case, missing)
    error_type = (
        CosmosResourceExistsError
        if status == 409
        else (CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError)
    )
    responses = []
    if case.missing:
        responses.append(
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}')
        )
    responses.append(
        BackendResponse(status_code=status, headers={}, body=b'{"message":"failure"}')
    )
    if case.missing and status == 409:
        responses.append(
            BackendResponse(status_code=409, headers={}, body=b'{"message":"reread"}')
        )
    case.backend.execute.side_effect = responses
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


def test_concurrent_container_get_or_create_calls_all_return_the_container_rust(container_create_case):
    """Eight get-or-create calls for the same container, run at the same time,
    all return that container.

    All eight reads return 404 before any create is sent. The first create
    succeeds with 201. The other seven get a conflict (409), so each of them reads
    the container again and gets it (200). In total the fake sender gets 23
    requests: 15 reads and 8 creates. Each call runs the response hook once and
    caches the settings once. The sync client runs the calls on threads; the async
    client runs them as tasks.
    """
    case = container_create_case
    asynchronous = isinstance(case.database, AsyncDatabaseProxy)
    thread_gate = Barrier(8)
    async_gate = asyncio.Event()
    lock = Lock()
    read_count = 0
    container_created = False
    container = {"id": "c1", "_rid": "winner", "partitionKey": {"paths": ["/pk"]}}

    def build_response(operation, initial_read):
        nonlocal container_created
        with lock:
            if initial_read:
                status = 404
            elif operation == OP_CREATE_CONTAINER:
                status = 409 if container_created else 201
                container_created = True
            else:
                status = 200
        return BackendResponse(
            status_code=status, headers={"x-ms-activity-id": operation},
            body=json.dumps(container if status < 400 else {"message": "race"}).encode(),
        )

    def is_first_read(operation):
        nonlocal read_count
        with lock:
            if operation == OP_READ_CONTAINER:
                read_count += 1
                return read_count <= 8
        return False

    def execute(operation):
        first_read = is_first_read(operation)
        if first_read:
            thread_gate.wait(timeout=10)
        return build_response(operation, first_read)

    async def execute_async(operation):
        first_read = is_first_read(operation)
        if first_read:
            if read_count == 8:
                async_gate.set()
            await asyncio.wait_for(async_gate.wait(), 10)
        return build_response(operation, first_read)

    def send(operation):
        if not asynchronous:
            reply = execute(operation)
            return reply

        async def run():
            reply = await execute_async(operation)
            return reply
        return run()

    async def fake_execute_async(prepared, **_kwargs):
        return await send(prepared.op)

    case.backend.execute.side_effect = (
        fake_execute_async
        if asynchronous
        else lambda prepared, **_k: send(prepared.op)
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
    assert read_count == 15
    assert case.backend.execute.call_count == 23
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("error", [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()])
def test_container_get_or_create_unexpected_errors_are_raised_unchanged_rust(container_get_or_create_case, error):
    """An unexpected error while sending a request reaches the caller unchanged,
    and the call is not retried.

    The error happens on the last request: the read when the container exists, or
    the create when it does not. The test covers an ordinary error (``ValueError``),
    an unsupported-feature error (``NotImplementedError``) and cancellation
    (``asyncio.CancelledError``). The connection object is not used to try the
    call again. A second try would be wrong because the create may already have
    worked, so it could report a conflict for a container the caller just created.
    """
    case = container_get_or_create_case
    responses = []
    if case.missing:
        responses.append(BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}'))
    case.backend.execute.side_effect = responses + [error]
    with pytest.raises(type(error)) as raised:
        _call_get_or_create(case)
    assert raised.value is error
    case.connection.ReadContainer.assert_not_called()
    case.connection.CreateContainer.assert_not_called()
    assert case.backend.execute.call_count == (2 if case.missing else 1)


@pytest.mark.parametrize(
    "header_source", ["initial_headers", "request_options", "feed_options"]
)
def test_container_get_or_create_handles_empty_body_read_and_create_rust(
    container_get_or_create_case,
    header_source,
):
    """An empty response body is handled differently for the read and for the
    create.

    The caller passes ``return_properties=True`` and ``match_condition=IfMissing``.

    - Container exists: the read returns 304 (not modified) with no body. The
      caller gets empty properties, and no create is sent.
    - Container missing: the create returns 201 with no body. The SDK sends a
      follow-up read without the ``if-none-match`` header, and returns the
      settings from that read.

    The custom header reaches every request, whether it was passed as
    ``initial_headers`` or inside ``request_options`` or ``feed_options``. The
    response hook is called once, with the first (empty) result, not with the
    follow-up read.
    """
    case = container_get_or_create_case
    empty_result = CosmosDict({}, response_headers=CaseInsensitiveDict({"etag": '"v1"'}))
    responses = []
    if case.missing:
        responses.append(
            BackendResponse(status_code=404, headers={}, body=b'{"message":"missing"}')
        )
    responses.append(
        BackendResponse(
            status_code=201 if case.missing else 304,
            headers=empty_result.get_response_headers(),
            body=b"",
        )
    )
    if case.missing:
        responses.append(
            BackendResponse(
                status_code=200,
                headers=case.existing_properties.get_response_headers(),
                body=json.dumps(case.existing_properties).encode(),
            )
        )
    case.backend.execute.side_effect = responses
    hook = MagicMock()
    kwargs = dict(
        match_condition=MatchConditions.IfMissing,
        return_properties=True,
        response_hook=hook,
    )
    custom_headers = {"x-company-trace": "setup"}
    kwargs[header_source] = (
        custom_headers if header_source == "initial_headers" else {"initialHeaders": custom_headers}
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


def test_container_get_or_create_read_preparation_does_not_change_caller_options_rust():
    """Preparing the read does not change the arguments the caller passed.

    The same arguments are used again for the create that may follow, so they must
    stay unchanged, including the nested headers dictionary. The test also checks
    the prepared read:

    - the call is supported;
    - ``match_condition=IfMissing`` becomes an if-none-match condition on ``"*"``;
    - throughput is left out, because it only applies to the create;
    - only ``timeout`` is left in the remaining keywords.
    """
    from azure.cosmos._helpers._request_container import prepare_container_get_or_create_read

    kwargs = {"request_options": {"initialHeaders": {"x-company-trace": "setup"}},
              "match_condition": MatchConditions.IfMissing, "etag": "unused", "timeout": 10}
    kwargs_before = deepcopy(kwargs)
    read_options, remaining_kwargs, supported, _deadline = prepare_container_get_or_create_read(
        kwargs, initial_headers=None, offer_throughput=400
    )
    assert supported
    assert kwargs == kwargs_before
    assert read_options["accessCondition"] == {"type": "IfNoneMatch", "condition": "*"}
    assert "offerThroughput" not in read_options
    assert remaining_kwargs == {"timeout": 10}


# --- single and paged operations ---------------------------------------


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
@pytest.mark.parametrize("timeout_seconds", [None, 0.125, 1.0])
@pytest.mark.parametrize("include_attempts", [False, True])
def test_compiled_container_functions_reject_a_string_handle_rust(operation, suffix, timeout_seconds, include_attempts):
    """The compiled read and create functions raise ``TypeError`` when given a
    string instead of a handle.

    The test also checks two keyword defaults: ``timeout_seconds`` is ``None``
    and ``include_attempts`` is ``False``.
    """
    from azure.cosmos import _rust

    prepared = (
        build_read_container_prepared("dbs/db1/colls/c1", {})
        if operation == "read_container"
        else build_create_container_prepared("dbs/db1", {"id": "c1"}, {})
    )
    compiled_function = getattr(_rust, operation + suffix)
    assert inspect.signature(compiled_function).parameters["timeout_seconds"].default is None
    assert inspect.signature(compiled_function).parameters["include_attempts"].default is False
    with pytest.raises(TypeError, match="_DriverHandle"):
        compiled_function("unregistered-container-composed-test", prepared,
               timeout_seconds=timeout_seconds, include_attempts=include_attempts)


@pytest.mark.parametrize("operation", ["read_container", "create_container"])
@pytest.mark.parametrize("suffix", ["", "_async"])
@pytest.mark.parametrize("invalid_timeout", [0, -1, float("inf"), float("nan")])
def test_compiled_container_functions_check_the_handle_before_the_timeout_rust(operation, suffix, invalid_timeout):
    """The handle is checked before the timeout.

    A string handle raises ``TypeError`` even when the timeout is also invalid
    (0, -1, infinity or NaN).
    """
    from azure.cosmos import _rust

    prepared = (
        build_read_container_prepared("dbs/db1/colls/c1", {})
        if operation == "read_container"
        else build_create_container_prepared("dbs/db1", {"id": "c1"}, {})
    )
    with pytest.raises(TypeError, match="_DriverHandle"):
        getattr(_rust, operation + suffix)(
            "unregistered-container-composed-test", prepared, timeout_seconds=invalid_timeout
        )


def test_create_container_request_names_the_database_and_carries_the_definition_rust():
    """The create request carries the database name and the full container
    definition.

    The container does not exist yet, so the database name goes in ``item_id``
    and ``container_link`` is empty. The body is the whole definition, including
    the partition key and default TTL. The partition key header is ``"[]"``,
    because the request is not for one partition. Throughput, custom headers and
    the timeout are carried too.
    """
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


def test_create_container_request_drops_the_session_token_rust():
    """The SDK does not send a session token with a container create, so a token
    passed in the options is dropped. Other options, such as throughput, are kept.
    """
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"sessionToken": "s1", "offerThroughput": 400},
    )

    assert "sessionToken" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'


def test_create_container_request_rejects_a_link_with_no_database_rust():
    """The link ``"dbs/"`` has no database name, so building the request raises
    ``ValueError``.
    """
    with pytest.raises(ValueError):
        build_create_container_prepared("dbs/", {"id": "c1"}, {})


def test_create_container_request_ignores_initial_headers_set_to_none_rust():
    """If the options contain ``initialHeaders=None``, the request is still built
    and no custom headers are sent.
    """
    prepared = build_create_container_prepared(
        "dbs/db1",
        {"id": "c1"},
        {"initialHeaders": None, "offerThroughput": 400},
    )

    assert "initialHeaders" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'


def test_list_containers_request_has_an_empty_body_rust():
    """A list request has no query, so its body is empty and ``container_link`` is
    the database link.

    If listing were not marked as a request without a query, building it would
    fail because no query is set.
    """
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


def test_query_containers_request_sends_the_query_as_json_body_rust():
    """The query is sent as JSON in the request body.
    """
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


# --- create_container support checks -------------------------------------


def test_create_container_is_supported_with_standard_options_rust():
    """A create with only standard options, such as throughput and a timeout, is
    supported.
    """
    assert is_create_container_rust_eligible({"offerThroughput": 400}, {"timeout": 3.5}) is True


def test_create_container_is_not_supported_with_an_intended_container_internal_id_rust():
    """A create is not supported when the options include an intended container
    internal id (``Constants.ContainerRID``).

    For other requests the SDK sends that value in the
    ``x-ms-cosmos-intended-collection-rid`` header.
    """
    assert is_create_container_rust_eligible({Constants.ContainerRID: "rid1"}, {}) is False


# --- create_container through the helper ---------------------------------


def test_sync_create_container_helper_uses_the_sender_and_calls_the_hook_once_rust():
    """The sync container helper sends the create through the fake sender, not the
    connection object.

    It returns the created container, stores the response headers on the
    connection object, and calls the response hook once.
    """
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    sender = _FakeBackend()
    hook_calls = []

    result = ContainerHelper(connection, sender).create_container(
        "dbs/db1",
        {"id": "c1"},
        {"offerThroughput": 400},
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
    )

    assert result["id"] == "c1"
    assert sender.prepared.op == OP_CREATE_CONTAINER
    assert sender.prepared.item_id == "db1"
    connection.CreateContainer.assert_not_called()
    assert connection.last_response_headers["x-ms-request-charge"] == "5.25"
    assert len(hook_calls) == 1
    assert hook_calls[0][1] == {"id": "c1", "_rid": "rid1"}


def test_async_create_container_helper_uses_the_sender_rust():
    """The async container helper builds the same create request as the sync
    helper and sends it through the fake sender.

    It is separate code, so it is tested on its own.
    """
    connection = SimpleNamespace(
        CreateContainer=MagicMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    sender = _AsyncFakeBackend()

    result = asyncio.run(
        AsyncContainerHelper(connection, sender).create_container(
            "dbs/db1",
            {"id": "c1"},
            {"offerThroughput": 400},
        )
    )

    assert result["id"] == "c1"
    assert sender.prepared.op == OP_CREATE_CONTAINER
    assert sender.prepared.item_id == "db1"
    connection.CreateContainer.assert_not_called()


# --- feed request shape ---------------------------------------------------


def test_list_containers_request_carries_the_database_link_rust():
    """A list request carries the database link in ``container_link``, because the
    list covers one database.

    Page size and continuation are carried too, and there is no query.
    """
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


def test_query_containers_request_carries_the_query_and_the_database_link_rust():
    """A query request carries the database link, the query text and its
    parameters.
    """
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


def test_container_list_request_keeps_custom_headers_rust():
    """A custom header the caller sets on a list request is sent with the request.
    """
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_page(
        path=path,
        options={"initialHeaders": {"x-custom-tag": "value"}},
        req_headers={"x-custom-tag": "value"},
    )

    assert all(
        wire_headers(prepared).get(key.lower()) == str(value)
        for key, value in ({"x-custom-tag": "value"}).items()
    )


# --- feed support checks --------------------------------------------------


def _list_containers_supported(path="dbs/db1/colls", options=None, kwargs=None, resource_type=_COLLECTION):
    """Call ``can_use_rust_list_containers`` with default arguments, so each test
    passes only what it changes.
    """
    return can_use_rust_list_containers(
        path=path,
        options=options or {},
        kwargs=kwargs or {},
        is_query_plan=False,
        resource_type=resource_type,
    )


def test_list_containers_is_supported_with_no_extra_options_rust():
    """A list request with no extra options is supported.
    """
    assert _list_containers_supported() is True


def test_list_containers_is_not_supported_without_a_database_in_the_path_rust():
    """A list request is not supported when the path has no database name
    (``dbs//colls``) or does not point to containers (``dbs/db1/docs``).
    """
    assert _list_containers_supported(path="dbs//colls") is False
    assert _list_containers_supported(path="dbs/db1/docs") is False


def test_list_containers_is_not_supported_for_another_resource_type_rust():
    """The container list check returns ``False`` for other resource types, such
    as databases. Those have their own checks.
    """
    assert _list_containers_supported(resource_type=http_constants.ResourceType.Database) is False


def test_query_containers_is_supported_for_a_dict_query_rust():
    """A query passed as a dict, sent as ``application/query+json``, is supported.
    """
    assert can_use_rust_query_containers(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is True


def test_query_containers_is_not_supported_for_a_string_query_rust():
    """A query passed as a plain string is not supported.

    The SDK sends a string query as ``text/plain``, while supported queries are
    sent as ``application/query+json``.
    """
    assert can_use_rust_query_containers(
        path="dbs/db1/colls",
        query_payload="SELECT * FROM c",
        options={},
        kwargs={},
        is_query_plan=False,
        resource_type=_COLLECTION,
    ) is False


def test_query_containers_is_not_supported_for_a_query_plan_request_rust():
    """A query plan request is not supported for container queries.
    """
    assert can_use_rust_query_containers(
        path="dbs/db1/colls",
        query_payload={"query": "SELECT * FROM c"},
        options={},
        kwargs={},
        is_query_plan=True,
        resource_type=_COLLECTION,
    ) is False


# --- container read -------------------------------------------------------


def _read_container_response() -> BackendResponse:
    """Return a 200 response whose body is a container with a partition key.
    """
    return BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-request-charge": "1.0"}),
        body=b'{"id":"c1","_rid":"rid1","partitionKey":{"paths":["/pk"],"kind":"Hash"}}',
    )


def test_read_container_request_carries_the_database_and_container_names_rust():
    """The container is read by name, so the request link contains both the
    database name and the container name.
    """
    prepared = build_read_container_prepared("dbs/db1/colls/c1", {})

    assert prepared.op == OP_READ_CONTAINER
    assert prepared.container_link == "dbs/db1/colls/c1"


def test_read_container_request_strips_slashes_from_the_link_rust():
    """Leading and trailing slashes are removed from the link.
    """
    prepared = build_read_container_prepared("/dbs/db1/colls/c1/", {})

    assert prepared.container_link == "dbs/db1/colls/c1"


@pytest.mark.parametrize(
    "link",
    ["dbs/db1", "dbs/db1/colls", "dbs/db1/colls/", "dbs//colls/c1", "colls/c1"],
)
def test_read_container_request_rejects_a_link_missing_a_name_rust(link):
    """A link without both a database name and a container name raises
    ``ValueError`` before any request is sent.
    """
    with pytest.raises(ValueError):
        build_read_container_prepared(link, {})


def test_read_container_request_drops_the_session_token_rust():
    """The SDK does not send a session token with a container read, so a token
    passed in the options is dropped.
    """
    prepared = build_read_container_prepared(
        "dbs/db1/colls/c1",
        {"sessionToken": "0:1#22"},
    )

    assert "sessionToken" not in wire_headers(prepared)


def test_read_container_is_supported_with_no_extra_options_rust():
    """A read with no extra options is supported.
    """
    assert is_read_container_rust_eligible({}, {}) is True


@pytest.mark.parametrize(
    "option",
    ["populatePartitionKeyRangeStatistics", "populateQuotaInfo"],
)
def test_read_container_is_supported_when_statistics_are_requested_rust(option):
    """A read that asks for partition key range statistics or quota information is
    supported.
    """
    assert is_read_container_rust_eligible({option: True}, {}) is True


def test_sync_read_container_helper_uses_the_sender_and_calls_the_hook_once_rust():
    """The sync container helper sends the read through the fake sender, not the
    connection object.

    It returns the container, stores the response headers on the connection
    object, and calls the response hook once.
    """
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    sender = _FakeBackend(_read_container_response())
    hook_calls = []

    result = ContainerHelper(connection, sender).read_container(
        "dbs/db1/colls/c1",
        {},
        response_hook=lambda headers, body: hook_calls.append((headers, body)),
    )

    assert result["id"] == "c1"
    assert sender.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()
    assert connection.last_response_headers["x-ms-request-charge"] == "1.0"
    assert len(hook_calls) == 1


def test_async_read_container_helper_uses_the_sender_rust():
    """The async container helper sends the read through the fake sender, not the
    connection object, and returns the container.
    """
    connection = SimpleNamespace(
        ReadContainer=MagicMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    sender = _AsyncFakeBackend(_read_container_response())

    result = asyncio.run(
        AsyncContainerHelper(connection, sender).read_container(
            "dbs/db1/colls/c1",
            {},
        )
    )

    assert result["id"] == "c1"
    assert sender.prepared.op == OP_READ_CONTAINER
    connection.ReadContainer.assert_not_called()


# --- asynchronous response hooks ------------------------------------------


def test_async_create_container_helper_calls_the_hook_once_rust():
    """The async create calls the response hook once, with the response headers
    and a copy of the result.
    """
    connection = SimpleNamespace(
        CreateContainer=AsyncMock(side_effect=AssertionError("legacy create called")),
        last_response_headers={},
    )
    hook_calls = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncFakeBackend()).create_container(
            "dbs/db1",
            {"id": "c1"},
            {},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )
    )

    assert len(hook_calls) == 1
    assert hook_calls[0][1] is not result
    assert hook_calls[0][1] == result
    assert hook_calls[0][0] == result.get_response_headers()
    connection.CreateContainer.assert_not_called()


def test_async_read_container_helper_calls_the_hook_once_rust():
    """The async read calls the response hook once, with the response headers and
    a copy of the result.
    """
    connection = SimpleNamespace(
        ReadContainer=AsyncMock(side_effect=AssertionError("legacy read called")),
        last_response_headers={},
    )
    hook_calls = []

    result = asyncio.run(
        AsyncContainerHelper(connection, _AsyncFakeBackend(_read_container_response())).read_container(
            "dbs/db1/colls/c1",
            {},
            response_hook=lambda headers, body: hook_calls.append((headers, body)),
        )
    )

    assert len(hook_calls) == 1
    assert hook_calls[0][1] == result
    assert hook_calls[0][1] is not result
    assert hook_calls[0][0] == result.get_response_headers()
    connection.ReadContainer.assert_not_called()
