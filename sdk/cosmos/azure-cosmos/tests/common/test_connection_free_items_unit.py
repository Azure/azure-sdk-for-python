# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for item operations, using a fake sender instead of a real service.

An item operation is one of create_item, read_item, replace_item, upsert_item,
delete_item and patch_item. Before sending, the SDK turns the call's arguments
into a prepared request: an object that holds the operation name, the
container, the partition key, the body and the request settings.

These tests replace the part of the SDK that sends requests with a fake sender.
The fake sender records each prepared request instead of sending it, so a test
can check what would have been sent. Nothing here contacts a Cosmos DB account.

Terms used in this file:

- item helper: the SDK object (``ItemHelper``, or ``AsyncItemHelper`` for the
  async client) that prepares and sends item operations.
- client defaults: settings given once on ``CosmosClient``, such as
  ``priority``, ``throughput_bucket`` and ``no_response_on_write``. Every item
  operation uses them unless the call gives its own value.
- container details: the container's internal id and partition key
  definition. Item operations must not look these up before sending.
- hedging: the ``availability_strategy`` option. When it is on, a request that
  is slow in one region may also be sent to another region after waiting
  ``threshold_ms`` milliseconds.
- last response headers: the headers of the most recent reply. The client
  keeps them so a caller can read values such as the request charge after a
  call.
- connection: the client's internal connection object (``client_connection``).
  Item operations get what they need from the client, so they must work even
  when a container object has no connection.
- client context: the object (``CosmosClientContext``) that the client creates
  once. It holds the sender, the client defaults and the last response
  headers. Database and container objects share it.
