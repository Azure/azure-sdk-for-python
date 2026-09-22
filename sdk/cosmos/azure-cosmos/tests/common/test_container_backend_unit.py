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

* the request the Rust engine is handed. A container create is scoped to a
  database, not to a container -- the container does not exist yet -- so the
  database name rides in ``item_id`` and the definition the caller assembled
  rides in the body. Get either wrong and the container is created in the wrong
  database or with the wrong policies.
* the feed pages carrying the owning database. ``PreparedPageRequest`` has no field for
  a database name, so the ``dbs/{id}`` link rides in ``container_link``. If the
  path cannot be parsed the gate must say no, so the call stays on the legacy
  path instead of running against nothing.
* the ``DocumentCollections`` envelope. The legacy reader pulls containers out of
  that key; a database feed uses ``Databases``. Getting it wrong yields a
  silently empty list rather than an error, which is the worst kind of wrong.
* routing away from Rust when Rust cannot honor an option exactly -- a
  sub-second ``timeout``, a socket-level ``read_timeout``, a query in the
  legacy-only string form that goes on the wire as ``text/plain``.
* create rejects obsolete keywords and unsupported Rust calls rather than
  silently switching transports. Conditional-header normalization is preserved.

All fakes, no Cosmos account.
"""

from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings

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
from azure.cosmos._backend.contracts import BackendResponse, BackendPage
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
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
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders
from common.typed_requests import flatten_options_to_headers
from azure.cosmos._query_rust_routing import (
    build_list_containers_prepared_query,
    build_query_containers_prepared_query,
    can_use_rust_backend_for_list_containers_page,
    can_use_rust_backend_for_query_containers_page,
)
from azure.cosmos.aio._helpers._container_operations import AsyncContainerHelper
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
    """Stand-in Rust backend: records the request it was handed and returns a
    canned reply, so a test can check what would have gone on the wire."""
    name = "rust"

    def __init__(self, response=None):
        """Store an optional canned reply; default to a 201 Created container response."""
        self.response = response or _created_container_response()
        self.prepared = None

    def execute(self, prepared, *, deadline=None):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


class _AsyncRustBackend(AsyncCosmosBackend):
    """Async stand-in Rust backend: records the request it was handed and returns
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

    async def execute(self, prepared, *, deadline=None):
        """Record the prepared request and return the canned reply."""
        self.prepared = prepared
        return self.response


