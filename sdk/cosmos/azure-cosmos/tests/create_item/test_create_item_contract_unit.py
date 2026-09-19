# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Single-item create contract through both public clients and their real dispatch adapters.

Every test here runs four times -- sync/async crossed with legacy/Rust -- so a
rule proved here is proved for all four combinations a customer can hit. The
container, the proxies and the option-merge helpers are all real; only the
network call at the bottom is faked, along with the clock, so the tests can
assert on exact time budgets without sleeping.

The ``point_create.events`` list is the spine of most assertions. It records
``("metadata", budget)`` and ``("write", budget)`` in the order the call made
them, so a test can prove not just the outcome but that a bad argument was
caught *before* anything was sent.

Create adds three concerns a point read does not have: the client may generate
the ``id`` itself, the body is serialized and sent, and the caller's dict must
come back unchanged no matter what the response hook does to its copy.
"""
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
import asyncio
import inspect
import json
from dataclasses import replace
from types import MappingProxyType
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import CosmosDict
from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._helpers import _item_prep, _document
from azure.cosmos._helpers._item_context import ItemClientDefaults
from azure.cosmos._helpers._response_parse import process_backend_response
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceExistsError
from common.test_connection_free_items_unit import Backend, AsyncBackend, invoke
from read_item.test_read_item_contract_unit import point_read


@pytest.fixture
def point_create(point_read, monkeypatch):
    """Reuse the point-read harness and repoint it at ``create_item``.

    Takes the container, proxies and fake clock already built by ``point_read``
    and swaps the bottom-most call for a create: the Rust binding's
    ``create_item`` when the Rust backend is under test, otherwise the legacy
    ``ClientConnection.CreateItem``. Both fakes run the same ``response``
    function, so the two backends are held to one script.

    ``response`` records ``("write", budget)``, fails if the remaining budget is
    smaller than ``write_delay``, and honours ``responsePayloadOnWriteDisabled``
    by returning an empty payload. Tests steer it through ``context.status``,
    ``context.write_delay`` and ``context.default_no_response``.
    """
    context = point_read
    context.write_delay = 0
    context.status = 201
    context.default_no_response = False
    context.cc._enable_compact_utf8_item_writes = False
    monkeypatch.setattr(_item_prep, "time", context.clock)
    async_mode = inspect.iscoroutinefunction(context.proxy.create_item)

    def response(body, options, timeout):
        context.events.append(("write", timeout))
        if timeout is not None and context.write_delay > timeout:
            context.clock.now += timeout
            if context.rust:
                raise TimeoutError("native create budget exhausted")
            raise CosmosClientTimeoutError()
        context.clock.now += context.write_delay
        if context.status >= 400:
            body = {"message": "service rejected create"}
        context.sent_body = body
        no_response = options.get("responsePayloadOnWriteDisabled", context.default_no_response)
        encoded = b"" if no_response and context.status < 400 else json.dumps(body).encode()
        return context.status, 0, dict(context.headers), encoded, None

    def create_native(_driver_handle, prepared, *, timeout_seconds=None):
        context.prepared = prepared
        timeout_seconds = context.resolve_for_item(timeout_seconds)
        return response(json.loads(prepared.body_bytes), settings_options(prepared), timeout_seconds)

    def create_legacy(**kwargs):
        context.options = kwargs["options"]
        assert not {"response_hook", "_item_operation_deadline", "etag", "match_condition"}.intersection(kwargs)
        result = process_backend_response(BackendResponse(*response(
            kwargs["document"], kwargs["options"], kwargs.get("timeout")
        )))
        context.cc.last_response_headers = result.get_response_headers()
        return result

    def wrap(function):
        return AsyncMock(side_effect=function) if async_mode else MagicMock(side_effect=function)

    if context.rust:
        binding = (async_rust if async_mode else sync_rust)._rust_module
        monkeypatch.setattr(binding, "create_item_async" if async_mode else "create_item",
                            wrap(create_native), raising=False)
    context.cc.CreateItem = wrap(create_legacy)

    def call(*args, **kwargs):
        result = context.proxy.create_item(*args, **kwargs)
        return asyncio.run(result) if inspect.isawaitable(result) else result

    context.call = call
    return context


@pytest.mark.parametrize("name", ["populate_query_metrics", "etag", "match_condition"])
@pytest.mark.parametrize("value", [None, False, True])
def test_retired_options_are_rejected_before_metadata(point_create, name, value):
    """Arguments that used to be accepted now raise ``TypeError``, naming the argument.

    ``etag`` and ``match_condition`` never applied to create, and
    ``populate_query_metrics`` was dropped. Passing any of them is a mistake
    worth reporting loudly rather than ignoring, so the call must fail even when
    the value is ``None``. The empty ``events`` list proves nothing was sent.
    """
    with pytest.raises(TypeError, match=name):
        point_create.call({"id": "item"}, **{name: value})
    assert point_create.events == []


def test_only_body_is_positional(point_create):
    """``body`` is the one positional argument; everything else is keyword-only.

    This pins the calling shape so later argument additions or reordering cannot
    silently change what a positional call means. Passing a second positional
    argument must raise rather than be absorbed by some other parameter.
    """
    parameters = inspect.signature(point_create.proxy.create_item).parameters
    assert [name for name, value in parameters.items()
            if value.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD] == ["body"]
    for name in ("pre_trigger_include", "post_trigger_include", "indexing_directive"):
        assert parameters[name].kind == inspect.Parameter.KEYWORD_ONLY
    with pytest.raises(TypeError):
        point_create.call({"id": "item"}, None)
    assert point_create.events == []


@pytest.mark.parametrize("body,error", [
    (None, TypeError), ([], TypeError), ("{}", TypeError),
    ({}, ValueError), ({"id": ""}, ValueError), ({"id": None}, ValueError),
    ({"id": 42}, TypeError), ({"id": False}, TypeError),
    ({"id": "bad/id"}, ValueError), ({"id": "bad "}, ValueError),
    ({"id": "item", "value": float("nan")}, ValueError),
    ({"id": "item", "value": float("inf")}, ValueError),
    ({"id": "item", "value": object()}, TypeError),
])
def test_invalid_input_has_same_early_error_on_both_backends(point_create, body, error):
    """Bad bodies raise the same exception type on both backends, before any request.

    Covers a body that is not a mapping, a missing or empty or wrongly typed
    ``id``, an ``id`` holding a character the service forbids or a trailing
    space, and values JSON cannot represent (``nan``, ``inf``, an arbitrary
    object). ``TypeError`` means the wrong type was supplied, ``ValueError``
    means the type was right but the value is not usable.

    The point is that switching backends must not change which exception a
    customer's error handling sees, and that none of these reach the network.
    """
    with pytest.raises(error):
        point_create.call(body)
    assert point_create.events == []


@pytest.mark.parametrize("hierarchical", [False, True])
def test_auto_id_precedes_partition_key_extraction_and_does_not_mutate_input(point_create, hierarchical):
    """A generated ``id`` is in place before the partition key is read, and the caller's dict is untouched.

    Both container shapes put ``/id`` in the partition key, so the ordering is
    observable: if the id were generated after the key was extracted, the key
    would be missing or wrong. The hierarchical case adds a second path in front
    of it to prove the ordering holds for multi-path keys too.

    The caller's ``body`` must come back exactly as passed -- the generated id
    goes only into the copy that is sent. The returned id, the id in the sent
    body, and the id the Rust path carries alongside the request must all agree.
    """
    point_create.properties["partitionKey"] = {
        "kind": "MultiHash" if hierarchical else "Hash",
        "paths": ["/tenant", "/id"] if hierarchical else ["/id"],
    }
    body = {"tenant": "tenant", "nested": {"value": 1}}
    result = point_create.call(body, enable_automatic_id_generation=True)
    assert body == {"tenant": "tenant", "nested": {"value": 1}}
    assert isinstance(result["id"], str) and result["id"]
    assert point_create.sent_body["id"] == result["id"]
    if point_create.rust:
        assert legacy_partition_key_from_request(point_create.prepared) is None
        assert json.loads(point_create.prepared.body_bytes)["id"] == result["id"]
        assert point_create.prepared.item_id == result["id"]
        assert point_create.native_calls == 1


def test_mapping_and_request_options_are_not_mutated(point_create):
    """A read-only mapping is accepted as the body, and ``request_options`` is left alone.

    ``MappingProxyType`` cannot be written to, so it fails the test outright if
    any layer tries to add to the caller's body instead of copying it first.
    The options dict is checked separately because it is the other object a
    customer is likely to reuse across calls.
    """
    original = {"id": "item", "pk": "pk"}
    options = {"initialHeaders": {"x-customer": "kept"}}
    result = point_create.call(MappingProxyType(original), request_options=options)
    assert result == original
    assert options == {"initialHeaders": {"x-customer": "kept"}}


@pytest.mark.parametrize("no_response", [False, True])
def test_falsey_hook_gets_independent_body_and_headers(point_create, no_response):
    """A response hook is called even when it is falsey, and its edits stay in its own copy.

    ``Hook.__bool__`` returns ``False``, so any layer testing the hook with a
    plain truth check would skip it. The hook must still run exactly once.

    Whatever the hook writes -- into the headers it is handed, into the body's
    response headers, into the body itself -- must not show up in the value
    returned to the caller, in the caller's original dict, or in the stored
    last-response headers. Running with and without ``no_response`` covers both
    the populated body and the empty one.
    """
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert isinstance(body, CosmosDict)
            assert bool(body) != no_response
            headers["etag"] = "hook"
            assert body.get_response_headers()["etag"] == '"current"'
            body._response_headers["etag"] = "body-hook"
            if body:
                body["nested"]["value"] = 2
            body["added"] = True
            calls.append(body)

    original = {"id": "item", "nested": {"value": 1}}
    result = point_create.call(original, no_response=no_response, response_hook=Hook())
    assert isinstance(result, CosmosDict)
    assert result == ({} if no_response else original)
    assert original["nested"]["value"] == 1
    assert result.get_response_headers()["etag"] == '"current"'
    state = point_create.state.last_response_headers if point_create.rust else point_create.cc.last_response_headers
    assert state["etag"] == '"current"'
    assert len(calls) == 1


def test_explicit_body_response_overrides_client_default(point_create):
    """``no_response=False`` on the call beats a client configured to suppress bodies.

    The client default is switched on, then overridden per call. The created
    item must come back with its ``id``, proving the per-call value wins.
    """
    context = point_create.proxy._item_context
    point_create.proxy._item_context = replace(context, defaults=ItemClientDefaults(no_response_on_write=True))
    point_create.default_no_response = True
    assert point_create.call({"id": "item"}, no_response=False)["id"] == "item"


def test_hook_failure_does_not_replay_create(point_create):
    """If the customer's hook raises, the item is not created a second time.

    The hook runs after the write has already succeeded, so treating its failure
    as a retryable error would create a duplicate. The exception must reach the
    caller unchanged -- the same object, not a copy or a wrapper -- and the
    recorded phases must show one metadata lookup and one write.
    """
    error = NotImplementedError("customer hook")
    hook = MagicMock(side_effect=error)
    with pytest.raises(NotImplementedError) as raised:
        point_create.call({"id": "item"}, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert [phase for phase, _ in point_create.events] == ["metadata", "write"]


def test_service_conflict_remains_typed_and_does_not_invoke_success_hook(point_create):
    """A 409 from the service surfaces as ``CosmosResourceExistsError`` and skips the hook.

    An item with that id already exists. The status must be translated into the
    specific exception type customers catch, not a generic error, and the
    response hook must not run for a failed write. The write was still attempted,
    so both phases appear in ``events``.
    """
    point_create.status = 409
    hook = MagicMock()
    with pytest.raises(CosmosResourceExistsError):
        point_create.call({"id": "item"}, response_hook=hook)
    hook.assert_not_called()
    assert [phase for phase, _ in point_create.events] == ["metadata", "write"]


def test_remaining_subsecond_budget_reaches_create(point_create):
    """Time already spent on metadata is deducted, and the fraction left is passed on.

    A one second budget with a 0.75 second metadata lookup leaves 0.25 seconds.
    That remainder must be handed to the write as a fraction -- rounding it down
    to zero would abandon a call that still had time, and rounding up would
    overrun the budget the customer asked for.
    """
    point_create.metadata_delay = 0.75
    point_create.write_delay = 0.125
    result = point_create.call({"id": "item"}, timeout=1)
    assert result["id"] == "item"
    assert point_create.events == [("metadata", 1), ("write", 0.25)]


@pytest.mark.parametrize("metadata_delay,write_delay,phases", [
    (2, 0, ["metadata"]), (1, 0, ["metadata"]), (0.75, 0.5, ["metadata", "write"]),
])
def test_metadata_and_write_share_one_budget(point_create, metadata_delay, write_delay, phases):
    """``timeout`` covers the whole call, not each phase, and expiry raises before the hook.

    Three cases: metadata alone overruns the budget; metadata consumes it
    exactly, leaving nothing for the write; metadata leaves too little for the
    write to finish. The recorded phases show how far the call got, which is
    what distinguishes a shared budget from a per-phase one.

    In every case the hook must not run -- there is no response to hand it.
    """
    point_create.metadata_delay = metadata_delay
    point_create.write_delay = write_delay
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        point_create.call({"id": "item"}, timeout=1, response_hook=hook)
    assert [phase for phase, _ in point_create.events] == phases
    hook.assert_not_called()


def test_create_charges_lazy_initialization_to_budget(point_create):
    """Rust only: starting the driver counts against the caller's timeout.

    The Rust backend builds its driver on first use. If that setup were not
    charged to the budget, a customer's one second timeout could be exceeded
    before any work began. Setup here takes longer than the whole budget, so the
    call must time out with nothing recorded in ``events``.

    The legacy path has no such step, so it returns early.
    """
    if not point_create.rust:
        return
    point_create.init_delay = 2
    with pytest.raises(CosmosClientTimeoutError):
        point_create.call({"id": "item"}, timeout=1)
    assert point_create.events == []


def test_create_serializes_once_before_metadata(point_create, monkeypatch):
    """Rust only: the body is turned into bytes exactly once per create.

    The bytes are needed both to read the partition key and to send, so the easy
    mistake is to serialize twice. For large items that doubles the cost of
    every write. Wrapping the real function and counting calls catches it.
    """
    if not point_create.rust:
        return
    serialize = MagicMock(wraps=_document.serialize_body_to_bytes)
    monkeypatch.setattr(_document, "serialize_body_to_bytes", serialize)
    point_create.call({"id": "item", "pk": "pk"})
    serialize.assert_called_once()


def test_partition_key_and_wire_body_use_the_same_nested_snapshot(point_create):
    """The body is captured once up front, so a caller editing it mid-call cannot split the write.

    The partition key path points into a nested dict. Another thread -- or, as
    here, a callback -- changes that nested value while the metadata lookup is
    in flight. If the partition key and the sent body were each read from the
    live dict at different moments, the item would be routed by one value and
    stored with another, and it would be unfindable.

    Both must use the snapshot taken before the lookup: the sent body still says
    ``before`` even though the caller's dict now says ``after``.
    """
    original = {"id": "item", "tenant": {"key": "before"}}
    point_create.properties["partitionKey"]["paths"] = ["/tenant/key"]
    async_mode = inspect.iscoroutinefunction(point_create.proxy.create_item)
    if point_create.rust:
        point_create.on_metadata = lambda: original["tenant"].update(key="after")
    else:
        metadata = point_create.proxy.read
        original_effect = metadata.side_effect

        def change_caller_during_lookup(*args, **kwargs):
            original["tenant"]["key"] = "after"
            return original_effect(*args, **kwargs)

        metadata.side_effect = change_caller_during_lookup
    result = point_create.call(original)
    assert original["tenant"]["key"] == "after"
    assert result["tenant"]["key"] == "before"
    if point_create.rust:
        assert legacy_partition_key_from_request(point_create.prepared) is None
        assert json.loads(point_create.prepared.body_bytes)["tenant"]["key"] == "before"
        assert point_create.native_calls == 1


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("op", ["create_item", "upsert_item", "replace_item", "patch_item"])
def test_compact_utf8_applies_to_all_singleton_write_bodies(async_mode, compact, op):
    """The compact UTF-8 setting reaches every single-item write, not just create.

    With the setting off, a non-ASCII character is sent as an escape sequence
    (``\\u00e9``); with it on, it is sent as raw UTF-8 bytes, which is smaller.
    The risk is that the setting is wired into create and forgotten elsewhere,
    so upsert, replace and patch are all checked, sync and async.

    Patch carries the character in an operation value rather than a body, which
    is why it builds its arguments differently. Either way the result must still
    parse as JSON.
    """
    backend = AsyncBackend() if async_mode else Backend()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(
        backend, ItemClientDefaults(enable_compact_utf8_item_writes=compact)
    )
    kwargs = (
        {"patch_operations": [{"op": "set", "path": "/label", "value": "\u00e9"}]}
        if op == "patch_item" else {"body": {"id": "item", "pk": "pk", "label": "\u00e9"}}
    )
    invoke(helper, op, **kwargs)
    wire = backend.events[-1].body_bytes
    assert (b"\\u00e9" in wire) != compact
    assert (b"\xc3\xa9" in wire) == compact
    assert json.loads(wire)