"""
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
import asyncio
import inspect
import json
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, CosmosDict
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._backend.contracts import BackendResponse, ContainerMetadata, PreparedRequest
from azure.cosmos._backend.errors import BindingProtocolError
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._helpers._client_context import (
    CosmosClientContext, ClientOperationDefaults, ClientLastResponseHeaders,
)
from azure.cosmos._helpers import _item_arguments, _request_item
from azure.cosmos._helpers._item_operations import ItemHelper, build_item_request, normalize_item_arguments
from common.request_preparation import call_item_helper
from azure.cosmos._helpers._paths import parse_paths
from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper
from azure.cosmos.aio._helpers._item_operations import build_item_request as async_build_item_request
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue


def fake_reply(body=None, status=200, headers=None):
    """Build a reply that gives only the parts a test cares about.

    A reply has a status code, a sub-status, headers, a body and diagnostics. The
    body is given as a Python value and turned into JSON bytes. The status code
    defaults to 200.
    """
    return BackendResponse(
        status_code=status, sub_status=0, headers=headers or {},
        body=json.dumps(body).encode() if body is not None else b"", diagnostics=None,
    )


class FakeSender(CosmosBackend):
    """Fake sender that records requests instead of sending them.

    It has the same methods as the SDK's sender (``CosmosBackend``), so the code
    that calls it runs unchanged. Every prepared request and every container
    details lookup is added to one list, ``events``, in the order it happened. A
    test can then check what was sent, how many times, and in what order.

    Other test files import this class and ``invoke``.
    """

    name = "rust"

    def __init__(self):
        """Start with an empty ``events`` list, normal container details, and a successful reply.

        To make a call fail, set ``metadata`` to an exception.
        ``get_container_metadata`` then raises it, and ``execute`` records the
        request first and then raises it.
        """
        self.events = []
        self.metadata = ContainerMetadata("rid", ("/pk",), "Hash")
        self.reply = fake_reply({"id": "x"}, headers={"x-ms-request-charge": 2.5})

    def get_container_metadata(self, link):
        """Record a container details lookup, then return the details or raise.

        The lookup is recorded as the string ``"metadata"``, so a test can count
        lookups with ``events.count("metadata")``.
        """
        self.events.append("metadata")
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.metadata

    def execute(self, prepared, *, deadline=None):
        """Record the whole prepared request and return the planned reply.

        The full request is kept, so a test can check its headers, settings and
        partition key.
        """
        self.events.append(prepared)
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.reply

    def run_operation(self, **kwargs):
        """Fail the test if this method is used.

        Item operations must call ``execute`` directly, not this more general method.
        """
        raise AssertionError("Item operations must call execute, not run_operation")


class AsyncFakeSender(AsyncCosmosBackend, FakeSender):
    """Async version of ``FakeSender``.

    It reuses the sync methods and records into the same ``events`` list, so a
    test written once checks both clients the same way.
    """

    name = "rust"

    async def get_container_metadata(self, link):
        """Async version of the sync container details lookup."""
        return FakeSender.get_container_metadata(self, link)

    async def execute(self, prepared, *, deadline=None):
        """Async version of the sync ``execute``."""
        return FakeSender.execute(self, prepared, deadline=deadline)


@pytest.fixture(
    name="merge_item_kwargs",
    params=[
        _item_arguments.merge_create_item_explicit_kwargs,
        _item_arguments.merge_delete_item_explicit_kwargs,
        _item_arguments.merge_read_item_explicit_kwargs,
        _item_arguments.merge_upsert_replace_item_kwargs,
        _item_arguments.merge_patch_item_explicit_kwargs,
    ],
    ids=["create", "delete", "read", "upsert-replace", "patch"],
)
def explicit_item_merger(request):
    """One of the five functions that copy an item method's keyword arguments into the request options.

    upsert and replace share one function.
    """
    return request.param


def test_keyword_merge_skips_none_and_keeps_false_and_zero_rust(merge_item_kwargs):
    """A keyword set to None leaves the earlier value alone. False, 0 and "" replace it.

    None means "not given", so the value already in the options stays. False, 0
    and the empty string are real choices and must be copied, even though they
    look empty. ``retry_write`` is checked only for write operations, because
    ``read_item`` does not take it.
    """
    hook = object()
    options = {
        "post_trigger_include": "keep",
        "session_token": "old",
        "priority": "Low",
        "availability_strategy": True,
        "response_hook": hook,
    }
    call_keywords = {
        "post_trigger_include": None,
        "session_token": "",
        "priority": None,
        "throughput_bucket": 0,
        "availability_strategy": False,
        "response_hook": None,
    }
    expected = {
        "post_trigger_include": "keep",
        "session_token": "",
        "priority": "Low",
        "availability_strategy": False,
        "response_hook": hook,
        "throughput_bucket": 0,
    }
    if merge_item_kwargs is not _item_arguments.merge_read_item_explicit_kwargs:
        options[Constants.Kwargs.RETRY_WRITE] = 3
        call_keywords["retry_write"] = 0
        expected[Constants.Kwargs.RETRY_WRITE] = 0
    merge_item_kwargs(options, **call_keywords)
    assert options == expected


def test_keyword_merge_converts_hedging_dict_without_changing_it_rust(merge_item_kwargs):
    """A hedging dict becomes a hedging setting, and the caller's dict is not changed.

    The options get an object whose ``threshold_ms`` is 25, while the dict the
    caller passed still equals ``{"threshold_ms": 25}``. The response hook is
    copied as it is.
    """
    caller_strategy = {"threshold_ms": 25}
    hook = object()
    options = {}
    merge_item_kwargs(options, availability_strategy=caller_strategy, response_hook=hook)
    assert options["availability_strategy"].threshold_ms == 25
    assert caller_strategy == {"threshold_ms": 25}
    assert options["response_hook"] is hook


def test_keyword_merge_stops_at_invalid_hedging_value_rust(merge_item_kwargs):
    """An invalid hedging value raises ValueError and stops the copy at that point.

    Keywords are copied one at a time in a fixed order. ``priority`` and
    ``throughput_bucket`` come before ``availability_strategy``, so they are
    copied. ``response_hook`` comes after it, so the earlier hook stays. The
    earlier ``availability_strategy`` value also stays.
    """
    hook = object()
    options = {"availability_strategy": False, "response_hook": hook}
    with pytest.raises(ValueError, match="threshold_ms must be positive"):
        merge_item_kwargs(
            options,
            priority="High",
            throughput_bucket=0,
            availability_strategy={"threshold_ms": 0},
            response_hook=object(),
        )
    assert options == {
        "availability_strategy": False,
        "response_hook": hook,
        "priority": "High",
        "throughput_bucket": 0,
    }


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("client_options, expected_threshold", [
    ({}, 500),
    ({"availability_strategy": False}, 500),
    ({"availability_strategy": True}, 500),
    ({"availability_strategy": {}}, 500),
    ({"availability_strategy": {"threshold_ms": 20}}, 20),
])
def test_read_item_hedging_true_uses_client_threshold_rust(
    monkeypatch, async_mode, client_options, expected_threshold,
):
    """``availability_strategy=True`` on read_item uses the client's hedging wait time.

    If the client was given a ``threshold_ms``, True uses it. Otherwise True uses
    the default of 500 milliseconds. False turns hedging off for that read. A dict
    uses its own ``threshold_ms``. None, or leaving the keyword out, adds no
    hedging setting to the request.

    The test also changes the client's dict after the client is created. The
    client keeps the value it had at creation, so the change has no effect.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    client_options = deepcopy(client_options)
    client = (AsyncCosmosClient if async_mode else CosmosClient)(
        "https://example.documents.azure.com", "key", _backend="rust", **client_options,
    )
    monkeypatch.setattr(client._adapter, "execute", sender.execute)
    monkeypatch.setattr(client._adapter, "get_container_metadata", sender.get_container_metadata)
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
        hedging = sender.events[-1].settings.hedging
        if enabled is None:
            assert hedging is None
        else:
            assert (hedging.enabled, hedging.threshold_ms) == (enabled, threshold)
    result = orders.read_item("order-42", "customer-17")
    if async_mode:
        asyncio.run(result)
    assert sender.events[-1].settings.hedging is None
    result = client.close()
    if async_mode:
        asyncio.run(result)


