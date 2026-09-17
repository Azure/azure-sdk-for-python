# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Point operations must work without constructing or receiving a legacy connection."""
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
import asyncio
import inspect
import json
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, CosmosDict, DatabaseProxy
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient, DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._backend.contracts import BackendResponse, ContainerMetadata, PreparedRequest
from azure.cosmos._backend.errors import BackendProtocolError
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults, ClientLastResponseHeaders
from azure.cosmos._helpers import _request_item
from azure.cosmos._helpers.item_helper import ItemHelper, build_item_request, normalize_item_arguments
from common.request_preparation import call_item_helper
from azure.cosmos._helpers._paths import parse_paths
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper
from azure.cosmos.aio._helpers.item_helper import build_item_request as async_execute_item_builder
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue
from azure.cosmos._read_items_helper import ReadItemsHelperSync
from azure.cosmos.aio._read_items_helper_async import ReadItemsHelperAsync


def response(body=None, status=200, headers=None):
    return BackendResponse(
        status_code=status, sub_status=0, headers=headers or {},
        body=json.dumps(body).encode() if body is not None else b"", diagnostics=None,
    )


class Backend(CosmosBackend):
    name = "rust"

    def __init__(self):
        self.events = []
        self.metadata = ContainerMetadata("rid", ("/pk",), "Hash")
        self.reply = response({"id": "x"}, headers={"x-ms-request-charge": 2.5})

    def get_container_metadata(self, link):
        self.events.append("metadata")
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.metadata

    def execute(self, prepared, *, deadline=None):
        self.events.append(prepared)
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.reply

    def run_operation(self, **kwargs):
        raise AssertionError("Migration fallback entrypoint must not be used")


class AsyncBackend(AsyncCosmosBackend, Backend):
    async def get_container_metadata(self, link):
        return Backend.get_container_metadata(self, link)

    async def execute(self, prepared, *, deadline=None):
        return Backend.execute(self, prepared, deadline=deadline)


def invoke(helper, op, **kwargs):
    arguments = {"container_link": "dbs/d/colls/c"}
    if op in ("create_item", "upsert_item", "replace_item"):
        arguments["body"] = {"id": "x", "pk": "p"}
    if op not in ("create_item", "upsert_item"):
        arguments.update(item_id="x")
    if op in ("read_item", "delete_item", "patch_item"):
        arguments["request_options"] = {"partitionKey": "p"}
    if op == "patch_item":
        arguments["patch_operations"] = [{"op": "add", "path": "/a", "value": 1}]
    arguments.update(kwargs)
    result = call_item_helper(helper, op, **arguments)
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
@pytest.mark.parametrize("kwargs,priority,bucket", [
    ({}, "Low", 3),
    ({"priority": "High", "throughput_bucket": 5}, "High", 5),
    ({"priority": None, "throughput_bucket": 0}, "Low", 3),
    ({"initial_headers": {"x-ms-cosmos-priority-level": "High",
                         "x-ms-cosmos-throughput-bucket": "7"}}, "High", "7"),
])
def test_independent_items_inherit_client_defaults(async_mode, op, kwargs, priority, bucket):
    backend = AsyncBackend() if async_mode else Backend()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(
        backend, ItemClientDefaults(priority="Low", throughput_bucket=3)
    )
    invoke(helper, op, **kwargs)
    request = backend.events[-1]
    headers = wire_headers(request)
    initial = headers.get("initialHeaders", headers)
    assert headers.get("x-ms-cosmos-priority-level", initial.get("x-ms-cosmos-priority-level")) == priority
    assert headers.get("x-ms-cosmos-throughput-bucket", initial.get("x-ms-cosmos-throughput-bucket")) == str(bucket)