@pytest.fixture(params=["sync", "async"])
def container_create_case(request):
    """Build a container create that runs once as a sync client and once as async.

    Both clients are driven through the same tests because the sync and async
    paths build their requests through separate code and could drift apart.

    The connection is a stand-in with a recording ``CreateContainer`` for the
    legacy route and a recording cache write, so a test can prove which route ran
    and whether the new container's properties were remembered.

    Handing out the legacy backend as well lets a test flip the connection over
    mid-setup and run the same call on the other engine.
    """
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
    """Call the named create method on the database and wait for it if the client is async.

    The method name is an argument because plain create and get-or-create share
    almost all of their rules, so most tests here run against both.
    """
    result = getattr(case.database, method)(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("method", ["create_container", "create_container_if_not_exists"])
@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_container_create_rejects_obsolete_keywords(container_create_case, use_legacy, method, option, value):
    """Retired options are refused on both create methods, both engines, and every value.

    Session token and query metrics no longer do anything. Passing one raises
    ``TypeError`` naming it, even when the value is ``None`` or ``False``,
    because it is the presence of the option that signals a stale expectation.

    Nothing is created and the customer's hook never runs, so the refusal cannot
    be mistaken for a call that partly happened.
    """
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
    """The socket-level ``read_timeout`` is not accepted per call on either create
    method or either engine.

    False, half a second, one second, and a string all raise ``TypeError`` naming
    the option, so the error points straight at what to remove. Nothing is
    created.
    """
    case = container_create_case
    if use_legacy:
        case.connection._backend = case.legacy_backend
    with pytest.raises(TypeError, match="read_timeout"):
        _call_container_create(case, "c1", PartitionKey(path="/pk"), method=method, read_timeout=timeout)
    case.backend.execute.assert_not_called()
    case.connection.CreateContainer.assert_not_called()


@pytest.mark.parametrize("extra_args", [(None,), (None, None), (None, None, False), (None, None, None, 400)])
def test_container_create_optional_settings_are_keyword_only(container_create_case, extra_args):
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
def test_container_create_retains_manual_runtime_signature(container_create_case, method):
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
def test_container_get_or_create_overloads_match_keyword_only_contract(proxy_type):
    """The published signatures agree with the rules the runtime enforces.

    Because get-or-create accepts open-ended arguments at runtime, the two
    declared forms are what customers actually see in editors and docs. Both
    must show only the container name and partition key as positional, show
    settings as keyword-only, and must not still advertise the retired query
    metrics option. Sync and async are both checked.
    """
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
    """Calls that do not match the signature fail before anything is created, with a
    message naming the method and the problem.

    Nine shapes are covered: nothing at all, a partition key with no name, a name
    with no partition key, each of the two given twice, and settings passed by
    position. Each error names the method the customer called, so the same
    wording does not appear for both create methods.

    Two further guarantees: the caller's keyword dictionary is unchanged, so
    argument parsing reads rather than consumes, and the fallback counter does
    not move, since a mistake in the customer's own call is not the Rust engine
    being unable to do something.
    """
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


def test_container_create_argument_binding_does_not_consume_arguments_on_error():
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


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_create_preserves_required_arguments_and_return_shapes(
    container_create_case, use_legacy, return_properties, positional_count
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


@pytest.mark.parametrize("timeout", [None, 1, 3.5, 10])
@pytest.mark.parametrize("autoscale", [False, True])
def test_container_create_preserves_throughput_headers_and_deadlines(container_create_case, timeout, autoscale):
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
    """Options the Rust path cannot honor stop the create instead of quietly moving
    it to the legacy transport.

    Twenty calls are covered: ten unusable deadlines, a connect timeout, both raw
    hooks, an unknown keyword, four driver-owned headers, and two raw
    request-options dictionaries.

    Each raises ``NotImplementedError`` pointing at the legacy Python client.
    Nothing is created on either route, the hook does not run, and the fallback
    counter does not move -- a refusal is not a fallback, and counting it as one
    would make the metric useless for judging how much traffic the Rust engine
    actually turns away.
    """
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
    """A hook that reports itself as false still runs, and the headers it is handed
    are its own copy.

    Being callable is what makes something a hook, not being true, so a hook
    object that says it is false is still invoked exactly once.

    It is given the same properties the caller receives, so the two views agree.
    But the headers are a separate copy: the hook changes the request charge and
    neither the properties nor the client's own record of the last response
    headers moves. A hook meant for logging must not be able to rewrite what the
    customer sees.
    """
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
def test_container_create_invalid_conditions_fail_before_dispatch(container_create_case, kwargs, error_type):
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
def test_container_create_errors_never_replay(container_create_case, failure_source, error_type):
    """A failure, wherever it comes from, is raised as-is after exactly one attempt.

    The error is injected in two places -- the customer's hook, which runs after
    the container exists, and the engine itself -- and in four flavors: an
    ordinary error, a capability failure, a transport failure, and cancellation.

    In all eight combinations the same exception object reaches the caller, the
    engine ran once, and the legacy route was never tried. Retrying would risk
    creating the container twice, and a transport failure is exactly the case
    where the client cannot tell whether the first attempt was applied.

    Cancellation must also pass through unchanged, or it stops unwinding and the
    caller's request to stop is ignored. The fallback counter does not move,
    because an error is not the engine declining the work.
    """
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


@pytest.mark.parametrize("use_legacy", [False, True])
def test_container_get_or_create_still_creates_after_404(container_create_case, use_legacy):
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
    """Extend the create setup to cover both outcomes of get-or-create.

    Each test runs twice: once where the container already exists and once where
    it does not. Those are two genuinely different paths -- one request or two --
    and the method has to return the same shape either way.

    The existing container is deliberately given settings that differ from what
    the tests ask for: a different partition key path and a different time to
    live. That lets a test prove the existing definition is returned untouched
    rather than quietly overwritten with the caller's arguments.

    The missing case is staged as a not-found reply followed by a created reply,
    which is the real two-step sequence.
    """
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
    """Call ``create_container_if_not_exists`` with a fixed name and partition key."""
    return _call_container_create(
        case, "c1", PartitionKey(path="/pk"), method="create_container_if_not_exists", **kwargs
    )


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("return_properties", [False, True])
@pytest.mark.parametrize("positional_count", [0, 1, 2])
def test_container_get_or_create_preserves_shapes_and_existing_settings(
    container_get_or_create_case, use_legacy, return_properties, positional_count
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
            assert settings_options(op)["timeout_seconds"] == 10
            assert op.headers["x-company-trace"] == "setup"
        assert "offerThroughput" not in operations[0].headers
        if case.missing:
            assert json.loads(operations[1].body_bytes)["defaultTtl"] == 99
            assert operations[1].settings.resource.offer_throughput == 400


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": float("nan")}, {"timeout": float("inf")},
    {"timeout": 2**64}, {"timeout": "10"}, {"connection_timeout": 1},
    {"raw_request_hook": lambda request: None}, {"raw_response_hook": lambda response: None},
    {"initial_headers": {"User-Agent": "override"}}, {"unknown_option": None},
    {"populate_quota_info": True}, {"populate_partition_key_range_statistics": False},
    {"request_options": {Constants.ContainerRID: "rid1"}},
])
def test_container_get_or_create_preflights_both_steps(container_get_or_create_case, kwargs):
    """An option the Rust path cannot honor is caught before the first request, not
    between the two.

    Get-or-create can make two requests, so an option that only the create step
    would choke on has to be spotted up front. Otherwise the read goes out, the
    call then fails, and the customer has paid for a request that achieved
    nothing.

    Fourteen cases are covered, including two options that only apply to reads.
    Each raises ``NotImplementedError`` naming the method, with no request on
    either engine, no cache write, no hook, and no movement in the fallback
    counter.
    """
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
    """A malformed condition is rejected before the read, not after it.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. All three
    are caught before anything goes out, so a call that was never going to work
    does not cost a request or leave the cache holding properties from it.
    """
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
    """A valid condition is attached to every request the call makes, on both engines,
    without warning.

    All four forms are covered. What is specific to get-or-create is that the
    condition must ride on *both* steps when the container turns out to be
    missing -- the read and the create that follows. Dropping it from the second
    would leave the create unguarded, which is exactly the step where a
    concurrent caller may have created the container in between.
    """
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
            assert CaseInsensitiveDict(wire_headers(call.args[0]))[expected[0]] == expected[1]
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


@pytest.mark.parametrize("use_legacy", [False, True])
@pytest.mark.parametrize("status", [401, 403, 404, 409, 429, 500])
def test_container_get_or_create_propagates_failures_without_replay(
    container_get_or_create_case, use_legacy, status
):
    """A failure at either step reaches the caller with its status intact and is not
    retried.

    Six statuses are covered against both outcomes. Where the container exists
    the failure lands on the read; where it is missing it lands on the create
    that follows, so both steps are exercised.

    A genuine initial not-found is skipped in the existing case, because that is
    not a failure at all -- it is the signal to create, covered by its own test.

    Conflict is the one worth naming: if the create comes back saying the
    container already exists, that means somebody else created it in the moment
    between the read and the create. It is reported, not retried, and never
    quietly reinterpreted as success. The hook does not run and nothing is
    cached.
    """
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


@pytest.mark.parametrize("use_legacy", [False, True])
def test_container_get_or_create_preserves_bodyless_conditional_results(container_get_or_create_case, use_legacy):
    """A reply with no body is passed through as it is, not invented around.

    A condition can produce a success with nothing in it -- a not-modified reply
    to the read, or a create whose body the service left empty. The SDK does not
    fill in the gap.

    Where the container exists, the caller gets a working proxy, since the name
    was known from the arguments, together with genuinely empty properties, and
    no create is attempted. Where it was missing, the empty create reply has no
    name to build from and the call fails plainly on the missing key rather than
    returning a proxy pointing at nothing.

    In both cases the hook is called once and is handed the same empty
    properties, so it sees exactly what the caller sees.
    """
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
    """A customer who chose legacy on purpose keeps the transport options only legacy
    supports.

    A sub-second deadline and a connect timeout are refused on the Rust path, but
    here the customer has explicitly asked for legacy, so both are forwarded --
    to every request the call makes, not just the first. Dropping them would
    silently give a call a longer deadline than the one asked for.
    """
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
    options, remaining, eligible = prepare_container_get_or_create_read(
        kwargs, initial_headers=None, offer_throughput=400
    )
    assert eligible
    assert kwargs == original
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "*"}
    assert "offerThroughput" not in options
    assert remaining == {"timeout": 10}