def invoke(helper, op, **kwargs):
    """Call one item operation with the smallest set of arguments it needs.

    create, upsert and replace get an item body. read, replace, delete and patch
    get an item id. read, delete and patch get a partition key. patch also gets
    one change. Any extra keyword arguments are added on top. An async result is
    awaited, so one test body works for both clients.
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
def test_item_operations_use_client_priority_and_throughput_bucket_rust(async_mode, op, kwargs, priority, bucket):
    """Item operations use the client's priority and throughput bucket unless the call gives its own.

    The client defaults here are priority "Low" and throughput bucket 3. A call
    that gives "High" and 5 uses those values. A call that gives None and 0 counts
    as not given, so the defaults apply. A call that sets the same two values as
    headers in ``initial_headers`` keeps the header values, and no default is
    added.

    All six item operations are checked on both clients.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(
        sender, ClientOperationDefaults(priority="Low", throughput_bucket=3)
    )
    invoke(helper, op, **kwargs)
    request = sender.events[-1]
    headers = wire_headers(request)
    caller_headers = headers.get("initialHeaders", headers)
    priority_header = "x-ms-cosmos-priority-level"
    bucket_header = "x-ms-cosmos-throughput-bucket"
    assert headers.get(priority_header, caller_headers.get(priority_header)) == priority
    assert headers.get(bucket_header, caller_headers.get(bucket_header)) == str(bucket)