@pytest.mark.parametrize("op", [
    "create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item",
])
def test_execute_item_builder_maps_arguments_and_returns_only_request(monkeypatch, op):
    assert async_execute_item_builder is build_item_request
    body = {"id": "order-42", "customerId": "customer-17", "total": 125.50}
    args, options = normalize_item_arguments(op, {
        "container_link": "dbs/Contoso/colls/Orders",
        "body": body,
        "item_id": "order-42",
        "patch_operations": [{"op": "replace", "path": "/total", "value": 150}],
        "no_response": True,
        "enable_automatic_id_generation": True,
        "request_options": {"partitionKey": "customer-17"},
    })
    prepared = PreparedRequest(op, args["container_link"], b"", key_from_legacy_header('["customer-17"]'))
    builder = MagicMock(return_value=prepared)
    monkeypatch.setattr(_request_item, f"build_{op}_request", builder)

    result = build_item_request(op, args, options, ItemClientDefaults(False))

    expected = {
        "container_link": args["container_link"],
        "partition_key_value": "customer-17",
        "container_rid": None,
        "request_options": options,
    }
    if op in ("create_item", "upsert_item", "replace_item"):
        expected["extract_partition_key"] = False
    if op in ("create_item", "upsert_item", "replace_item"):
        expected["document"] = args["document"]
    if op in ("create_item", "upsert_item", "replace_item", "patch_item"):
        expected["no_response_on_write_default"] = False
    if op not in ("create_item", "upsert_item"):
        expected["item_id"] = "order-42"
    if op == "create_item":
        expected.update(indexing_directive=None)
    if op == "patch_item":
        expected.update(body_bytes=args["body_bytes"])
    builder.assert_called_once_with(**expected)
    assert result is prepared


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_standalone_item_execution(async_mode, op):
    backend = AsyncBackend() if async_mode else Backend()
    state = ClientLastResponseHeaders()
    hook = MagicMock()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend, ItemClientDefaults(True), state)
    result = invoke(helper, op, response_hook=hook)
    assert len(backend.events) == 1
    request = backend.events[0]
    assert request.op == op
    assert legacy_partition_key_from_request(request) == (None if op in ("create_item", "upsert_item", "replace_item") else '["p"]')
    assert "x-ms-cosmos-intended-collection-rid" not in wire_headers(request)
    hook.assert_called_once()
    assert state.last_response_headers["x-ms-request-charge"] == "2.5"
    if op == "delete_item":
        assert result is None
    else:
        assert isinstance(result, CosmosDict)
        assert result.get_response_headers() == state.last_response_headers
    if op in ("create_item", "upsert_item", "replace_item", "patch_item"):
        assert settings_options(request)["responsePayloadOnWriteDisabled"] is True


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("metadata", [
    BackendProtocolError("missing metadata"), BackendProtocolError("invalid rid"),
    BackendProtocolError("invalid partition key"),
    CosmosResourceNotFoundError(status_code=404, message="missing"), AttributeError("lookup failed"),
])
def test_native_preparation_failure_propagates_without_a_python_metadata_call(async_mode, metadata):
    backend = AsyncBackend() if async_mode else Backend()
    backend.metadata = metadata
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend)
    with pytest.raises((BackendProtocolError, CosmosResourceNotFoundError, AttributeError)):
        invoke(helper, "create_item")
    assert len(backend.events) == 1
    assert backend.events[0].op == "create_item"


@pytest.mark.parametrize("async_mode", [False, True])
def test_options_defaults_errors_and_hooks(async_mode):
    backend = AsyncBackend() if async_mode else Backend()
    helper_type = AsyncItemHelper if async_mode else ItemHelper
    state = ClientLastResponseHeaders()
    helper = helper_type(backend, ItemClientDefaults(True), state)
    invoke(helper, "create_item", no_response=False)
    assert settings_options(backend.events[-1])["responsePayloadOnWriteDisabled"] is False
    backend.events.clear()
    for kwargs in ({"filter_predicate": "FROM c WHERE c.x = 1"}, {"read_timeout": 2},
                   {"retry_write": 1}, {"raw_request_hook": MagicMock()}, {"raw_response_hook": MagicMock()},
                   {"initial_headers": {"User-Agent": "caller"}},
                   {"access_condition": {"type": "IfNoneMatch", "condition": '"e"'}}):
        with pytest.raises(NotImplementedError):
            invoke(helper, "patch_item", **kwargs)
    with pytest.raises(ValueError, match="timeout"):
        invoke(helper, "patch_item", timeout=0.5)
    assert not backend.events
    backend.reply = response({"message": "gone"}, 404, {"etag": "error"})
    hook = MagicMock()
    with pytest.raises(CosmosResourceNotFoundError):
        invoke(helper_type(backend, response_state=state), "read_item", response_hook=hook)
    hook.assert_not_called()
    assert state.last_response_headers["etag"] == "error"
    backend.reply = response(status=304, headers={"etag": "current"})
    result = invoke(helper_type(backend), "read_item", response_hook=hook)
    assert result == {}
    hook.assert_called_once()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("key", [NonePartitionKeyValue, NullPartitionKeyValue])
