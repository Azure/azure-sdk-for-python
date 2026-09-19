# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline checks of Python metadata handling and response-header publication.

Native entry points are replaced. Point-operation cases assert one item
binding invocation and no separate Python metadata invocation; this is not
a count of HTTP requests or driver-internal metadata/cache activity.
Error cases inspect translated details and preservation of prior headers.
"""
from common.typed_requests import legacy_partition_key_from_request

import asyncio
import inspect
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.exceptions import ServiceResponseError
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos._backend._binding_conversions import build_container_metadata
from azure.cosmos._backend.contracts import ContainerMetadata
from azure.cosmos._backend.errors import BackendProtocolError
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders
from azure.cosmos._helpers._pk_extract import extract_partition_key_value
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError
from azure.cosmos.partition_key import _Empty, _Undefined


@pytest.mark.parametrize(
    "raw",
    [
        None,
        (),
        (200, 0, {}, b'{"_rid":"rid"}'),
        ("", ("/pk",), "Hash", None),
        (12, (), None, None),
        ("rid", ["/pk"], "Hash", None),
        ("rid", (1,), "Hash", None),
        ("rid", ("",), "Hash", None),
        ("rid", (), "Hash", None),
        ("rid", ("/pk",), None, None),
        ("rid", ("/pk",), "unknown", None),
        ("rid", ("/pk",), "Hash", 1),
    ],
)
def test_invalid_native_metadata_is_a_protocol_error(raw):
    """Anything that is not well-formed metadata is refused outright.

    Twelve shapes are covered: nothing at all, an empty set of values, a
    response-shaped set of values that belongs to a different call, an empty or
    non-text container id, paths given as a list rather than a fixed sequence, a
    path that is a number, an empty path, a missing kind, an unrecognized kind,
    and a system-key flag that is not a true or false value.

    Every one raises rather than being partly accepted. Metadata decides where
    an item is stored, so a half-understood answer would route items to the
    wrong place and only surface much later as missing data.

    Note that no paths at all is refused here in combination with a kind, while
    genuinely absent metadata is handled separately below.
    """
    with pytest.raises(BackendProtocolError):
        build_container_metadata(raw)


@pytest.mark.parametrize("kind", ["Hash", "MultiHash", "Range"])
@pytest.mark.parametrize("system_key", [None, False, True])
def test_metadata_preserves_kind_and_system_key_knowledge(kind, system_key):
    """All three partition key kinds and all three states of the system-key flag survive
    unchanged, and the result cannot be edited afterwards.

    The flag has three meaningful states -- true, false, and unknown -- and they
    are not interchangeable. Collapsing unknown into false would make the client
    act on a guess about how the container was defined.

    The result refuses to be modified. Metadata describes how the container
    really is; code that could edit its own copy would be able to convince the
    rest of the client of something untrue.
    """
    result = build_container_metadata(("rid", ("/pk",), kind, system_key))
    assert result == ContainerMetadata("rid", ("/pk",), kind, system_key)
    with pytest.raises(FrozenInstanceError):
        result.rid = "changed"


@pytest.mark.parametrize(
    "kind,paths,body,expected",
    [
        ("Hash", ("/pk",), {"pk": "customerA"}, "customerA"),
        ("Hash", ("/address/city",), {"address": {"city": "Seattle"}}, "Seattle"),
        ("MultiHash", ("/a", "/b"), {"a": "x", "b": "y"}, ["x", "y"]),
        ("MultiHash", ("/a", "/b"), {"a": "x"}, ["x", None]),
        ("MultiHash", ("/pk",), {"pk": "x"}, ["x"]),
        ("Range", ("/pk",), {"pk": "x"}, "x"),
    ],
)
def test_extraction_uses_kind_not_path_count(kind, paths, body, expected):
    """The partition key value is shaped by the container's kind, not by how many paths
    it happens to have.

    A hierarchical container returns a list even when it has only one path,
    while a single-path container returns a bare value. Deciding by counting
    paths instead would get that one-path hierarchical case wrong, and the
    service would not find items written under the other shape.

    A nested path reaches into the item to find its value. A hierarchical
    container missing one of its values yields ``None`` in that position rather
    than a shorter list, which would silently shift the remaining values.
    """
    assert (
        extract_partition_key_value(ContainerMetadata("rid", paths, kind), body)
        == expected
    )


@pytest.mark.parametrize(
    "flag,expected", [(True, _Empty), (False, _Undefined), (None, _Undefined)]
)
def test_missing_partition_key_preserves_existing_system_key_behavior(flag, expected):
    """An item with no partition key value is reported differently depending on whether
    the container uses a system key.

    With a system key the result is "empty"; without one, or when it is not
    known, the result is "undefined". These are two different things on the
    wire, and the service stores items under different keys for each.

    Unknown deliberately behaves like false, matching what earlier versions did,
    so containers whose definition the client cannot confirm keep working the
    way they always have.
    """
    metadata = ContainerMetadata("rid", ("/pk",), "Hash", flag)
    assert isinstance(extract_partition_key_value(metadata, {"id": "item"}), expected)


def test_absent_definition_is_explicit():
    """A container with no partition key definition yields "empty", even when the item
    has a value that would otherwise have matched.

    With no paths defined there is nothing to extract, so a field in the item
    that merely looks like a partition key is ignored rather than guessed at.
    Guessing would send the item somewhere the container does not expect.
    """
    metadata = build_container_metadata(("rid", (), None, None))
    assert isinstance(extract_partition_key_value(metadata, {"pk": "ignored"}), _Empty)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def metadata_case(request, monkeypatch):
    """Build a real Rust backend whose driver is replaced by a stand-in, sync and async.

    Everything above the driver is the shipping code; only the driver's own
    entry points are swapped. That way the engine selection, error translation,
    and header handling under test are the real ones.

    The client's record of the last response headers is seeded with values from
    an earlier call. Both stand-in entry points assert, as they are called, that
    this record has not been replaced yet -- so a test can prove headers are
    published only once a real item response arrives, not before.

    Either step can be armed to fail: the metadata lookup or the write itself.
    """
    asynchronous = request.param
    module = async_rust if asynchronous else sync_rust
    state = ClientLastResponseHeaders(
        CaseInsensitiveDict({"etag": "previous", "x-ms-request-charge": "7"})
    )
    original_headers = state.last_response_headers
    context = SimpleNamespace(
        raw=("rid", ("/pk",), "Hash", None),
        asynchronous=asynchronous,
        state=state,
        original_headers=original_headers,
        metadata_error=None,
        write_error=None,
    )

    def metadata(*_args, **_kwargs):
        assert state.last_response_headers is original_headers
        if context.metadata_error is not None:
            raise context.metadata_error
        return context.raw

    def create(_handle, prepared, **_kwargs):
        context.prepared = prepared
        assert state.last_response_headers is original_headers
        if context.metadata_error is not None:
            raise context.metadata_error
        if context.write_error is not None:
            raise context.write_error
        return (
            201,
            0,
            {"etag": "item", "x-ms-request-charge": "3"},
            b'{"id":"item"}',
            None,
        )

    wrap = AsyncMock if asynchronous else MagicMock
    binding = SimpleNamespace()
    getter = wrap(side_effect=metadata)
    setattr(
        binding,
        "get_container_metadata_async" if asynchronous else "get_container_metadata",
        getter,
    )
    setattr(
        binding,
        "create_item_async" if asynchronous else "create_item",
        wrap(side_effect=create),
    )
    context.item_call = getattr(
        binding, "create_item_async" if asynchronous else "create_item"
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    backend = (async_rust.AsyncRustBackend if asynchronous else sync_rust.RustBackend)(
        "https://metadata.invalid",
        master_key="ZmFrZQ==",
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", wrap(return_value="handle"))
    helper = (AsyncItemHelper if asynchronous else ItemHelper)(
        backend, response_state=state
    )

    def run(value):
        return asyncio.run(value) if inspect.isawaitable(value) else value

    context.get = lambda: run(backend.get_container_metadata("dbs/db/colls/c"))
    from common.request_preparation import call_create_item_helper
    context.create = lambda **kwargs: run(
        call_create_item_helper(
            helper,
            container_link="dbs/db/colls/c",
            body={"id": "item", "pk": "key"},
            **kwargs,
        )
    )
    context.run, context.helper, context.backend, context.getter, context.module = (
        run,
        helper,
        backend,
        getter,
        module,
    )
    yield context
    run(backend.close())


def test_metadata_success_does_not_parse_json_or_a_response(metadata_case, monkeypatch):
    """Fetching metadata is not an item read, and does not go through response
    handling at all.

    Response parsing, response building, and text decoding are each replaced
    with something that fails if called. The lookup still succeeds, proving it
    takes the driver's answer directly rather than pretending it was an ordinary
    reply.

    That matters for cost as much as correctness: treating metadata as a
    response would run it through parsing on a path used by every operation.

    The client's record of the last response headers is also untouched, because
    this was not a call the customer made.
    """
    def forbidden(*_args, **_kwargs):
        raise AssertionError("Metadata is not a document response")

    monkeypatch.setattr(
        "azure.cosmos._helpers._response_parse.process_backend_response", forbidden
    )
    monkeypatch.setattr(
        "azure.cosmos._backend._binding_conversions.build_backend_response", forbidden
    )
    monkeypatch.setattr("json.loads", forbidden)
    assert metadata_case.get() == ContainerMetadata("rid", ("/pk",), "Hash")
    assert metadata_case.state.last_response_headers is metadata_case.original_headers


def test_each_call_observes_current_driver_metadata_without_a_python_cache(
    metadata_case,
):
    """Each lookup asks the driver again rather than remembering an earlier answer.

    The driver's answer is changed between two lookups, as if the container had
    been deleted and recreated, and the second lookup sees the new value. Both
    calls reached the driver.

    Keeping a copy in Python would be the bug: the driver already caches this
    and knows when it is stale. A second cache above it could go on addressing a
    container that no longer exists, sending items to an id the service has
    since reused.
    """
    assert metadata_case.get().rid == "rid"
    metadata_case.raw = ("recreated-rid", ("/tenant",), "Hash", None)
    assert metadata_case.get().rid == "recreated-rid"
    assert metadata_case.getter.call_count == 2


def test_point_operation_uses_one_item_call_and_only_publishes_item_headers(
    metadata_case,
):
    """One mocked item-binding call publishes its response headers.

    Python does not invoke the separate metadata entry point. The native
    driver's internal resolution and network requests are outside this test.
    """
    metadata_case.create()
    assert metadata_case.getter.call_count == 0
    assert metadata_case.item_call.call_count == 1
    assert "x-ms-cosmos-intended-collection-rid" not in metadata_case.prepared.headers
    assert legacy_partition_key_from_request(metadata_case.prepared) is None
    assert metadata_case.state.last_response_headers["etag"] == "item"


@pytest.mark.parametrize(
    "key,header",
    [
        ("explicit", '["explicit"]'),
        (None, "[null]"),
        (_Undefined(), "[{}]"),
        (_Empty(), "[]"),
    ],
)
def test_explicit_key_overrides_extraction(metadata_case, key, header):
    """A partition key the customer supplied is used as given, and still no metadata is
    fetched.

    Four values are covered and each has its own wire form: an ordinary value,
    ``None``, "undefined", and "empty". They are genuinely different -- ``None``
    is a real partition key value, while undefined and empty mean the item has
    none, in the two different ways a container can express that.

    Collapsing any of them together would write items under a different key than
    the customer asked for, and later reads with the same key would not find
    them.
    """
    metadata_case.create(request_options={"partitionKey": key})
    assert legacy_partition_key_from_request(metadata_case.prepared) == header
    assert metadata_case.getter.call_count == 0


@pytest.mark.parametrize(
    "op",
    [
        "create_item",
        "upsert_item",
        "replace_item",
        "read_item",
        "delete_item",
        "patch_item",
    ],
)
def test_all_point_operations_enter_only_the_item_binding(
    metadata_case, op, monkeypatch
):
    """Each listed point operation uses its item-binding entry, not Python metadata.

    One fake binding call is not proof of one HTTP request.
    """
    case = metadata_case
    method = op + ("_async" if case.asynchronous else "")
    monkeypatch.setattr(case.module._rust_module, method, case.item_call, raising=False)
    arguments = {"container_link": "dbs/db/colls/c", "item_id": "item"}
    if op in ("create_item", "upsert_item", "replace_item"):
        arguments["body"] = {"id": "item", "pk": "key"}
    else:
        arguments["request_options"] = {"partitionKey": "key"}
    if op == "patch_item":
        arguments["patch_operations"] = [{"op": "incr", "path": "/n", "value": 1}]
    from common.request_preparation import call_item_helper
    case.run(call_item_helper(case.helper, op, **arguments))
    case.item_call.assert_called_once()
    case.getter.assert_not_called()
    assert "x-ms-cosmos-intended-collection-rid" not in case.prepared.headers


@pytest.mark.parametrize("status", [400, 404, 429])
def test_metadata_errors_keep_details_without_publishing_headers(metadata_case, status):
    """Selected metadata error fields survive translation without publishing headers.

    These synthetic failures check status, substatus, message, exception type,
    retry-after, diagnostics, and prior response state, not every error detail.
    """
    raw = (
        status,
        1002,
        {
            "etag": "metadata-error",
            "x-ms-retry-after-ms": "25",
            "x-ms-request-charge": "1",
        },
        b'{"message":"lookup failed"}',
        '{"request_count":1}',
    )
    metadata_case.metadata_error = metadata_case.module._DRIVER_RESPONSE_ERROR(raw)
    expected = CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError
    with pytest.raises(expected) as raised:
        metadata_case.create()
    error = raised.value
    assert error.status_code == status
    assert error.sub_status == 1002
    assert "lookup failed" in str(error)
    assert error.response.headers["etag"] == "metadata-error"
    assert error.response.headers["x-ms-retry-after-ms"] == "25"
    assert (
        error.response.headers["x-ms-cosmos-sdk-diagnostics"] == '{"request_count":1}'
    )
    assert metadata_case.state.last_response_headers is metadata_case.original_headers


@pytest.mark.parametrize("phase", ["metadata", "write"])
def test_transport_failure_does_not_clear_previous_headers(metadata_case, phase):
    """A transport failure at either step leaves the previous headers intact.

    The failure is injected once while resolving the container and once during
    the write itself, and it surfaces as a transport error both times.

    In neither case is the client's record of the last response headers cleared
    or replaced. A customer inspecting those headers after a failure should find
    the last call that actually returned something, not an empty set standing in
    for a request that never completed.
    """
    error = metadata_case.module._DRIVER_TRANSPORT_ERROR("transport failed")
    if phase == "metadata":
        metadata_case.metadata_error = error
    else:
        metadata_case.write_error = error
    with pytest.raises(ServiceResponseError):
        metadata_case.create()
    assert metadata_case.state.last_response_headers is metadata_case.original_headers


def test_metadata_cancellation_preserves_headers_and_drains_work(metadata_case):
    """Cancelling a write in flight unwinds the driver call and leaves the headers
    alone.

    The write is made to hang, then cancelled. Three things must hold: the
    cancellation reaches the caller rather than being turned into something else,
    the hanging call is actually unwound rather than left running, and the
    client's record of the last response headers is untouched.

    The middle one is the easiest to get wrong. A call abandoned but still alive
    would hold the driver's resources for the life of the process, and might
    write its headers long after the customer gave up.

    Async only -- there is nothing to cancel on the sync client.
    """
    if not metadata_case.asynchronous:
        pytest.skip("Async cancellation contract")

    async def run():
        started, stopped = asyncio.Event(), asyncio.Event()

        async def pending(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                stopped.set()

        metadata_case.item_call.side_effect = pending
        from common.request_preparation import call_create_item_helper
        task = asyncio.create_task(
            call_create_item_helper(
                metadata_case.helper,
                container_link="dbs/db/colls/c",
                body={"id": "item", "pk": "key"},
                timeout=1,
            )
        )
        await asyncio.wait_for(started.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stopped.is_set()
        assert (
            metadata_case.state.last_response_headers is metadata_case.original_headers
        )

    asyncio.run(run())