@pytest.mark.parametrize("op", [
    "create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item",
])
def test_request_builder_gets_exact_arguments_for_each_operation_rust(monkeypatch, op):
    """The shared request builder gives each operation exactly the arguments it needs.

    The sync and async item helpers use the same builder function, which is
    checked first. The builder picks the request function for the operation and
    calls it. The test replaces that function with a mock and checks the exact
    arguments:

    - Every operation gets the container, partition key and options.
    - create, upsert and replace get the item body. They are told not to read the
      partition key from the body, because the call already gives it.
    - create also gets its indexing setting.
    - Writes and patch get the client's ``no_response_on_write`` default.
    - Operations that name an existing item get its id.
    - patch gets its list of changes as JSON bytes.

    The builder returns the mock's request unchanged. The full list is checked
    because a missing argument would not cause an error. The request function
    would silently use its default value instead.
    """
    assert async_build_item_request is build_item_request
    body = {"id": "order-42", "customerId": "customer-17", "total": 125.50}
    arguments = {
        "container_link": "dbs/Contoso/colls/Orders",
        "request_options": {"partitionKey": "customer-17"},
    }
    if op != "read_item":
        arguments.update(body=body, no_response=True, enable_automatic_id_generation=True)
    if op not in ("create_item", "upsert_item"):
        arguments["item_id"] = "order-42"
    if op == "patch_item":
        arguments["patch_operations"] = [{"op": "replace", "path": "/total", "value": 150}]
    args, options = normalize_item_arguments(op, arguments)
    fake_request = PreparedRequest(op, args["container_link"], b"", key_from_legacy_header('["customer-17"]'))
    fake_request_function = MagicMock(return_value=fake_request)
    monkeypatch.setattr(_request_item, f"build_{op}_request", fake_request_function)

    result = build_item_request(op, args, options, ClientOperationDefaults(False))

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
    if op in ("read_item", "replace_item", "delete_item", "patch_item"):
        expected["item_self_link"] = None
    if op == "patch_item":
        expected.update(body_bytes=args["body_bytes"])
    fake_request_function.assert_called_once_with(**expected)
    assert result is fake_request


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_each_item_operation_sends_one_request_and_updates_headers_rust(async_mode, op):
    """Each item operation sends one request and handles the reply the same way on both clients.

    For each operation the test checks:

    - Exactly one request is sent, with the right operation name.
    - read, delete and patch carry the partition key given by the call. create,
      upsert and replace carry none, because the key is read from the item body
      later.
    - No container id header (``x-ms-cosmos-intended-collection-rid``) is added.
    - The response hook is called once and the last response headers are updated.
    - delete returns None and passes None as the body to the hook. The others
      return a ``CosmosDict`` whose headers match the last response headers.
    - Writes and patch ask for no response body, because the client default
      ``no_response_on_write`` is True here.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    last_headers = ClientLastResponseHeaders()
    hook = MagicMock()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(sender, ClientOperationDefaults(True), last_headers)
    result = invoke(helper, op, response_hook=hook)
    assert len(sender.events) == 1
    request = sender.events[0]
    assert request.op == op
    expected_key = None if op in ("create_item", "upsert_item", "replace_item") else '["p"]'
    assert legacy_partition_key_from_request(request) == expected_key
    assert "x-ms-cosmos-intended-collection-rid" not in wire_headers(request)
    hook.assert_called_once()
    assert last_headers.last_response_headers["x-ms-request-charge"] == "2.5"
    if op == "delete_item":
        assert result is None
        assert hook.call_args.args[1] is None
    else:
        assert isinstance(result, CosmosDict)
        assert result.get_response_headers() == last_headers.last_response_headers
    if op in ("create_item", "upsert_item", "replace_item", "patch_item"):
        assert settings_options(request)["responsePayloadOnWriteDisabled"] is True


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("error", [
    BindingProtocolError("missing metadata"), BindingProtocolError("invalid rid"),
    BindingProtocolError("invalid partition key"),
    CosmosResourceNotFoundError(status_code=404, message="missing"), AttributeError("lookup failed"),
])
def test_error_while_sending_reaches_caller_unchanged_rust(async_mode, error):
    """An error raised while sending reaches the caller unchanged.

    The fake sender raises one of several errors after recording the request. The
    caller gets the very same exception object, and the response hook is not
    called. Exactly one request is recorded, and there is no container details
    lookup.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    sender.metadata = error
    helper = (AsyncItemHelper if async_mode else ItemHelper)(sender)
    hook = MagicMock()
    with pytest.raises(type(error)) as raised:
        invoke(helper, "create_item", response_hook=hook)
    assert raised.value is error
    hook.assert_not_called()
    assert len(sender.events) == 1
    assert sender.events[0].op == "create_item"