def test_public_item_sentinels_do_not_read_connection(async_mode, key):
    backend = AsyncBackend() if async_mode else Backend()
    context = ItemClientContext(backend)
    proxy_type = AsyncContainerProxy if async_mode else ContainerProxy
    proxy = proxy_type(None, "dbs/d", "c", _item_context=context)
    result = proxy.read_item("x", partition_key=key)
    if async_mode:
        result = asyncio.run(result)
    assert result["id"] == "x"
    assert len(backend.events) == 1


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_all_public_point_methods_work_with_no_connection(async_mode, op):
    backend = AsyncBackend() if async_mode else Backend()
    proxy_type = AsyncContainerProxy if async_mode else ContainerProxy
    proxy = proxy_type(
        None, "dbs/d", "c", properties={"_rid": "python-properties"},
        _item_context=ItemClientContext(backend),
    )
    arguments = {}
    if op in ("create_item", "upsert_item", "replace_item"):
        arguments["body"] = {"id": "x", "pk": "p"}
    if op not in ("create_item", "upsert_item"):
        arguments["item"] = "x"
    if op in ("read_item", "delete_item", "patch_item"):
        arguments["partition_key"] = "p"
    if op == "patch_item":
        arguments["patch_operations"] = [{"op": "add", "path": "/a", "value": 1}]
    legacy_calls = []
    previous_profile = sys.getprofile()

    def record_legacy_calls(frame, event, arg):
        if event == "call":
            module = frame.f_globals.get("__name__", "")
            if module in (
                "azure.cosmos._base",
                "azure.cosmos._cosmos_client_connection",
                "azure.cosmos.aio._cosmos_client_connection_async",
                "azure.cosmos._helpers.legacy_item_helper",
                "azure.cosmos.aio._helpers.legacy_item_helper",
            ) or (module == "azure.cosmos._helpers._item_dispatch"
                  and frame.f_code.co_name.startswith("build_")):
                legacy_calls.append((module, frame.f_code.co_name))

    sys.setprofile(record_legacy_calls)
    try:
        result = getattr(proxy, op)(**arguments)
        if async_mode:
            result = asyncio.run(result)
    finally:
        sys.setprofile(previous_profile)
    assert legacy_calls == []
    assert len(backend.events) == 1
    assert backend.events[0].op == op
    assert "x-ms-cosmos-intended-collection-rid" not in backend.events[0].headers
    assert result is None if op == "delete_item" else result["id"] == "x"


@pytest.mark.parametrize("async_mode", [False, True])
def test_no_python_metadata_calls_and_preparation_error_preserves_headers(async_mode):
    backend = AsyncBackend() if async_mode else Backend()
    state = ClientLastResponseHeaders()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend, response_state=state)
    invoke(helper, "create_item")
    invoke(helper, "upsert_item")
    assert backend.events.count("metadata") == 0
    assert len(backend.events) == 2
    previous = state.last_response_headers
    backend.metadata = CosmosResourceNotFoundError(status_code=404, message="missing")
    with pytest.raises(CosmosResourceNotFoundError):
        invoke(helper, "read_item")
    assert state.last_response_headers is previous


@pytest.mark.parametrize("helper_type,backend_type", [(ItemHelper, Backend), (AsyncItemHelper, AsyncBackend)])
def test_rust_helper_rejects_old_connection_argument(helper_type, backend_type):
    with pytest.raises(TypeError, match="ItemClientDefaults"):
        helper_type(backend_type(), object())


@pytest.mark.parametrize("helper_type,backend_type", [(ItemHelper, Backend), (AsyncItemHelper, AsyncBackend)])
def test_rust_helper_rejects_invalid_response_state(helper_type, backend_type):
    with pytest.raises(TypeError, match="response_state must be ClientLastResponseHeaders"):
        helper_type(backend_type(), response_state=object())


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["read_item", "delete_item", "upsert_item", "replace_item"])
@pytest.mark.parametrize("condition,etag,header,value", [
    (MatchConditions.IfNotModified, '"v"', "If-Match", '"v"'),
    (MatchConditions.IfModified, '"v"', "If-None-Match", '"v"'),
    (MatchConditions.IfPresent, None, "If-Match", "*"),
    (MatchConditions.IfMissing, None, "If-None-Match", "*"),
])
def test_rust_owned_condition_options_reach_wire(async_mode, op, condition, etag, header, value):
    backend = AsyncBackend() if async_mode else Backend()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend)
    invoke(helper, op, match_condition=condition, etag=etag)
    assert getattr(backend.events[-1].settings.item, header.lower().replace("-", "_")) == value


