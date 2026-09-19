# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Point-read contract through both public clients and their actual dispatch adapters.

Every test here runs four times -- sync/async crossed with legacy/Rust -- so a
rule proved here is proved for all four combinations a customer can hit. The
container, the proxies and the option-merge helpers are all real; only the
network call at the bottom is faked, along with the clock, so the tests can
assert on exact time budgets without sleeping.

The ``point_read.events`` list is the spine of most assertions. It records
``("metadata", budget)`` and ``("read", budget)`` in the order the call made
them, so a test can prove not just the outcome but that a bad argument was
caught *before* anything was sent.
"""
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import CosmosDict, _operation_deadline
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import binding as sync_rust
from azure.cosmos.aio._backend import binding as async_rust
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._helpers import _item_prep
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos._helpers._response_parse import process_backend_response
from azure.cosmos.exceptions import CosmosAccessConditionFailedError, CosmosClientTimeoutError
from azure.cosmos.partition_key import NonePartitionKeyValue, NullPartitionKeyValue


@pytest.fixture(params=[(False, False), (False, True), (True, False), (True, True)],
                ids=["sync-legacy", "sync-rust", "async-legacy", "async-rust"])
def point_read(request, monkeypatch):
    """Build one read_item call site for each sync/async x legacy/Rust combination.

    Yields a context object whose ``call(...)`` invokes the real public
    ``read_item`` and whose ``events`` list records each network phase with
    the timeout budget it was given. Tests tune ``metadata_delay``,
    ``read_delay``, ``init_delay``, ``status``, ``body`` and ``headers`` to
    stage the situation they need.
    """
    async_mode, rust = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_item_prep, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        clock=clock, events=[], metadata_delay=0.0, read_delay=0.0, init_delay=0.0,
        status=200, body={"id": "item", "nested": {"values": [1]}}, headers={"etag": '"current"'},
        properties={"_rid": "rid", "partitionKey": {"paths": ["/pk"], "kind": "Hash"}},
        rust=rust, native_calls=0, on_metadata=lambda: None,
    )
    link = "dbs/db/colls/c"
    cc = MagicMock()
    cc._container_properties_cache = {}

    def advance(phase, timeout):
        context.events.append((phase, timeout))
        delay = getattr(context, phase + "_delay")
        if timeout is not None and delay > timeout:
            clock.now += timeout
            if rust:
                raise TimeoutError("native point-read budget exhausted")
            raise CosmosClientTimeoutError()
        clock.now += delay

    def reply():
        body = b"" if context.status == 304 else json.dumps(context.body).encode()
        return context.status, 0, dict(context.headers), body, None

    def metadata(_driver_handle, _link, *, timeout_seconds=None):
        advance("metadata", timeout_seconds)
        definition = context.properties.get("partitionKey")
        return (
            context.properties["_rid"], tuple(definition["paths"]) if definition else (),
            definition["kind"] if definition else None, definition.get("systemKey") if definition else None,
        )

    def read(_driver_handle, prepared, *, timeout_seconds=None):
        context.prepared = prepared
        timeout_seconds = resolve_for_item(timeout_seconds)
        advance("read", timeout_seconds)
        return reply()

    def resolve_for_item(timeout_seconds):
        context.native_calls += 1
        started = clock.now
        context.on_metadata()
        metadata("test-handle", link, timeout_seconds=timeout_seconds)
        if timeout_seconds is not None:
            timeout_seconds -= clock.now - started
            if timeout_seconds <= 0:
                raise TimeoutError("native item budget exhausted during metadata")
        return timeout_seconds

    def ensure_driver_handle():
        clock.now += context.init_delay
        return "test-handle"

    def wrap(function):
        return AsyncMock(side_effect=function) if async_mode else MagicMock(side_effect=function)

    if rust:
        module = async_rust if async_mode else sync_rust
        binding = SimpleNamespace(
            read_item=wrap(read), read_item_async=wrap(read),
            get_container_metadata=MagicMock(side_effect=AssertionError("Unexpected metadata FFI call")),
            get_container_metadata_async=MagicMock(side_effect=AssertionError("Unexpected metadata FFI call")),
        )
        monkeypatch.setattr(module, "_rust_module", binding)
        backend_type = async_rust.AsyncRustBinding if async_mode else sync_rust.RustBinding
        backend = backend_type("https://point-read.invalid", master_key="ZmFrZQ==")
        monkeypatch.setattr(backend, "_ensure_driver_handle", wrap(ensure_driver_handle))
    else:
        backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND

    cc._backend = backend
    item_context = ItemClientContext(backend)
    proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        cc, "dbs/db", "c", _item_context=item_context,
    )

    def legacy_metadata(**kwargs):
        advance("metadata", kwargs.get("timeout"))
        assert "etag" not in kwargs and "match_condition" not in kwargs
        assert "response_hook" not in kwargs
        cc._container_properties_cache[link] = context.properties
        return CosmosDict(context.properties, response_headers={})

    def legacy_read(**kwargs):
        context.options = kwargs["options"]
        assert "response_hook" not in kwargs
        assert not {"etag", "match_condition", "_item_operation_deadline"}.intersection(kwargs)
        advance("read", kwargs.get("timeout"))
        response = BackendResponse(*reply())
        result = process_backend_response(response)
        cc.last_response_headers = result.get_response_headers()
        return result

    proxy.read = wrap(legacy_metadata)
    cc.ReadItem = wrap(legacy_read)

    def call(*args, **kwargs):
        result = proxy.read_item(*args, **kwargs)
        return asyncio.run(result) if inspect.isawaitable(result) else result

    context.resolve_for_item = resolve_for_item
    context.call, context.proxy, context.cc, context.state = call, proxy, cc, item_context.response_state
    yield context
    if rust:
        binding.get_container_metadata.assert_not_called()
        binding.get_container_metadata_async.assert_not_called()
        closed = backend.close()
        if inspect.isawaitable(closed):
            asyncio.run(closed)


@pytest.mark.parametrize("value", [None, False, True, 0])
def test_retired_metrics_are_rejected_by_presence_before_metadata(point_read, value):
    """``populate_query_metrics`` is rejected whenever it is supplied at all.

    The argument was retired. Rejection is by presence, not by truthiness, so
    even ``None`` or ``False`` raises rather than being quietly ignored. A
    customer removing this argument gets a clear error instead of silently
    losing whatever they thought it did, and nothing is sent to the service.
    """
    with pytest.raises(TypeError, match="populate_query_metrics"):
        point_read.call("item", "pk", populate_query_metrics=value)
    assert point_read.events == []


def test_only_item_and_partition_key_are_positional(point_read):
    """Only ``item`` and ``partition_key`` may be passed positionally.

    Everything else is keyword-only, so the SDK can add or reorder options
    later without silently changing what an existing customer call means. A
    third positional argument raises before anything is sent.
    """
    signature = inspect.signature(point_read.proxy.read_item)
    assert [name for name, parameter in signature.parameters.items()
            if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD] == ["item", "partition_key"]
    for name in ("etag", "match_condition", "post_trigger_include", "response_hook"):
        assert signature.parameters[name].kind == inspect.Parameter.KEYWORD_ONLY
    with pytest.raises(TypeError):
        point_read.call("item", "pk", None)
    assert point_read.events == []


@pytest.mark.parametrize("kwargs,error", [
    ({"etag": '"v1"'}, ValueError),
    ({"match_condition": MatchConditions.IfModified}, ValueError),
    ({"etag": "", "match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": "invalid"}, TypeError),
])
def test_invalid_conditions_fail_before_metadata(point_read, kwargs, error):
    """A half-specified or malformed access condition fails before any request.

    ``etag`` and ``match_condition`` only mean something together, so either
    one alone is an error, as is an empty etag or a ``match_condition`` that
    is not a ``MatchConditions`` member. Failing up front means the
    customer's traceback points at their own call, not at a service reply.
    """
    with pytest.raises(error):
        point_read.call("item", "pk", **kwargs)
    assert point_read.events == []


@pytest.mark.parametrize("condition,kind,value", [
    (MatchConditions.IfModified, "IfNoneMatch", '"v1"'),
    (MatchConditions.IfNotModified, "IfMatch", '"v1"'),
    (MatchConditions.IfMissing, "IfNoneMatch", "*"),
    (MatchConditions.IfPresent, "IfMatch", "*"),
])
def test_conditions_and_options_are_isolated(point_read, condition, kind, value):
    """Each match condition maps to the right header, and the caller's dict is left alone.

    ``IfModified``/``IfMissing`` become ``If-None-Match``;
    ``IfNotModified``/``IfPresent`` become ``If-Match``; the two "existence"
    conditions use ``*``. The ``request_options`` dict the customer passed in
    must come back unchanged, because customers reuse one options dict across
    many calls and a mutation would leak a condition into later reads.
    """
    supplied = {"initialHeaders": {"x-customer": "kept"}}
    result = point_read.call("item", "pk", etag='"v1"', match_condition=condition, request_options=supplied)
    assert supplied == {"initialHeaders": {"x-customer": "kept"}}
    assert result["id"] == "item"
    if point_read.rust:
        headers = CaseInsensitiveDict(wire_headers(point_read.prepared))
        assert headers["if-match" if kind == "IfMatch" else "if-none-match"] == value
    else:
        assert point_read.options["accessCondition"] == {"type": kind, "condition": value}
        assert point_read.options["initialHeaders"]["x-customer"] == "kept"


@pytest.mark.parametrize("status", [200, 304])
def test_hook_receives_independent_cosmosdict_and_headers_even_when_falsey(point_read, status):
    """The response hook runs even if it is falsey, and cannot corrupt the result.

    A hook object whose ``__bool__`` is False is still a supplied callback,
    so it must be called -- testing the hook for truthiness instead of for
    ``None`` would silently drop it. Whatever the hook does to the body and
    headers it receives must not show up in what the caller gets back, on
    either a 200 or an empty 304.
    """
    point_read.status = status
    snapshots = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert isinstance(body, CosmosDict)
            assert body.get_response_headers()["etag"] == '"current"'
            assert (not body) == (status == 304)
            headers["etag"] = "hook-header"
            assert body.get_response_headers()["etag"] == '"current"'
            body._response_headers["etag"] = "hook-body-header"
            if body:
                body["nested"]["values"].append(2)
            body["added"] = True
            snapshots.append((headers, body))

    result = point_read.call("item", "pk", response_hook=Hook())
    assert isinstance(result, CosmosDict)
    assert "added" not in result
    assert result.get_response_headers()["etag"] == '"current"'
    assert result == ({} if status == 304 else {"id": "item", "nested": {"values": [1]}})
    state = point_read.state.last_response_headers if point_read.rust else point_read.cc.last_response_headers
    assert state["etag"] == '"current"'
    assert len(snapshots) == 1
    assert [phase for phase, _ in point_read.events] == ["metadata", "read"]


def test_hook_exception_is_not_replayed(point_read):
    """If the customer's hook raises, that exact error surfaces and the read is not repeated.

    The hook runs after a successful reply, so a failure inside it is the
    customer's bug, not a transport fault. Retrying would send the read
    twice and call the hook twice.
    """
    error = NotImplementedError("customer callback")
    hook = MagicMock(side_effect=error)
    with pytest.raises(NotImplementedError) as raised:
        point_read.call("item", "pk", response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert [phase for phase, _ in point_read.events] == ["metadata", "read"]


def test_service_412_is_preserved_and_does_not_invoke_success_hook(point_read):
    """A 412 from the service becomes the typed error, and the success hook stays silent.

    The hook is a success callback. Firing it on a failed precondition would
    let a customer treat a rejected read as a completed one.
    """
    point_read.status = 412
    hook = MagicMock()
    with pytest.raises(CosmosAccessConditionFailedError):
        point_read.call("item", "pk", etag='"old"', match_condition=MatchConditions.IfNotModified,
                        response_hook=hook)
    hook.assert_not_called()


def test_stale_if_match_does_not_invent_local_412(point_read):
    """Pass through the fixture's successful read despite a stale supplied etag.

    The fake response supplies the current etag. This checks that Python does
    not invent a 412, not how a real service evaluates the precondition.
    """
    result = point_read.call("item", "pk", etag='"old"', match_condition=MatchConditions.IfNotModified)
    assert result["id"] == "item"
    assert result.get_response_headers()["etag"] == '"current"'


@pytest.mark.parametrize("timeout", [0, -1, 0.5, True, "2", float("nan"), float("inf"), 2**64, 10**1000])
def test_invalid_timeout_fails_before_metadata(point_read, timeout):
    """A timeout that isn't a usable positive duration is rejected up front.

    Zero and negatives mean "no time at all", booleans and strings are the
    wrong type, NaN and infinity cannot be compared against a clock, and
    huge integers overflow the driver's duration type. All are caught before
    any request so the customer never gets a confusing transport error.
    """
    with pytest.raises(ValueError, match="timeout"):
        point_read.call("item", "pk", timeout=timeout)
    assert point_read.events == []


def test_remaining_subsecond_budget_reaches_item_without_rounding(point_read):
    """Time left over after resolving the container is passed on exactly.

    Metadata takes 0.75s of a 1s budget, so the read must be given 0.25s --
    not 0 (which would fail a call that had time left) and not 1 (which
    would let the two phases together run for almost twice the budget).
    """
    point_read.metadata_delay = 0.75
    point_read.read_delay = 0.125
    result = point_read.call("item", "pk", timeout=1)
    assert result["id"] == "item"
    assert point_read.events == [("metadata", 1), ("read", 0.25)]


def test_metadata_timeout_never_dispatches_item(point_read):
    """If resolving the container uses up the budget, the read is never sent.

    The customer asked for the whole call to finish within the timeout, so
    once it is gone there is no time left to spend on the read itself. The
    success hook must not fire either.
    """
    point_read.metadata_delay = 2
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        point_read.call("item", "pk", timeout=1, response_hook=hook)
    assert point_read.events == [("metadata", 1)]
    hook.assert_not_called()


def test_combined_phases_cannot_each_restart_budget(point_read):
    """The timeout covers the whole call, not each phase separately.

    Metadata takes 0.75s and the read 0.5s. Neither exceeds the 1s budget on
    its own, but together they do, so the call must fail and the clock must
    show exactly 1s spent. If each phase got its own fresh budget, a
    ``timeout=1`` call could run for 1.25s and still be reported a success.
    """
    point_read.metadata_delay = 0.75
    point_read.read_delay = 0.5
    with pytest.raises(CosmosClientTimeoutError):
        point_read.call("item", "pk", timeout=1)
    assert point_read.events == [("metadata", 1), ("read", 0.25)]
    assert point_read.clock.now == 101


def test_no_read_after_metadata_uses_exact_budget(point_read):
    """Using the budget exactly, with nothing left over, still stops the call.

    The boundary case of the test above: metadata consumes the full 1s. Zero
    remaining is not "a tiny bit remaining", so the read is not attempted.
    """
    point_read.metadata_delay = 1
    with pytest.raises(CosmosClientTimeoutError):
        point_read.call("item", "pk", timeout=1)
    assert point_read.events == [("metadata", 1)]


def test_lazy_driver_handle_initialization_consumes_budget(point_read):
    """Starting the driver on the first call counts against the customer's timeout.

    The Rust driver is built on first use. That setup is time the customer
    is waiting, so it comes out of the budget: if it alone exceeds the
    timeout, the call fails having sent nothing. Rust only -- the legacy
    path has no driver to start.
    """
    if not point_read.rust:
        return
    point_read.init_delay = 2
    with pytest.raises(CosmosClientTimeoutError):
        point_read.call("item", "pk", timeout=1)
    assert point_read.events == []


def test_expired_cache_lock_does_not_start_metadata(point_read):
    """Time spent queueing behind another call's cache refresh also counts.

    When several calls race to resolve the same container, only one refreshes
    and the rest wait on a lock. That wait is charged to the budget, so a
    call that waited past its timeout stops instead of starting a request it
    has no time for -- and the lock is released either way. Legacy only --
    the Rust path caches inside the driver and takes no such lock.
    """
    if point_read.rust:
        return
    acquired = []

    def acquire(**kwargs):
        acquired.append(kwargs.get("timeout"))
        point_read.clock.now += 2
        return True

    lock = MagicMock()
    lock.acquire = AsyncMock(side_effect=acquire) if inspect.iscoroutinefunction(
        point_read.proxy.read_item
    ) else MagicMock(side_effect=acquire)
    point_read.proxy.container_cache_lock = lock
    with pytest.raises(CosmosClientTimeoutError):
        point_read.call("item", "pk", timeout=1)
    assert len(acquired) == 1
    lock.release.assert_called_once()
    assert point_read.events == []


@pytest.mark.parametrize("method", [
    "read_item", "read_item_async", "get_container_metadata", "get_container_metadata_async",
    "create_item", "create_item_async",
])
@pytest.mark.parametrize("seconds", [0, -1, float("nan"), float("inf"), 2**64])
def test_native_remaining_timeout_rejects_invalid_durations_without_dispatch(method, seconds):
    """The binding re-checks the timeout itself, for every entry point it exposes.

    The Python layer already rejects these values, but the binding is a
    public boundary and must not trust its caller: an unusable duration has
    to raise before the driver is invoked. Checked on every exported
    function so a newly added one cannot quietly skip the check. The driver
    handle is deliberately invalid -- if validation ever stopped running
    first, the call would fail with a different, unmistakable error.
    """
    from azure.cosmos._backend.contracts import PreparedRequest
    binding = pytest.importorskip("azure.cosmos._rust")
    prepared = PreparedRequest(
        method.removesuffix("_async"), "dbs/db/colls/c", b'{"id":"item"}',
        key_from_legacy_header('["pk"]'), item_id="item",
    )
    argument = prepared if method.startswith(("read_item", "create_item")) else prepared.container_link
    argument_name = "prepared" if method.startswith(("read_item", "create_item")) else "container_link"
    with pytest.raises(ValueError, match="timeout_seconds"):
        getattr(binding, method)(
            driver_handle="invalid-driver-handle", **{argument_name: argument}, timeout_seconds=seconds
        )


@pytest.mark.parametrize("key", [None, NullPartitionKeyValue, NonePartitionKeyValue])
@pytest.mark.parametrize("system_key", [False, True])
def test_partition_key_sentinels_preserve_native_unknown_system_key_fallback(point_read, key, system_key):
    """The three "no partition key value" spellings each keep their own meaning.

    ``None`` and ``NullPartitionKeyValue`` both mean a stored JSON null and
    go on the wire as ``[null]``; ``NonePartitionKeyValue`` means the
    property is absent from the item and goes as ``[{}]``. They are not
    interchangeable -- swapping them reads a different row. This holds
    whether or not the container uses a system key, and the container is
    resolved once, not once per spelling.
    """
    point_read.properties["partitionKey"]["systemKey"] = system_key
    point_read.metadata_delay = 0.75
    point_read.call("item", key, timeout=1)
    assert point_read.events == [("metadata", 1), ("read", 0.25)]
    if point_read.rust:
        # The actual driver never retains the fixture's systemKey field.
        expected = "[{}]" if key == NonePartitionKeyValue else "[null]"
        assert legacy_partition_key_from_request(point_read.prepared) == expected
        assert point_read.native_calls == 1