@pytest.mark.parametrize("async_mode", [False, True])
def test_item_call_options_and_404_and_304_replies_rust(async_mode):
    """Per-call options are applied, unsupported patch options are refused, and 404 and 304 replies are handled.

    - ``no_response=False`` on create overrides the client default and asks for
      the response body.
    - ``filter_predicate`` on patch is sent in the patch body as ``condition``.
    - patch refuses ``retry_write``, headers the SDK always sets itself (such as
      User-Agent), and an If-None-Match condition. Each raises
      NotImplementedError.
    - A timeout below 1 second raises ValueError.
    - None of the refused calls sends anything.
    - A 404 reply raises ``CosmosResourceNotFoundError``, does not call the
      response hook, and still updates the last response headers.
    - A 304 reply on read returns an empty dict and calls the response hook.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    helper_type = AsyncItemHelper if async_mode else ItemHelper
    last_headers = ClientLastResponseHeaders()
    helper = helper_type(sender, ClientOperationDefaults(True), last_headers)
    invoke(helper, "create_item", no_response=False)
    assert settings_options(sender.events[-1])["responsePayloadOnWriteDisabled"] is False
    sender.events.clear()
    invoke(helper, "patch_item", filter_predicate="FROM c WHERE c.x = 1")
    (patch_request,) = sender.events
    assert json.loads(patch_request.body_bytes) == {
        "operations": [{"op": "add", "path": "/a", "value": 1}],
        "condition": "FROM c WHERE c.x = 1",
    }
    sender.events.clear()
    for kwargs in ({"retry_write": 1},
                   {"initial_headers": {"User-Agent": "caller"}},
                   {"access_condition": {"type": "IfNoneMatch", "condition": '"e"'}}):
        with pytest.raises(NotImplementedError):
            invoke(helper, "patch_item", **kwargs)
    with pytest.raises(ValueError, match="timeout"):
        invoke(helper, "patch_item", timeout=0.5)
    assert not sender.events
    sender.reply = fake_reply({"message": "gone"}, 404, {"etag": "error"})
    hook = MagicMock()
    with pytest.raises(CosmosResourceNotFoundError):
        invoke(helper_type(sender, response_state=last_headers), "read_item", response_hook=hook)
    hook.assert_not_called()
    assert last_headers.last_response_headers["etag"] == "error"
    sender.reply = fake_reply(status=304, headers={"etag": "current"})
    result = invoke(helper_type(sender), "read_item", response_hook=hook)
    assert result == {}
    hook.assert_called_once()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("key", [NonePartitionKeyValue, NullPartitionKeyValue])
def test_special_partition_key_values_work_without_connection_rust(async_mode, key):
    """read_item works with the two special partition key values on a container that has no connection.

    ``NonePartitionKeyValue`` means the item has no partition key value.
    ``NullPartitionKeyValue`` means the value is JSON null. Both reads succeed and
    send exactly one request.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    context = CosmosClientContext(sender)
    proxy_type = AsyncContainerProxy if async_mode else ContainerProxy
    proxy = proxy_type(None, "dbs/d", "c", _client_context=context)
    result = proxy.read_item("x", partition_key=key)
    if async_mode:
        result = asyncio.run(result)
    assert result["id"] == "x"
    assert len(sender.events) == 1


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_item_operations_do_not_use_connection_code_rust(async_mode, op):
    """All six item operations run without calling any connection-based request code.

    The container has no connection. While each operation runs, Python's profiler
    hook (``sys.setprofile``) records every function call. The test fails if any
    call lands in the client connection modules, the connection-based item helper
    modules, or the ``build_*`` functions in ``_item_arguments``.

    Exactly one request is sent and the result comes back. The request has no
    container id header, even though the container object was given an id in its
    properties.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    proxy_type = AsyncContainerProxy if async_mode else ContainerProxy
    proxy = proxy_type(
        None, "dbs/d", "c", properties={"_rid": "rid-from-container-properties"},
        _client_context=CosmosClientContext(sender),
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
    connection_code_calls = []
    previous_profile = sys.getprofile()

    def record_connection_code_calls(frame, event, arg):
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
                connection_code_calls.append((module, frame.f_code.co_name))

    sys.setprofile(record_connection_code_calls)
    try:
        result = getattr(proxy, op)(**arguments)
        if async_mode:
            result = asyncio.run(result)
    finally:
        sys.setprofile(previous_profile)
    assert connection_code_calls == []
    assert len(sender.events) == 1
    assert sender.events[0].op == op
    assert "x-ms-cosmos-intended-collection-rid" not in sender.events[0].headers
    assert result is None if op == "delete_item" else result["id"] == "x"


@pytest.mark.parametrize("async_mode", [False, True])
def test_writes_skip_container_lookup_and_failed_send_keeps_last_headers_rust(async_mode):
    """Writes never look up container details, and a failed send keeps the last response headers.

    Two writes send two requests and no container details lookup. Then the fake
    sender raises a 404 error without a reply. The last response headers are
    still the same object as after the second write. A caller who reads them
    after the failure therefore sees the headers of the last call that got a
    reply.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    last_headers = ClientLastResponseHeaders()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(sender, response_state=last_headers)
    invoke(helper, "create_item")
    invoke(helper, "upsert_item")
    assert sender.events.count("metadata") == 0
    assert len(sender.events) == 2
    headers_before_failure = last_headers.last_response_headers
    sender.metadata = CosmosResourceNotFoundError(status_code=404, message="missing")
    with pytest.raises(CosmosResourceNotFoundError):
        invoke(helper, "read_item")
    assert last_headers.last_response_headers is headers_before_failure