# --- routing registration ------------------------------------------------


def test_create_container_is_a_single_response_operation():
    """One create, one reply: it is sent through ``execute``, not the paged path."""
    assert OP_TO_BINDING_FUNCTION_NAME[OP_CREATE_CONTAINER] == "create_container"
    assert OP_CREATE_CONTAINER not in STATELESS_PAGE_BINDING_FUNCTION_NAMES


def test_container_feeds_are_paged_operations():
    """Both feeds are sent through ``execute_pages``, never the single-reply path."""
    assert STATELESS_PAGE_BINDING_FUNCTION_NAMES[OP_LIST_CONTAINERS] == "list_containers"
    assert STATELESS_PAGE_BINDING_FUNCTION_NAMES[OP_QUERY_CONTAINERS] == "query_containers"
    assert OP_LIST_CONTAINERS not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_QUERY_CONTAINERS not in OP_TO_BINDING_FUNCTION_NAME


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
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert json.loads(prepared.body_bytes) == definition
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'
    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-custom": "value"}).items())
    assert settings_options(prepared)["timeout_seconds"] == 3.5


def test_create_container_prepared_drops_the_session_token():
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

    assert "initialHeaders" not in wire_headers(prepared)
    assert wire_headers(prepared)["x-ms-offer-throughput"] == '400'