@pytest.mark.parametrize("kwargs,error,message", [
    ({"etag": "v"}, ValueError, "'etag' specified without 'match_condition'."),
    ({"match_condition": MatchConditions.IfModified}, ValueError, "'match_condition' specified without 'etag'."),
    ({"match_condition": MatchConditions.IfNotModified}, ValueError, "'match_condition' specified without 'etag'."),
    ({"match_condition": "invalid"}, TypeError, "Invalid match condition: invalid"),
])
def test_condition_validation_precedes_metadata(kwargs, error, message):
    for helper_type, backend_type in ((ItemHelper, Backend), (AsyncItemHelper, AsyncBackend)):
        backend = backend_type()
        with pytest.raises(error) as caught:
            invoke(helper_type(backend), "read_item", **kwargs)
        assert str(caught.value) == message
        assert backend.events == []


def test_rust_option_prep_owns_copies_without_pipeline_bookkeeping():
    arguments = {
        "container_link": "dbs/d/colls/c",
        "item_id": "x",
        "request_options": {
            "partitionKey": "p", "priorityLevel": "Low",
            "accessCondition": {"type": "IfMatch", "condition": "old"},
        },
        "priority": "High",
        "if_match": "direct",
        "if_none_match": "winner",
        "initial_headers": {"x-ms-custom": "value"},
        "timeout": 2,
    }
    original = deepcopy(arguments)
    args, options = normalize_item_arguments("read_item", arguments)
    assert arguments == original
    assert options is not arguments["request_options"]
    assert options["priorityLevel"] == "High"
    assert options["accessCondition"] == {"type": "IfNoneMatch", "condition": "winner"}
    assert Constants.OperationStartTime not in options
    assert "wire_kwargs" not in args
    assert args["kwargs"]["timeout"] == 2


@pytest.mark.parametrize("path,expected", [
    ("/a/b", ["a", "b"]),
    ('/"a/b"/c', ["a/b", "c"]),
    ("/'a/b'/c", ["a/b", "c"]),
    (r'/"a\"b"/c', [r'a\"b', "c"]),
    ("/ a / b /", ["a", "b"]),
    ("/", []),
])
def test_shared_path_tokenization(path, expected):
    assert parse_paths([path]) == expected