@pytest.mark.parametrize("helper_type,sender_type", [(ItemHelper, FakeSender), (AsyncItemHelper, AsyncFakeSender)])
def test_item_helper_rejects_connection_as_defaults_rust(helper_type, sender_type):
    """The item helper's second argument must be ``ClientOperationDefaults``.

    Passing any other object, such as a client connection, raises TypeError with
    a message that names the expected type. The mistake is caught at once,
    instead of failing later with a less clear error.
    """
    with pytest.raises(TypeError, match="ClientOperationDefaults"):
        helper_type(sender_type(), object())


@pytest.mark.parametrize("helper_type,sender_type", [(ItemHelper, FakeSender), (AsyncItemHelper, AsyncFakeSender)])
def test_item_helper_rejects_wrong_response_headers_object_rust(helper_type, sender_type):
    """The item helper only accepts a ``ClientLastResponseHeaders`` object for ``response_state``.

    ``response_state`` is where the item helper stores the last response headers.
    Any other object raises TypeError when the helper is created, instead of
    failing later during a call.
    """
    with pytest.raises(TypeError, match="response_state must be ClientLastResponseHeaders"):
        helper_type(sender_type(), response_state=object())


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["read_item", "delete_item", "upsert_item", "replace_item"])
@pytest.mark.parametrize("condition,etag,header,value", [
    (MatchConditions.IfNotModified, '"v"', "If-Match", '"v"'),
    (MatchConditions.IfModified, '"v"', "If-None-Match", '"v"'),
    (MatchConditions.IfPresent, None, "If-Match", "*"),
    (MatchConditions.IfMissing, None, "If-None-Match", "*"),
])
def test_match_condition_sets_if_match_or_if_none_match_rust(async_mode, op, condition, etag, header, value):
    """``match_condition`` and ``etag`` set the right If-Match or If-None-Match value.

    IfNotModified sets If-Match to the etag. IfModified sets If-None-Match to the
    etag. IfPresent sets If-Match to ``"*"``. IfMissing sets If-None-Match to
    ``"*"``. This is checked for read, delete, upsert and replace on both clients.

    The test checks the values in the prepared request's settings, not the HTTP
    headers that are finally sent.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(sender)
    invoke(helper, op, match_condition=condition, etag=etag)
    assert getattr(sender.events[-1].settings.item, header.lower().replace("-", "_")) == value


@pytest.mark.parametrize("kwargs,error,message", [
    ({"etag": "v"}, ValueError, "'etag' specified without 'match_condition'."),
    ({"match_condition": MatchConditions.IfModified}, ValueError, "'match_condition' specified without 'etag'."),
    ({"match_condition": MatchConditions.IfNotModified}, ValueError, "'match_condition' specified without 'etag'."),
    ({"match_condition": "invalid"}, TypeError, "Invalid match condition: invalid"),
])
def test_incomplete_match_condition_raises_before_sending_rust(kwargs, error, message):
    """An incomplete or unknown match condition raises an error before anything is sent.

    Each of these raises an error with an exact message, on both clients:

    - an etag without ``match_condition``
    - IfModified or IfNotModified without an etag
    - a value that is not a ``MatchConditions`` member

    The fake sender records nothing.
    """
    for helper_type, sender_type in ((ItemHelper, FakeSender), (AsyncItemHelper, AsyncFakeSender)):
        sender = sender_type()
        with pytest.raises(error) as caught:
            invoke(helper_type(sender), "read_item", **kwargs)
        assert str(caught.value) == message
        assert sender.events == []


def test_item_option_preparation_copies_input_and_direct_arguments_win_rust():
    """Preparing item options copies the caller's input, and direct arguments win over ``request_options``.

    The caller gives a priority and an access condition in ``request_options``,
    and also as direct arguments (``priority``, ``if_match``, ``if_none_match``).
    The direct values win. When both ``if_match`` and ``if_none_match`` are given,
    ``if_none_match`` is used.

    The caller's dicts are not changed, and the options are a new dict. The
    options have no start time entry, there is no ``wire_kwargs`` entry, and
    ``timeout`` stays with the call keywords.
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
def test_partition_key_path_split_handles_quotes_and_spaces_rust(path, expected):
    """``parse_paths`` splits a partition key path into its parts, handling quotes and spaces.

    A part in double or single quotes may contain a slash and stays one part. An
    escaped quote inside a quoted part is kept as written. Spaces around a part
    are removed. The root path ``"/"`` has no parts. A plain split on ``"/"``
    would get the quoted cases wrong.
    """
    assert parse_paths([path]) == expected