def test_list_containers_sends_no_query_body():
    """A read feed has no SQL. The page adapter refuses a feed op that is not on its
    parameterless list, so leaving ``list_containers`` off it makes every
    ``list_containers`` call fail once it reaches the binding."""
    from azure.cosmos._backend.rust_backend import build_binding_request_from_page

    request = build_binding_request_from_page(
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
    from azure.cosmos._backend.rust_backend import build_binding_request_from_page

    request = build_binding_request_from_page(
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
    resource type except ``dbs``, which includes this one. The Rust path has no
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
    fires exactly once with the same shape as on the Rust path."""
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
    option-key translation on the Rust side."""
    path = base.GetPathFromLink("dbs/db1", _COLLECTION)
    prepared = build_list_containers_prepared_query(
        path=path,
        options={"initialHeaders": {"x-custom-tag": "value"}},
        req_headers={"x-custom-tag": "value"},
    )

    assert all(wire_headers(prepared).get(key.lower()) == str(value) for key, value in ({"x-custom-tag": "value"}).items())


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
    """Without a database name the Rust page has nothing to run against, so the call
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


# --- end-to-end feed routing --------------------------------------------
#
# The gates and builders above are only half of it. The other half is the
# routing inside the client connection that picks them: it tells a container
# feed apart from a database feed and an item feed by resource type alone, and a
# wrong arm there sends the call to the wrong binding entry point. These drive
# the real routing with a fake backend.


class _CapturingPagedBackend(CosmosBackend):
    """Records the paged request it was handed and yields one canned page."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body to yield and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    def execute_pages(self, prepared, *, deadline=None):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield BackendPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    def execute(self, prepared, *, deadline=None):
        """Fail immediately -- a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


class _CapturingAsyncPagedBackend(AsyncCosmosBackend):
    """Record the page request produced by asynchronous container methods."""

    def __init__(self, body: bytes) -> None:
        """Store the canned page body and a slot to capture the prepared request."""
        self.body = body
        self.prepared = None

    async def execute_pages(self, prepared, *, deadline=None):
        """Record the prepared query and yield one canned page."""
        self.prepared = prepared
        yield BackendPage(
            status_code=200,
            continuation=None,
            headers=CaseInsensitiveDict({"x-ms-request-charge": "2.0"}),
            body=self.body,
        )

    async def execute(self, prepared, *, deadline=None):
        """Fail immediately -- a paged backend must never be called through the single-reply path."""
        raise AssertionError("a feed must not dispatch through the single-reply path")


def _new_sync_connection() -> SyncConnection:
    """Build a minimal ``SyncConnection`` with no live transport, for routing tests."""
    conn = SyncConnection.__new__(SyncConnection)
    conn._response_state = ClientLastResponseHeaders()
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
    """Build a minimal ``AsyncConnection`` with no live transport, for routing tests."""
    conn = AsyncConnection.__new__(AsyncConnection)
    conn._response_state = ClientLastResponseHeaders()
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
    """The async routing is separate code with its own branch, so it can break alone."""
    async def _run():
        """Drive the async routing branch for a list feed so it can be verified independently."""
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
        """Drive the async routing for a query feed."""
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
    this read. Sending one on Rust only would be a difference between the two."""
    prepared = build_read_container_prepared(
        "dbs/db1/colls/c1",
        {"sessionToken": "0:1#22"},
    )

    assert "sessionToken" not in wire_headers(prepared)


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
# its request builder and its legacy call. The Rust-path tests above prove the
# request it builds; these prove the other branch -- that an option Rust cannot
# honor still reaches the legacy call, and that the hook fires exactly once with
# the response's own headers on that branch too. Without them the async legacy
# arm is the one code path in this family with no coverage at all.


def test_async_create_container_explicit_legacy_helper_preserves_read_timeout():
    """Explicit legacy helper selection keeps the timeout handling it passes through."""
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
