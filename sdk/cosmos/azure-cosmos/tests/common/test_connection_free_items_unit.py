# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks of item helpers with fake backends and response state.

Exercise prepared requests, selected option/error paths, hooks, and tracing
of specified Python preparation functions. The fake backend is the dispatch
boundary: these tests do not inspect transmitted bytes, native metadata
resolution, or every possible legacy call path.
"""
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
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults, ClientLastResponseHeaders
from azure.cosmos._helpers import _request_item
from azure.cosmos._helpers._item_operations import ItemHelper, build_item_request, normalize_item_arguments
from common.request_preparation import call_item_helper
from azure.cosmos._helpers._paths import parse_paths
from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper
from azure.cosmos.aio._helpers._item_operations import build_item_request as async_execute_item_builder
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue
from azure.cosmos._read_items_helper import ReadItemsHelperSync
from azure.cosmos.aio._read_items_helper_async import ReadItemsHelperAsync


def response(body=None, status=200, headers=None):
    """Build a reply in the shape the backend returns, with sensible parts filled in.

    Keeps each test to naming only the part it cares about -- a status, a tag, a
    body -- rather than restating the whole shape every time.
    """
    return BackendResponse(
        status_code=status, sub_status=0, headers=headers or {},
        body=json.dumps(body).encode() if body is not None else b"", diagnostics=None,
    )


class Backend(CosmosBackend):
    """A stand-in backend that records what it was asked to do instead of sending it.

    It implements the real backend interface, so anything above it runs
    unchanged. Every request and every container information lookup is appended
    to one list in the order it happened, which lets a test say not just what
    was sent but how many times and in what sequence -- the basis for most
    claims in this file.

    It is shared beyond this file; the request protocol and item dependency
    suites import it rather than writing their own.
    """

    name = "rust"

    def __init__(self):
        """Start with an empty record, ordinary container information, and a successful reply.

        A test that wants a failure replaces the container information with an
        error, which both lookups then raise, so one attribute covers failures
        on either side.
        """
        self.events = []
        self.metadata = ContainerMetadata("rid", ("/pk",), "Hash")
        self.reply = response({"id": "x"}, headers={"x-ms-request-charge": 2.5})

    def get_container_metadata(self, link):
        """Record that container information was asked for, then answer or fail.

        The record is what lets tests prove item operations never ask. It is
        written down as a plain marker, so a count of it in the list is a count
        of lookups.
        """
        self.events.append("metadata")
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.metadata

    def execute(self, prepared, *, deadline=None):
        """Record the prepared request itself and return the arranged reply.

        The whole request is kept, not a summary, so tests can inspect its
        headers, its settings, and its partition key afterwards.
        """
        self.events.append(prepared)
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.reply

    def run_operation(self, **kwargs):
        """Fail loudly if anything falls back to the older general-purpose entry point.

        That route exists for the legacy path. An item operation reaching it
        would still work, which is the problem -- it would quietly bypass
        everything this file checks, and the tests would keep passing.
        """
        raise AssertionError("Migration fallback entrypoint must not be used")


class AsyncBackend(AsyncCosmosBackend, Backend):
    """The same stand-in with awaitable entry points, recording into the same list.

    It reuses the sync behavior rather than repeating it, so both clients are
    measured by identical bookkeeping and a test written once means the same
    thing on each.
    """

    async def get_container_metadata(self, link):
        """Await-able container information lookup, recorded like the sync one."""
        return Backend.get_container_metadata(self, link)

    async def execute(self, prepared, *, deadline=None):
        """Await-able request, recorded like the sync one."""
        return Backend.execute(self, prepared, deadline=deadline)


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("client_options, expected_threshold", [
    ({}, 500),
    ({"availability_strategy": False}, 500),
    ({"availability_strategy": True}, 500),
    ({"availability_strategy": {}}, 500),
    ({"availability_strategy": {"threshold_ms": 20}}, 20),
])
def test_read_hedging_true_retains_client_threshold(
    monkeypatch, async_mode, client_options, expected_threshold,
):
    backend = AsyncBackend() if async_mode else Backend()
    module = "azure.cosmos.aio._cosmos_client" if async_mode else "azure.cosmos.cosmos_client"
    factory = ".make_async_backend" if async_mode else ".make_backend"
    monkeypatch.setattr(module + factory, lambda *args, **kwargs: backend)
    connection_type = __import__(
        "azure.cosmos.aio._cosmos_client_connection_async" if async_mode else
        "azure.cosmos._cosmos_client_connection", fromlist=["CosmosClientConnection"]
    ).CosmosClientConnection

    def initialize(connection, **kwargs):
        connection._response_state = kwargs["_response_state"]

    monkeypatch.setattr(connection_type, "__init__", initialize)
    client_options = deepcopy(client_options)
    client = (AsyncCosmosClient if async_mode else CosmosClient)(
        "https://example.documents.azure.com", "key", **client_options,
    )
    strategy = client_options.get("availability_strategy")
    if isinstance(strategy, dict):
        strategy["threshold_ms"] = 900
    orders = client.get_database_client("sales").get_container_client("orders")
    for requested, enabled, threshold in [
        (True, True, expected_threshold),
        (False, False, None),
        ({"threshold_ms": 40}, True, 40),
        (None, None, None),
    ]:
        result = orders.read_item("order-42", "customer-17", availability_strategy=requested)
        if async_mode:
            asyncio.run(result)
        hedging = backend.events[-1].settings.hedging
        if enabled is None:
            assert hedging is None
        else:
            assert (hedging.enabled, hedging.threshold_ms) == (enabled, threshold)
    result = orders.read_item("order-42", "customer-17")
    if async_mode:
        asyncio.run(result)
    assert backend.events[-1].settings.hedging is None


def invoke(helper, op, **kwargs):
    """Call any item operation with the minimum arguments that operation requires.

    The six operations differ in what they need: writes take a body, the others
    take an item id, three take a partition key, and patch takes a list of
    changes. Gathering that here lets a test loop over all six and vary only
    what it is actually studying.

    The result is awaited when needed, so one test body serves both clients.
    """
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
    """Priority and throughput bucket set on the client apply to every item call, and a
    per-call value overrides them.

    Four combinations run against all six operations on both clients: nothing
    given, both given, both given as nothing, and both written directly as
    headers.

    The third is the one that needs care. A priority of nothing and a bucket of
    zero both look like "not supplied" to a simple check, so the client defaults
    correctly apply -- but zero is also a value someone might mean, and the
    behavior should be deliberate rather than accidental.

    These settings decide what the account throttles first. Losing them means a
    customer's background work competes with their customer-facing traffic,
    which is visible only as latency under load.
    """
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
    """The one shared builder hands each operation exactly the arguments it takes, and
    returns the request untouched.

    Both clients use the same builder, which is checked first -- two copies
    would drift, and the drift would be one client sending a field the other
    does not.

    For each operation the full argument list is pinned. Writes get the prepared
    body and are told not to extract the partition key again, since it was
    already resolved; create additionally gets its indexing instruction; patch
    gets its changes as prepared bytes. Operations that name an item get the id.

    Passing an argument an operation does not take would fail loudly, but
    omitting one would not -- it would simply be left unset, and a customer's
    indexing instruction or response preference would go missing on that
    operation alone.
    """
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
    if op in ("read_item", "replace_item"):
        expected["item_self_link"] = None
    if op == "patch_item":
        expected.update(body_bytes=args["body_bytes"])
    builder.assert_called_once_with(**expected)
    assert result is prepared


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_standalone_item_execution(async_mode, op):
    """Each listed operation dispatches once to a fake backend on sync and async.

    Check the operation tag, partition-key representation, lack of a Python-
    stamped container-id header, response state, hook, and write-body settings.
    Native key extraction and service execution are outside this test.
    """
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
    BindingProtocolError("missing metadata"), BindingProtocolError("invalid rid"),
    BindingProtocolError("invalid partition key"),
    CosmosResourceNotFoundError(status_code=404, message="missing"), AttributeError("lookup failed"),
])
def test_native_preparation_failure_propagates_without_a_python_metadata_call(async_mode, metadata):
    """When the driver fails to resolve the container, the error comes straight back and
    Python does not go looking itself.

    Five failures are covered, from malformed information to a missing container
    to an unexpected internal error. Each surfaces unchanged, and exactly one
    request was attempted.

    Falling back to a lookup in Python on failure is the tempting repair and the
    wrong one. It would turn one failed call into two, double the cost of every
    outage, and replace a precise error with whatever the second attempt
    produced.
    """
    backend = AsyncBackend() if async_mode else Backend()
    backend.metadata = metadata
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend)
    with pytest.raises((BindingProtocolError, CosmosResourceNotFoundError, AttributeError)):
        invoke(helper, "create_item")
    assert len(backend.events) == 1
    assert backend.events[0].op == "create_item"


@pytest.mark.parametrize("async_mode", [False, True])
def test_options_defaults_errors_and_hooks(async_mode):
    """Check no-response override, listed patch rejections, and synthetic 404/304 hooks.

    The unsupported condition here is If-None-Match, not every access condition.
    Rejected calls leave the fake backend's event list empty.
    """
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
    """The two special partition key values work on a container with no connection at all.

    One means the item has no partition key; the other means its key is
    explicitly null. They are different on the wire and must stay different, and
    neither is a value the driver can infer.

    Historically these were interpreted by consulting the connection for how the
    container was defined. Here there is no connection, and the read still
    succeeds in a single request.
    """
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
    """Watch every function called during an item operation and prove none of them belongs
    to the legacy code.

    This is the central test of the file. All six operations run on both clients
    with Python recording each call as it happens, and the legacy request
    builders, the legacy connection, and the legacy item helpers must never
    appear. Exactly one request goes out and the result comes back.

    A recorder is used rather than reasoning about the code because the
    dependency it guards against is easy to reintroduce by accident -- one
    attribute read for a default or a container id is enough, and nothing about
    it looks wrong in review. It would only fail for customers whose container
    has no connection behind it.

    The container is even given properties of its own, so an implementation
    inclined to reach for a container id has one available. The request still
    carries no container id header.
    """
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
                "azure.cosmos._helpers._legacy_item_operations",
                "azure.cosmos.aio._helpers._legacy_item_operations",
            ) or (module == "azure.cosmos._helpers._item_arguments"
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
    """Repeated writes never fetch container information, and a failure before sending
    leaves the published headers alone.

    Two writes produce two requests and no lookups. Then the driver is made to
    fail while resolving the container, and the headers the client publishes are
    still the identical object from the last successful call.

    Clearing them would misrepresent what happened. A customer reading the
    charge or the tracking id after a failure would find nothing, or values
    belonging to a request that was never sent, and would report the wrong call
    to support.
    """
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
    """Passing a connection where the defaults belong is refused by name.

    That position used to take a connection. Code written against the older
    shape must fail immediately rather than have the object accepted and read
    for attributes it does not have -- which would produce a confusing failure
    somewhere inside the first call, or worse, defaults quietly read as absent.

    The message names the type that is expected, which is the whole fix.
    """
    with pytest.raises(TypeError, match="ItemClientDefaults"):
        helper_type(backend_type(), object())


@pytest.mark.parametrize("helper_type,backend_type", [(ItemHelper, Backend), (AsyncItemHelper, AsyncBackend)])
def test_rust_helper_rejects_invalid_response_state(helper_type, backend_type):
    """The place where response headers get published must be the real one.

    Anything else is refused at construction. This object is shared by the
    client and everything under it, and it is how a customer reads the charge
    and tracking id after a call.

    A stand-in accepted here would swallow every update, so headers would go
    nowhere and the customer would see whatever was there before -- values from
    an older call, indistinguishable from fresh ones.
    """
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
    """Check typed condition settings on requests captured by the fake backend.

    Despite the test name, no HTTP header rendering or transmission is observed.
    """
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
    """Half-specified conditions are refused before anything is sent, with exact messages.

    A version tag without a condition, either condition needing a tag without
    one, and an unrecognized condition are all caught. Nothing reaches the
    backend.

    The danger in letting these through is that a condition the code cannot make
    sense of tends to become no condition at all, and the write then happens
    unconditionally -- the precise outcome the customer was guarding against.

    Messages are compared exactly, since they are what a customer reads to find
    which half they forgot.
    """
    for helper_type, backend_type in ((ItemHelper, Backend), (AsyncItemHelper, AsyncBackend)):
        backend = backend_type()
        with pytest.raises(error) as caught:
            invoke(helper_type(backend), "read_item", **kwargs)
        assert str(caught.value) == message
        assert backend.events == []


def test_rust_option_prep_owns_copies_without_pipeline_bookkeeping():
    """Preparing options copies the caller's input, resolves conflicts in favor of the
    direct argument, and adds no internal bookkeeping.

    The caller passes the same thing two ways -- a priority in the options and
    another as an argument, an access condition in the options and header forms
    directly -- and the direct arguments win. Their original object is compared
    afterwards and is unchanged, and the prepared options are a separate object.

    The last two checks are about what is not there. The legacy pipeline wrote
    a start time into the options and carried a second bag of arguments for the
    wire. Neither appears here. Both were bookkeeping for a transport this path
    does not use, and leaving them would put values in the request that nothing
    reads but everything has to keep working around.
    """
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
    """Splitting a partition key path handles quoting and spacing the way the service
    does.

    Six cases: a plain path, a segment quoted with double or single quotes so it
    can contain a slash, an escaped quote inside a quoted segment, surrounding
    spaces, and the root path which has no segments at all.

    Quoting is the reason this is not a simple split. A field genuinely
    containing a slash is written in quotes, and splitting naively would turn
    one field into two -- so the value would be looked for in a place that does
    not exist, and items would land in the wrong partition.
    """
    assert parse_paths([path]) == expected


@pytest.mark.parametrize("path", ["no-leading-slash", '/"unterminated', '/"a"b'])
def test_shared_path_tokenization_rejects_invalid_paths(path):
    """A path that cannot be read is refused, with the position of the problem.

    Three cases: no leading slash, a quote that is never closed, and text
    immediately after a closing quote. Each is ambiguous rather than merely
    unusual, so guessing would mean choosing a partition key path the customer
    did not write.

    The message gives the index, which is the only practical way to find the
    mistake in a long path.
    """
    with pytest.raises(ValueError, match="Invalid path character at index"):
        parse_paths([path])


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("compact_utf8", [False, True])
def test_public_context_and_compatibility_bridge(monkeypatch, async_mode, compact_utf8):
    """The client builds one context, shares it all the way down, and keeps the legacy
    headers view working without letting defaults leak back.

    One context is created, holding the backend and the client's defaults, and
    the same object reaches the database and the container -- so a setting given
    once at the client applies everywhere, rather than being rebuilt and
    possibly differing.

    The connection's policy object is replaced with one that fails if its
    response preference is read, and a create still succeeds using the client's
    own default. That is the leak this guards against: reading defaults from the
    connection would work on clients that have one and quietly differ on those
    that do not.

    The legacy headers attribute still works in both directions -- reading it
    gives the same object the new context publishes to, and assigning to it is
    seen by the context -- so existing code that inspects headers after a call
    keeps working.

    Finally the defaults refuse to be modified, since they are shared by every
    container in the program and an edit in one place would silently change all
    of them.
    """
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
    """A container built directly from a connection keeps working on the legacy path, and
    refuses to use a Rust backend it was never given a context for.

    Building a container straight from a connection is not supported but people
    do it, so it still works: the legacy call is made and the item comes back,
    whether the container was made directly or through a database.

    Then the same connection is given a Rust backend, and the read refuses with
    a message saying the context has to come from the client. Nothing is sent
    either way.

    Refusing is better than improvising a context. One invented here would carry
    default settings rather than the customer's -- no priority, the wrong
    response preference -- and would publish headers somewhere the client never
    reads, so the call would appear to work while quietly ignoring the client's
    configuration.
    """
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
    """Reading many items falls back to single reads, and that fallback follows the same
    rule as every other item call.

    Without a context it refuses, even though a Rust backend is sitting on the
    connection where it could be found. Taking it from there is exactly the
    shortcut this forbids -- it would work, and it would bypass the client's
    defaults and its published headers.

    With a context supplied, that context wins over unrelated state on the
    connection, and the read goes through it, with its headers recorded where
    the context publishes them.

    This path is easy to overlook because it is a helper rather than a container
    method, and it is where a customer reading a batch of items would be
    affected.
    """
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
    """A container told explicitly to use the legacy backend still makes the old call,
    container id and all.

    All six operations on both clients go to the matching legacy method, return
    its result, and carry the container id taken from the connection's own
    store.

    This is the deliberate opposite of the rest of the file. The legacy path is
    kept whole rather than partly modernized, so customers who need it get the
    behavior they had, and the choice between the two paths stays a single
    visible decision rather than a mixture that differs per operation.
    """
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
