# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Patch contract through both public clients, against the real Rust dispatch adapters.

Unlike the create and read contract files, every test here runs twice --
sync-Rust and async-Rust -- because patch is a Rust-only path in this
migration. The legacy column is covered separately by the parity files and
by ``sync/test_container_patch_item_regression_unit.py``.

Patch differs from the other single-item writes in three ways that drive
most of these tests:

* the caller sends an **operations list**, not a body, so "invalid input"
  means a malformed operation rather than a malformed item;
* an ``If-Match`` guard is the normal case (read-modify-write), and there
  are many spellings of it that must all land on the same header;
* several options the other writes accept are simply not implemented here,
  and must say so loudly rather than being ignored.

``rust_patch.events`` records ``("metadata", budget)`` and
``("patch", budget)`` in order, so a test can prove an argument was
rejected *before* anything reached the network.
"""
from common.typed_requests import wire_headers, settings_options, legacy_settings

import asyncio
import inspect
import json
from dataclasses import replace
from types import MappingProxyType
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosDict
from azure.cosmos._backend import rust_backend as sync_rust
from azure.cosmos.aio._backend import rust_backend as async_rust
from azure.cosmos._helpers import _item_prep
from azure.cosmos._helpers._item_context import ItemClientDefaults
from azure.cosmos.exceptions import (
    CosmosAccessConditionFailedError,
    CosmosClientTimeoutError,
    CosmosHttpResponseError,
)
from read_item.test_read_item_contract_unit import point_read

pytestmark = pytest.mark.parametrize(
    "point_read",
    [(False, True), (True, True)],
    indirect=True,
    ids=["sync-rust", "async-rust"],
)


@pytest.fixture
def point_patch(point_read, monkeypatch):
    """Reuse the point-read harness and repoint it at ``patch_item``.

    Replaces the Rust binding's ``patch_item`` with a fake that records
    ``("patch", budget)``, fails when the remaining budget is smaller than
    ``write_delay``, and returns an empty payload when the request asked for
    no response body.

    ``context.mutate`` is the hook that lets a test change the caller's own
    arguments while the metadata lookup is in flight -- that is how the
    snapshot test proves the inputs were copied up front.

    ``call`` always patches item ``"item"`` in partition ``"pk"``, defaulting
    to a single ``set`` operation, so individual tests only state what they
    are actually varying.
    """
    context = point_read
    context.write_delay = 0
    context.mutate = lambda: None
    monkeypatch.setattr(_item_prep, "time", context.clock)
    async_mode = inspect.iscoroutinefunction(context.proxy.patch_item)

    def patch(_handle, prepared, *, timeout_seconds=None):
        context.prepared = prepared
        timeout_seconds = context.resolve_for_item(timeout_seconds)
        context.events.append(("patch", timeout_seconds))
        if timeout_seconds is not None and context.write_delay > timeout_seconds:
            context.clock.now += timeout_seconds
            raise TimeoutError("native patch budget exhausted")
        context.clock.now += context.write_delay
        body = context.body if context.status < 400 else {"message": "patch rejected"}
        encoded = (
            b""
            if settings_options(prepared).get("responsePayloadOnWriteDisabled")
            else json.dumps(body).encode()
        )
        return context.status, 0, dict(context.headers), encoded, None

    if context.rust:
        binding = (async_rust if async_mode else sync_rust)._rust_module
        context.on_metadata = lambda: context.mutate()
        setattr(
            binding,
            "patch_item_async" if async_mode else "patch_item",
            (
                AsyncMock(side_effect=patch)
                if async_mode
                else MagicMock(side_effect=patch)
            ),
        )

    def call(operations=None, **kwargs):
        result = context.proxy.patch_item(
            "item",
            "pk",
            (
                operations
                if operations is not None
                else [{"op": "set", "path": "/n", "value": 2}]
            ),
            **kwargs,
        )
        return asyncio.run(result) if inspect.isawaitable(result) else result

    context.call = call
    return context


@pytest.fixture
def rust_patch(point_patch):
    """Readable alias for ``point_patch``; patch only runs on the Rust path here."""
    return point_patch


@pytest.mark.parametrize(
    "kwargs,etag",
    [
        ({"etag": '"v1"', "match_condition": MatchConditions.IfNotModified}, '"v1"'),
        ({"etag": '"ignored"', "match_condition": MatchConditions.IfPresent}, "*"),
        ({"if_match": '"v1"'}, '"v1"'),
        ({"access_condition": {"type": "IfMatch", "condition": '"v1"'}}, '"v1"'),
        (
            {
                "request_options": {
                    "accessCondition": {"type": "IfMatch", "condition": '"v1"'}
                }
            },
            '"v1"',
        ),
        ({"initial_headers": {"IF-MATCH": '"v1"'}}, '"v1"'),
        ({"request_options": {"If-Match": '"v1"'}}, '"v1"'),
    ],
)
def test_if_match_reaches_patch_without_replay(rust_patch, kwargs, etag):
    """Inspect equivalent If-Match settings through the test's header-view helper.

    The fake binding records one patch phase and legacy PatchItem is untouched.
    The header view is not a capture of actual native HTTP serialization.
    """
    rust_patch.call(**kwargs)
    assert wire_headers(rust_patch.prepared)["if-match"] == etag
    assert [phase for phase, _ in rust_patch.events] == ["metadata", "patch"]
    rust_patch.cc.PatchItem.assert_not_called()


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"etag": '"v1"'}, ValueError),
        ({"if_match": ""}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfMissing}, NotImplementedError),
        ({"if_none_match": '"v1"'}, NotImplementedError),
        ({"initial_headers": {"If-None-Match": "*"}}, NotImplementedError),
        ({"request_options": {"if-none-match": "*"}}, NotImplementedError),
        (
            {"access_condition": {"type": "IfNoneMatch", "condition": "*"}},
            NotImplementedError,
        ),
        ({"access_condition": {"type": "invalid", "condition": "*"}}, ValueError),
        ({"access_condition": {"type": "IfMatch", "condition": 1}}, ValueError),
        ({"if_match": '"v1"', "initial_headers": {"IF-MATCH": '"v2"'}}, ValueError),
        ({"initial_headers": {"if-match": '"v1"', "IF-MATCH": '"v2"'}}, ValueError),
        ({"filter_predicate": "FROM c WHERE c.n = 1"}, NotImplementedError),
        ({"request_options": {"filterPredicate": "FROM c"}}, NotImplementedError),
        ({"response_hook": False}, TypeError),
        ({"read_timeout": 2}, NotImplementedError),
        ({"retry_write": 0}, NotImplementedError),
    ],
)
def test_invalid_or_unsupported_options_fail_before_io(rust_patch, kwargs, error):
    """Bad and not-yet-supported options raise before any request is sent.

    Two kinds of failure, deliberately given different types:

    * ``ValueError`` -- the argument is wrong. An ``etag`` with no
      ``match_condition``, an empty ``if_match``, a malformed
      ``access_condition``, or the same guard supplied twice with conflicting
      values (the SDK must not silently pick a winner).
    * ``NotImplementedError`` -- the argument is valid Cosmos usage that this
      path does not support yet: any ``If-None-Match`` form, a
      ``filter_predicate``, ``read_timeout``, ``retry_write``.

    The distinction matters to a customer: one says "fix your call", the
    other says "this does not work here yet". Neither may reach the service,
    which the empty ``events`` list proves.
    """
    with pytest.raises(error):
        rust_patch.call(**kwargs)
    assert rust_patch.events == []


@pytest.mark.parametrize(
    "timeout", [0, -1, 0.5, float("nan"), float("inf"), "1", True, 2**64]
)
@pytest.mark.parametrize("nested", [False, True])
def test_invalid_timeout_fails_before_io(rust_patch, timeout, nested):
    """An unusable ``timeout`` is rejected up front, whether passed directly or nested.

    Covers zero and negative values, a value too small to be meaningful,
    ``nan`` and ``inf``, a string, a bool, and a number too large to convert.
    Each must raise ``ValueError`` naming ``timeout`` rather than being
    clamped, ignored, or passed down to overflow inside the driver.

    Running each case both as ``timeout=`` and inside ``request_options``
    proves the same validation covers both entry points.
    """
    kwargs = (
        {"request_options": {"timeout": timeout}} if nested else {"timeout": timeout}
    )
    with pytest.raises(ValueError, match="timeout"):
        rust_patch.call(**kwargs)
    assert rust_patch.events == []


@pytest.mark.parametrize("metadata_delay,write_delay", [(2, 0), (1, 0), (0.75, 0.5)])
def test_one_deadline_covers_metadata_and_patch(
    rust_patch, metadata_delay, write_delay
):
    """``timeout`` covers metadata and the patch together, and expiry skips the hook.

    Three cases: the metadata lookup alone overruns the budget; it consumes
    the budget exactly, leaving nothing; it leaves too little for the patch to
    finish. All three must surface as ``CosmosClientTimeoutError``.

    The response hook must not run -- there is no response to give it.
    """
    rust_patch.metadata_delay, rust_patch.write_delay = metadata_delay, write_delay
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        rust_patch.call(timeout=1, response_hook=hook)
    hook.assert_not_called()


def test_subsecond_remaining_budget_reaches_binding(rust_patch):
    """Time spent on metadata is deducted, and the fraction left is handed to the patch.

    A one second budget less a 0.75 second lookup leaves 0.25 seconds, which
    must reach the binding as a fraction. Rounding down to zero would abandon
    a call that still had time; rounding up would overrun the budget.

    The prepared request must carry no ``deadline`` attribute: the remaining
    time travels as the call's timeout, not as an absolute deadline baked
    into the request.
    """
    rust_patch.metadata_delay = 0.75
    rust_patch.call(timeout=1)
    assert rust_patch.events == [("metadata", 1), ("patch", 0.25)]
    assert not hasattr(rust_patch.prepared, "deadline")


def test_lazy_initialization_uses_the_same_budget(rust_patch):
    """Starting the Rust driver counts against the caller's timeout.

    The driver is built on first use. If that setup were not charged to the
    budget, a one second timeout could be exceeded before any work started.
    Setup here outlasts the whole budget, so the call must time out with
    nothing recorded in ``events``.
    """
    rust_patch.init_delay = 2
    with pytest.raises(CosmosClientTimeoutError):
        rust_patch.call(timeout=1)
    assert rust_patch.events == []


def test_inputs_are_snapshotted_before_metadata(rust_patch):
    """Everything the caller passes is copied up front, so later edits cannot change the request.

    While the metadata lookup is in flight, the caller mutates all three
    inputs: a value nested inside an operation, a header dict, and an
    excluded-locations list. None of those changes may appear in the request
    that is ultimately sent.

    Without an up-front copy, a customer reusing an options dict across
    concurrent calls would see one call's arguments leak into another.

    ``request_options`` is passed read-only, so any attempt to write the
    partition key back into the caller's mapping fails the test outright.
    """
    operations = [{"op": "set", "path": "/data", "value": {"nested": [1]}}]
    initial = {"x-trace": "original"}
    exclusions = ["West US"]
    options = {"initialHeaders": initial, "excludedLocations": exclusions}

    def mutate():
        operations[0]["value"]["nested"].append(2)
        initial["x-trace"] = "changed"
        exclusions.append("East US")

    rust_patch.mutate = mutate
    rust_patch.call(operations, request_options=MappingProxyType(options))
    assert "partitionKey" not in options
    assert json.loads(rust_patch.prepared.body_bytes)["operations"][0]["value"] == {
        "nested": [1]
    }
    assert wire_headers(rust_patch.prepared)["x-trace"] == "original"
    assert settings_options(rust_patch.prepared)["excludedLocations"] == ["West US"]


@pytest.mark.parametrize(
    "operations,error",
    [
        ([], ValueError),
        ({}, TypeError),
        ([1], TypeError),
        ([{"op": "set", "path": "/n", "value": float("nan")}], ValueError),
        ([{"op": "set", "path": "/n", "value": object()}], TypeError),
    ],
)
def test_invalid_payload_fails_before_io(rust_patch, operations, error):
    """A malformed operations list is rejected locally, not by the service.

    An empty list has nothing to do, a mapping is the wrong container, a list
    of non-operations has no ``op`` to read, and a value that JSON cannot
    represent (``nan``, an arbitrary object) cannot be serialised.

    Catching these locally turns a confusing service error into an immediate,
    specific one, and costs the customer no request.
    """
    with pytest.raises(error):
        rust_patch.call(operations)
    assert rust_patch.events == []


@pytest.mark.parametrize("no_response", [False, True])
def test_hooks_get_independent_snapshots(rust_patch, no_response):
    """A falsey response hook still runs, and its edits stay inside its own copy.

    ``Hook.__bool__`` returns ``False``, so any layer testing the hook with a
    plain truth check would skip it. It must still run exactly once.

    Whatever the hook writes -- the headers it is handed, the body's response
    headers, a nested list inside the body -- must not reach the caller's
    result or the stored last-response headers. Both the populated body and
    the empty one are covered.
    """
    seen = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert isinstance(body, CosmosDict)
            headers["etag"] = "hook"
            body._response_headers["etag"] = "body-hook"
            if body:
                body["nested"]["values"].append(2)
            body["added"] = True
            seen.append(body)

    result = rust_patch.call(no_response=no_response, response_hook=Hook())
    assert result == ({} if no_response else {"id": "item", "nested": {"values": [1]}})
    assert result.get_response_headers()["etag"] == '"current"'
    assert rust_patch.state.last_response_headers["etag"] == '"current"'
    assert len(seen) == 1


def test_hook_failure_does_not_replay_write(rust_patch):
    """If the customer's hook raises, the patch is not applied a second time.

    The hook runs after the patch has already succeeded. The exception it
    raises is a ``TimeoutError``, which the retry machinery would normally
    find tempting -- so this test proves it is passed straight through
    (the same object) rather than triggering a replay that would apply the
    operations twice.
    """
    error = TimeoutError("customer hook")
    hook = MagicMock(side_effect=error)
    with pytest.raises(TimeoutError) as raised:
        rust_patch.call(response_hook=hook, timeout=1)
    assert raised.value is error
    assert [phase for phase, _ in rust_patch.events] == ["metadata", "patch"]
    hook.assert_called_once()


@pytest.mark.parametrize(
    "status,error",
    [(400, CosmosHttpResponseError), (412, CosmosAccessConditionFailedError)],
)
def test_error_tuple_stays_typed_and_never_invokes_success_hook(
    rust_patch, status, error
):
    """Service errors keep their specific type and status, and skip the hook.

    A 400 becomes ``CosmosHttpResponseError``; a 412 (the version guard
    failed) becomes ``CosmosAccessConditionFailedError``, which is the one a
    read-modify-write loop catches to retry. Both must carry the original
    status code, and neither may invoke the success hook.
    """
    rust_patch.status = status
    hook = MagicMock()
    with pytest.raises(error) as raised:
        rust_patch.call(response_hook=hook)
    assert raised.value.status_code == status
    hook.assert_not_called()


def test_client_defaults_and_per_call_overrides(rust_patch):
    """Client-level defaults apply to a patch, and per-call arguments override them.

    The client is configured to suppress response bodies and to send a
    priority and throughput bucket. A bare call must honour all three. The
    same call with explicit arguments must win on all three.

    This is checked on the wire headers rather than on the options dict, so a
    default that is recorded but never sent would still fail.
    """
    context = rust_patch.proxy._item_context
    rust_patch.proxy._item_context = replace(
        context,
        defaults=ItemClientDefaults(
            no_response_on_write=True,
            priority="Low",
            throughput_bucket=2,
        ),
    )
    assert rust_patch.call() == {}
    assert wire_headers(rust_patch.prepared)["x-ms-cosmos-priority-level"] == "Low"
    assert wire_headers(rust_patch.prepared)["x-ms-cosmos-throughput-bucket"] == "2"
    assert rust_patch.call(no_response=False, priority="High", throughput_bucket=3)
    assert wire_headers(rust_patch.prepared)["x-ms-cosmos-priority-level"] == "High"
    assert wire_headers(rust_patch.prepared)["x-ms-cosmos-throughput-bucket"] == "3"


def test_async_cancellation_drains_single_native_call(rust_patch):
    """Cancellation unwinds the fake async binding coroutine and skips the hook.

    Assert one patch await, no metadata-entry call, and the coroutine's finally
    marker. No real driver task, socket cleanup, or service rollback is observed.
    """
    if not inspect.iscoroutinefunction(rust_patch.proxy.patch_item):
        pytest.skip("Async cancellation contract.")

    async def run():
        started, stopped = asyncio.Event(), asyncio.Event()

        async def blocked(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                stopped.set()

        binding = async_rust._rust_module
        binding.patch_item_async.side_effect = blocked
        hook = MagicMock()
        task = asyncio.create_task(
            rust_patch.proxy.patch_item(
                "item",
                "pk",
                [{"op": "incr", "path": "/n", "value": 1}],
                timeout=1,
                response_hook=hook,
            )
        )
        await asyncio.wait_for(started.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stopped.is_set()
        hook.assert_not_called()
        binding.get_container_metadata_async.assert_not_called()
        binding.patch_item_async.assert_awaited_once()

    asyncio.run(run())