@pytest.mark.parametrize("path", ["no-leading-slash", '/"unterminated', '/"a"b'])
def test_shared_path_tokenization_rejects_invalid_paths(path):
    with pytest.raises(ValueError, match="Invalid path character at index"):
        parse_paths([path])


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("compact_utf8", [False, True])
def test_public_context_and_compatibility_bridge(monkeypatch, async_mode, compact_utf8):
    backend = AsyncBackend() if async_mode else Backend()
    module = "azure.cosmos.aio._cosmos_client" if async_mode else "azure.cosmos.cosmos_client"
    monkeypatch.setattr(module + (".make_async_backend" if async_mode else ".make_backend"), lambda *a, **kw: backend)
    created_contexts = []

    def create_context(*args, **kwargs):
        context = ItemClientContext(*args, **kwargs)
        created_contexts.append(context)
        return context

    monkeypatch.setattr(module + ".ItemClientContext", create_context)
    # Bypass transport initialization only; exercise the real connection's header property.
    connection_type = __import__(
        "azure.cosmos.aio._cosmos_client_connection_async" if async_mode else
        "azure.cosmos._cosmos_client_connection", fromlist=["CosmosClientConnection"]
    ).CosmosClientConnection

    def initialize(connection, **kwargs):
        assert len(created_contexts) == 1
        assert created_contexts[0].backend is backend
        assert created_contexts[0].defaults.no_response_on_write is True
        assert created_contexts[0].defaults.enable_compact_utf8_item_writes is compact_utf8
        assert kwargs["enable_compact_utf8_item_writes"] is compact_utf8
        assert kwargs["_response_state"] is created_contexts[0].response_state
        connection._response_state = kwargs["_response_state"]

    monkeypatch.setattr(connection_type, "__init__", initialize)
    client = (AsyncCosmosClient if async_mode else CosmosClient)(
        "https://example.documents.azure.com", "key", no_response_on_write=True,
        enable_compact_utf8_item_writes=compact_utf8,
    )
    database = client.get_database_client("d")
    container = database.get_container_client("c")
    assert container._item_context is database._item_context is client._item_context
    connection = client.client_connection
    connection._backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND

    class ForbiddenPolicy:
        @property
        def ResponsePayloadOnWriteDisabled(self):
            raise AssertionError("Rust must not copy defaults from the connection")

    connection.connection_policy = ForbiddenPolicy()
    hook = MagicMock(side_effect=lambda h, b: backend.events.append("hook"))
    result = container.create_item({"id": "x", "pk": "p"}, response_hook=hook)
    if async_mode:
        result = asyncio.run(result)
    assert result["id"] == "x"
    assert settings_options(backend.events[-2])["responsePayloadOnWriteDisabled"] is True
    assert backend.events[-1] == "hook"
    assert connection.last_response_headers is client._item_context.response_state.last_response_headers
    connection.last_response_headers = {"legacy": "headers"}
    assert client._item_context.response_state.last_response_headers == {"legacy": "headers"}
    with pytest.raises(FrozenInstanceError):
        client._item_context.defaults.no_response_on_write = False


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("via_database", [False, True])
def test_direct_proxy_compatibility_is_explicit_legacy_only(async_mode, via_database):
    connection = MagicMock()
    connection._backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND
    connection._container_properties_cache = {
        "dbs/d/colls/c": {"_rid": "legacy-rid", "partitionKey": {"paths": ["/pk"], "kind": "Hash"}}
    }
    call = AsyncMock(return_value={"id": "x"}) if async_mode else MagicMock(return_value={"id": "x"})
    connection.ReadItem = call
    if via_database:
        database = (AsyncDatabaseProxy if async_mode else DatabaseProxy)(connection, "d")
        container = database.get_container_client("c")
    else:
        container = (AsyncContainerProxy if async_mode else ContainerProxy)(connection, "dbs/d", "c")
    assert container._item_context is None
    result = container.read_item("x", partition_key=NonePartitionKeyValue)
    if async_mode:
        result = asyncio.run(result)
    assert result["id"] == "x"
    call.assert_called_once()
    backend = AsyncBackend() if async_mode else Backend()
    connection._backend = backend
    call.reset_mock()
    with pytest.raises(RuntimeError, match="context supplied by CosmosClient"):
        result = container.read_item("x", partition_key=NonePartitionKeyValue)
        if async_mode:
            asyncio.run(result)
    assert backend.events == []
    call.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("with_context", [False, True])
def test_read_many_point_leg_never_recovers_rust_backend(async_mode, with_context):
    backend = AsyncBackend() if async_mode else Backend()
    connection = MagicMock()
    connection._backend = backend
    context = ItemClientContext(backend) if with_context else None
    helper = (ReadItemsHelperAsync if async_mode else ReadItemsHelperSync)(
        connection, "dbs/d/colls/c", [("x", "p")], {}, {"paths": ["/pk"], "kind": "Hash"},
        _item_context=context,
    )
    if not with_context:
        with pytest.raises(RuntimeError, match="context supplied by CosmosClient"):
            result = helper._execute_point_read("x", "p", {})
            if async_mode:
                asyncio.run(result)
        assert backend.events == []
        return
    # The independently supplied context wins over unrelated connection state.
    connection._backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND
    result = helper._execute_point_read("x", "p", {})
    if async_mode:
        result = asyncio.run(result)
    item, headers = result
    assert item["id"] == "x"
    assert headers == context.response_state.last_response_headers
    assert backend.events[-1].op == "read_item"


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op,method", [("create_item", "CreateItem"), ("read_item", "ReadItem"),
                                     ("delete_item", "DeleteItem"), ("upsert_item", "UpsertItem"),
                                     ("replace_item", "ReplaceItem"), ("patch_item", "PatchItem")])
def test_explicit_parity_adapter_keeps_legacy_call(async_mode, op, method):
    connection = MagicMock()
    connection._container_properties_cache = {"dbs/d/colls/c": {"_rid": "legacy-rid"}}
    call = AsyncMock(return_value={"legacy": True}) if async_mode else MagicMock(return_value={"legacy": True})
    setattr(connection, method, call)
    context = ItemClientContext(ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND)
    proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(connection, "dbs/d", "c", _item_context=context)
    helper = proxy._get_item_helper()
    result = invoke(helper, op, **({"filter_predicate": "FROM c"} if op == "patch_item" else {}))
    assert result == {"legacy": True}
    assert call.call_args.kwargs["options"][Constants.ContainerRID] == "legacy-rid"