@pytest.mark.parametrize("path", ["no-leading-slash", '/"unterminated', '/"a"b'])
def test_partition_key_path_split_rejects_invalid_paths_rust(path):
    """``parse_paths`` rejects a path it cannot read, and the message gives the position.

    The invalid paths are: no leading slash, a quote that is never closed, and
    text right after a closing quote. Each raises ValueError with "Invalid path
    character at index".
    """
    with pytest.raises(ValueError, match="Invalid path character at index"):
        parse_paths([path])


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("compact_utf8", [False, True])
def test_client_shares_one_context_and_keeps_connection_headers_in_sync_rust(
    monkeypatch, async_mode, compact_utf8,
):
    """The client creates one client context, shares it, and keeps the connection's headers in sync.

    - Exactly one client context is created. It holds the fake sender and the
      client options ``no_response_on_write`` and
      ``enable_compact_utf8_item_writes``.
    - The database and container objects use that same context.
    - create_item takes ``no_response_on_write`` from the context. The test makes
      reading it from the connection fail.
    - The connection's ``last_response_headers`` is the same object as the
      context's. Setting it on the connection is seen by the context.
    - The client defaults cannot be changed after the client is created.
    """
    sender = AsyncFakeSender() if async_mode else FakeSender()
    client_module = "azure.cosmos.aio._cosmos_client" if async_mode else "azure.cosmos.cosmos_client"
    factory_name = ".make_async_backend" if async_mode else ".make_backend"
    monkeypatch.setattr(client_module + factory_name, lambda *a, **kw: sender)
    created_contexts = []

    def record_context(*args, **kwargs):
        context = CosmosClientContext(*args, **kwargs)
        created_contexts.append(context)
        return context

    monkeypatch.setattr(client_module + ".CosmosClientContext", record_context)
    # Replace only the connection's setup. Its last_response_headers property stays real.
    connection_type = __import__(
        "azure.cosmos.aio._cosmos_client_connection_async" if async_mode else
        "azure.cosmos._cosmos_client_connection", fromlist=["CosmosClientConnection"]
    ).CosmosClientConnection

    def fake_connection_init(connection, **kwargs):
        assert len(created_contexts) == 1
        assert created_contexts[0].adapter is sender
        assert created_contexts[0].defaults.no_response_on_write is True
        assert created_contexts[0].defaults.enable_compact_utf8_item_writes is compact_utf8
        assert kwargs["enable_compact_utf8_item_writes"] is compact_utf8
        assert kwargs["_response_state"] is created_contexts[0].response_state
        connection._response_state = kwargs["_response_state"]

    monkeypatch.setattr(connection_type, "__init__", fake_connection_init)
    client = (AsyncCosmosClient if async_mode else CosmosClient)(
        "https://example.documents.azure.com", "key", no_response_on_write=True,
        enable_compact_utf8_item_writes=compact_utf8,
    )
    database = client.get_database_client("d")
    container = database.get_container_client("c")
    assert container._client_context is database._client_context is client._client_context
    connection = client.client_connection
    # Point the connection at a different sender, so a create that used the
    # connection would not reach the fake sender.
    connection._backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND

    class PolicyThatMustNotBeRead:
        @property
        def ResponsePayloadOnWriteDisabled(self):
            raise AssertionError("Item operations must not read defaults from the connection")

    connection.connection_policy = PolicyThatMustNotBeRead()
    hook = MagicMock(side_effect=lambda h, b: sender.events.append("hook"))
    result = container.create_item({"id": "x", "pk": "p"}, response_hook=hook)
    if async_mode:
        result = asyncio.run(result)
    assert result["id"] == "x"
    assert settings_options(sender.events[-2])["responsePayloadOnWriteDisabled"] is True
    assert sender.events[-1] == "hook"
    assert connection.last_response_headers is client._client_context.response_state.last_response_headers
    connection.last_response_headers = {"set-on": "connection"}
    assert client._client_context.response_state.last_response_headers == {"set-on": "connection"}
    with pytest.raises(FrozenInstanceError):
        client._client_context.defaults.no_response_on_write = False


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("with_context", [False, True])
def test_read_items_uses_only_client_context_rust(async_mode, with_context):
    """read_items uses the client context and never touches the connection.

    With a client context, read_items sends one request through the context's
    sender, returns the items, and its response headers match the last response
    headers. The connection, which points at a different sender, is never used.
    Without a client context, read_items raises NotImplementedError and sends
    nothing.
    """
    from read_items._helpers import make_proxy, page

    proxy, sender = make_proxy(async_mode, [page([{"id": "x", "pk": "p"}], 2)])
    connection = MagicMock()
    connection._backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND
    proxy.client_connection = connection
    if not with_context:
        proxy._client_context = None
        with pytest.raises(NotImplementedError, match="requires a client-owned"):
            result = proxy.read_items([("x", "p")])
            if async_mode:
                asyncio.run(result)
        assert sender.calls == []
        return
    result = proxy.read_items([("x", "p")])
    if async_mode:
        result = asyncio.run(result)
    assert result == [{"id": "x", "pk": "p"}]
    assert result.get_response_headers() == proxy._client_context.response_state.last_response_headers
    assert sender.calls[-1].op == "read_items"
    assert connection.mock_calls == []
