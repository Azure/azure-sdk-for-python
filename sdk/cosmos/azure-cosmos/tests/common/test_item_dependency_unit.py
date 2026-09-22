# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for who prepares an item call and what it is allowed to remember (no network).

Two concerns run through this file.

The first is that preparation happens exactly once, in one place. An item call
passes through a public method, a helper, and a request builder, and each could
plausibly normalize the arguments. Doing it twice is not harmless: deadlines get
recomputed from a later start, defaults get applied to values that already have
them, and the caller's own options risk being consumed along the way.

The second is that the two paths address items differently, and neither should
inherit the other's way. The legacy path builds a link out of the container
address and the item id; the Rust path sends the id and lets the driver work out
the rest. Keeping a link on the Rust path would be dead weight that looks
authoritative, and it is exactly the sort of thing that later gets trusted.

Around both sits a smaller theme: helpers are reused for speed, so the tests
here check that a reused helper holds nothing belonging to a particular call and
does not keep the container object alive after the customer drops it.
"""

import asyncio
import gc
import inspect
import threading
import weakref
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import CosmosDict
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._helpers import _item_prep, _response_parse
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos._helpers._item_operations import ItemHelper, normalize_item_arguments
from azure.cosmos._helpers._legacy_item_operations import (
    LegacyItemHelper,
    prepare_legacy_item_arguments,
)
from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper
from azure.cosmos.aio._helpers._legacy_item_operations import AsyncLegacyItemHelper
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import rust_backend as sync_rust
from azure.cosmos.aio._backend import rust_backend as async_rust
from common.test_connection_free_items_unit import Backend, AsyncBackend
from create_item.test_create_item_contract_unit import point_create
from read_item.test_read_item_contract_unit import point_read


def finish(value):
    """Run a call to completion whether it is asynchronous or not.

    Lets a single test body cover both clients instead of being written twice
    with the only difference being an await.
    """
    return asyncio.run(value) if inspect.isawaitable(value) else value


@pytest.mark.parametrize("timeout", [None, 2.0])
def test_create_prepares_once_even_without_a_timeout(
    point_create, monkeypatch, timeout
):
    """Working out the deadline happens exactly once per call, with and without a timeout.

    The step is counted, and it runs once either way. With no timeout there is
    nothing to compute, which is precisely when it is tempting to skip the step
    and then repeat it further down "just in case" -- leaving two answers for
    when the call should give up.

    It is told which operation it is preparing, since different operations get
    different treatment, and it is not handed any leftover internal marker of an
    earlier deadline. The caller's options come back unchanged.
    """
    prepare = MagicMock(wraps=_item_prep.prepare_item_deadline)
    monkeypatch.setattr(_item_prep, "prepare_item_deadline", prepare)
    options = {"initialHeaders": {"x-app": "original"}}
    point_create.call({"id": "item"}, timeout=timeout, request_options=options)
    prepare.assert_called_once()
    assert prepare.call_args.args[1] == "create_item"
    assert "_item_operation_deadline" not in prepare.call_args.args[0]
    assert options == {"initialHeaders": {"x-app": "original"}}


@pytest.mark.parametrize(
    "helper_type",
    [ItemHelper, AsyncItemHelper, LegacyItemHelper, AsyncLegacyItemHelper],
)
def test_create_helper_requires_an_explicit_optional_budget(helper_type):
    """All four helpers insist on being told the deadline, by name, with no default.

    Both clients and both paths are covered. The deadline may be nothing, but it
    has to be passed -- omitting it is an error.

    A default would be the quiet bug. A caller who forgot to pass the remaining
    time would get a call with no deadline at all rather than a failure, so the
    customer's timeout would be honored on some routes and ignored on others,
    depending only on which call site remembered.

    Requiring it by name also stops it being confused with the other numbers in
    these signatures.
    """
    parameter = inspect.signature(helper_type.create_item).parameters["deadline"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    with pytest.raises(TypeError, match="deadline"):
        helper_type.create_item(
            None, container_link="dbs/d/colls/c", body={"id": "item"}
        )


@pytest.mark.parametrize(
    "normalize", [normalize_item_arguments, prepare_legacy_item_arguments]
)
@pytest.mark.parametrize("deadline", [None, 101.0])
def test_create_budget_is_explicit_not_inferred_from_a_marker(normalize, deadline):
    """The deadline comes from the argument, and a stray internal marker in the options is
    ignored and removed.

    Both paths are given options carrying an old internal deadline marker with a
    conspicuous value, and both use the argument instead -- including when the
    argument is nothing at all. The marker does not survive into what gets sent.

    That marker is how the deadline used to travel. Still reading it would mean
    a caller who reuses an options object from an earlier call silently inherits
    the old call's deadline, which by then is in the past, and their new call
    times out immediately for no visible reason.
    """
    args, _ = normalize(
        "create_item",
        {
            "container_link": "dbs/d/colls/c",
            "body": {"id": "item"},
            "_item_operation_deadline": 999.0,
        },
        deadline=deadline,
    )
    assert args["deadline"] == deadline
    assert "_item_operation_deadline" not in args["kwargs"]


@pytest.mark.parametrize("async_mode", [False, True])
def test_rust_helper_never_repeats_public_create_preparation(monkeypatch, async_mode):
    """The helper does not redo the preparation the public method already did.

    The public preparation step is replaced with something that fails if called,
    and a create through the helper succeeds without touching it, producing
    exactly one call to the backend.

    Repeating it would not usually raise -- that is what makes it worth a test.
    It would apply defaults a second time, to values that already have them, and
    restart the deadline from a later moment, so the customer's timeout would
    quietly stretch.
    """
    forbidden = MagicMock(
        side_effect=AssertionError("helper repeated public preparation")
    )
    monkeypatch.setattr(_item_prep, "prepare_create_item_kwargs", forbidden)
    backend = AsyncBackend() if async_mode else Backend()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend)
    finish(
        helper.create_item(
            container_link="dbs/d/colls/c", body={"id": "item"}, deadline=None
        )
    )
    forbidden.assert_not_called()
    assert len(backend.events) == 1


@pytest.mark.parametrize("async_mode", [False, True])
def test_rust_helper_reuse_is_context_scoped_and_does_not_retain_proxy(async_mode):
    """A container reuses one helper across calls, rebuilds it when its settings change, and
    does not keep the container alive.

    Choosing which backend to use happens once, not per call, and two creates go
    through the same helper. Repeating that choice on every item operation would
    be pure overhead on the hottest path in the SDK.

    When the container's defaults are replaced the helper is rebuilt, because a
    helper carries those defaults. Keeping the old one would leave the customer
    changing a setting and seeing no effect.

    Finally the container is dropped and confirmed collected. A cached helper
    that pointed back at its container would form a loop that keeps every
    container object alive for the life of the program -- a slow leak in exactly
    the applications that create containers dynamically.
    """
    base = AsyncBackend if async_mode else Backend

    class CountingBackend(base):
        selections = 0

        @property
        def name(self):
            self.selections += 1
            return "rust"

    backend = CountingBackend()
    context = ItemClientContext(backend)
    proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        None, "dbs/d", "c", _item_context=context
    )
    helper = proxy._get_item_helper()
    finish(proxy.create_item({"id": "one"}))
    finish(proxy.create_item({"id": "two"}))
    assert proxy._get_item_helper() is helper
    assert backend.selections == 1
    assert len(backend.events) == 2
    assert not hasattr(proxy, "_create_item_helper")

    proxy._item_context = replace(
        context, defaults=ItemClientDefaults(no_response_on_write=True)
    )
    replacement = proxy._get_item_helper()
    assert replacement is not helper
    assert replacement._defaults.no_response_on_write is True
    reference = weakref.ref(proxy)
    del proxy
    gc.collect()
    assert reference() is None


def test_legacy_helpers_are_not_cached_with_a_container_bound_callback(point_read):
    """On the legacy path a fresh helper is built each time and nothing is cached.

    The legacy helper holds a callback tied to its container, so keeping one
    would create the very loop the test above guards against. Building a new one
    each call is cheap here because the legacy path has other per-call work
    anyway.

    The difference between the two paths is deliberate, so it is stated rather
    than left to be discovered by someone adding caching to both for
    consistency.
    """
    if point_read.rust:
        return
    first = point_read.proxy._get_item_helper()
    second = point_read.proxy._get_item_helper()
    assert first is not second
    assert point_read.proxy._item_helper_cache is None


@pytest.mark.parametrize("async_mode", [False, True])
def test_cached_helper_keeps_concurrent_request_and_result_state_local(async_mode):
    """Two writes running at once through one shared helper do not mix up their bodies,
    their results, or their headers.

    Both calls are made to overlap -- held at a barrier on threads, or
    interleaved on the event loop -- and each gets back its own item and its own
    headers. A callback that edits what it is given runs for both, and neither
    sees the other's changes.

    This is the risk that comes with reusing a helper. Anything kept on it
    during a call would be shared by every caller, and the symptom would be one
    customer's item returned to another's request. That is both a correctness
    bug and a disclosure one, and it would only appear under load.

    The helper is still the same object afterwards, so concurrency did not
    quietly disable the reuse.
    """
    backend = AsyncBackend() if async_mode else Backend()
    barrier = threading.Barrier(2)

    def reply(prepared):
        return BackendResponse(201, 0, {"etag": prepared.item_id}, prepared.body_bytes)

    def execute(prepared, *, deadline=None):
        barrier.wait(timeout=5)
        return reply(prepared)

    async def execute_async(prepared, *, deadline=None):
        await asyncio.sleep(0)
        return reply(prepared)

    backend.execute = execute_async if async_mode else execute
    proxy = (AsyncContainerProxy if async_mode else ContainerProxy)(
        None, "dbs/d", "c", _item_context=ItemClientContext(backend)
    )
    helper = proxy._get_item_helper()
    documents = [{"id": name, "nested": [name]} for name in ("first", "second")]

    def hook(headers, body):
        body["nested"].append("hook")
        headers["etag"] = "hook"

    async def run():
        return await asyncio.gather(
            *(proxy.create_item(body, response_hook=hook) for body in documents)
        )

    if async_mode:
        results = asyncio.run(run())
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(proxy.create_item, body, response_hook=hook)
                for body in documents
            ]
            results = [future.result(timeout=10) for future in futures]
    assert results == documents
    assert [result.get_response_headers()["etag"] for result in results] == [
        "first",
        "second",
    ]
    assert proxy._get_item_helper() is helper


def call_target(proxy, operation, item, **kwargs):
    """Call an item operation with whatever extra arguments that operation needs.

    Replace needs a new body and patch needs a list of changes, while read and
    delete need neither. This keeps that difference in one place so the tests
    below can loop over all four.
    """
    if operation == "replace_item":
        return finish(
            proxy.replace_item(item, {"id": "different-body-id", "pk": "p"}, **kwargs)
        )
    if operation == "patch_item":
        return finish(
            proxy.patch_item(
                item, "p", [{"op": "set", "path": "/n", "value": 1}], **kwargs
            )
        )
    return finish(getattr(proxy, operation)(item, "p", **kwargs))


@pytest.mark.parametrize(
    "operation", ["read_item", "delete_item", "replace_item", "patch_item"]
)
@pytest.mark.parametrize("mapping", [False, True])
def test_links_are_built_only_for_legacy_and_mapping_fields_are_read_once(
    point_read, monkeypatch, operation, mapping
):
    """Only the legacy path builds an item link, and an item passed as a set of values has
    its fields read exactly once.

    Four operations are covered, with the item given either as an id or as
    something holding an id and its own address. On the legacy path a link is
    built from the container address and the id, or taken from the item's own
    address when it has one. On the Rust path no link is built at all -- the id
    and the container address are sent and the driver resolves the rest.

    The fields are counted as they are read, using stand-ins that record each
    access. Reading them more than once is not free and not safe: these may be
    computed values, and a second read could return something different, so the
    request would be built from a mixture.

    The method that used to build links is also confirmed gone from the
    container, so there is nothing left to call by habit.
    """
    context = point_read
    async_mode = inspect.iscoroutinefunction(context.proxy.read_item)
    mock = AsyncMock if async_mode else MagicMock
    formatted = []
    lookups = []

    class ItemId(str):
        def __format__(self, specification):
            formatted.append(self)
            return str.__format__(self, specification)

    class Reference(Mapping):
        def __getitem__(self, key):
            lookups.append(key)
            return {"id": "target", "_self": "dbs/rid/colls/rid/docs/opaque"}[key]

        def __iter__(self):
            return iter(("id", "_self"))

        def __len__(self):
            return 2

    capture = mock(return_value=(200, 0, {}, b"{}", None))
    if context.rust:
        module = async_rust if async_mode else sync_rust
        monkeypatch.setattr(
            module._rust_module,
            operation + ("_async" if async_mode else ""),
            capture,
            raising=False,
        )
    else:
        capture = mock(return_value=CosmosDict({}, response_headers={}))
        monkeypatch.setattr(
            context.cc,
            {
                "read_item": "ReadItem",
                "delete_item": "DeleteItem",
                "replace_item": "ReplaceItem",
                "patch_item": "PatchItem",
            }[operation],
            capture,
        )
    call_target(context.proxy, operation, Reference() if mapping else ItemId("target"))
    capture.assert_called_once()
    assert not hasattr(context.proxy, "_get_document_link")
    if mapping:
        assert lookups == ["_self", "id"]
    assert len(formatted) == (0 if context.rust or mapping else 1)
    if context.rust:
        prepared = capture.call_args.args[1]
        assert prepared.item_id == "target"
        assert prepared.container_link == context.proxy.container_link
    else:
        expected = (
            "dbs/rid/colls/rid/docs/opaque"
            if mapping
            else context.proxy.container_link + "/docs/target"
        )
        assert capture.call_args.kwargs["document_link"] == expected


@pytest.mark.parametrize(
    "operation", ["read_item", "delete_item", "replace_item", "patch_item"]
)
@pytest.mark.parametrize(
    "item,missing", [({"id": "target"}, "_self"), ({"_self": "opaque"}, "id")]
)
def test_mapping_validation_still_precedes_item_io(
    point_read, operation, item, missing
):
    """An item missing a field the call needs is refused before anything is sent.

    Each of the two required fields is left out in turn, across four operations,
    and the error names the missing one. Nothing reached the backend and no Rust
    call was made.

    Checking first is what makes the message useful. Left until later, the same
    mistake would surface as a request built around an empty address and come
    back as a not-found from the service -- which reads as "your item is gone"
    rather than "you passed the wrong thing".
    """
    with pytest.raises(KeyError) as raised:
        call_target(point_read.proxy, operation, item)
    assert raised.value.args == (missing,)
    assert point_read.events == []
    assert point_read.native_calls == 0


def test_rust_preparation_retains_no_legacy_address():
    """Preparation for the Rust path drops the legacy address entirely, even when one was
    supplied.

    Neither the built link nor the item's own address survives into what gets
    sent. The Rust driver addresses items itself, so these are not merely
    unused -- they are a second opinion about where the item lives.

    Carrying them would invite exactly the wrong repair later: someone debugging
    a routing problem finds an address sitting in the request and starts
    trusting it, and now two parts of the system decide where writes go.
    """
    args, _ = normalize_item_arguments(
        "read_item",
        {
            "container_link": "dbs/d/colls/c",
            "item_id": "item",
            "_item_self_link": "opaque",
            "request_options": {"partitionKey": "p"},
        },
    )
    assert "document_link" not in args
    assert "_item_self_link" not in args["kwargs"]


@pytest.mark.parametrize(
    "operation", ["read_item", "delete_item", "replace_item", "patch_item"]
)
@pytest.mark.parametrize("key", ["document_link", "_item_self_link"])
def test_keyword_arguments_cannot_override_the_item_target(point_read, operation, key):
    """Neither form of item address can be supplied as an extra argument to redirect a
    call.

    Both spellings are refused across four operations, with a message about
    addressing, and nothing is sent.

    These were internal values that once travelled this way. Still accepting
    them would give callers a hidden way to point an operation at a different
    item than the one they named -- a delete aimed at one item and addressed to
    another, with nothing in the visible arguments to show it.
    """
    with pytest.raises(TypeError, match="addressing"):
        call_target(
            point_read.proxy,
            operation,
            "target",
            **{key: "dbs/other/colls/other/docs/other"}
        )
    assert point_read.events == []


@pytest.mark.parametrize("has_hook", [False, True])
@pytest.mark.parametrize("empty", [False, True])
def test_completion_copies_only_nonempty_hook_bodies(monkeypatch, has_hook, empty):
    """The customer's callback gets its own copy of the result to play with, and the copy
    is only made when there is something to copy.

    The callback is handed a separate body and separate headers, and everything
    it changes -- adding fields, editing nested values, replacing the tag -- is
    discarded. What the caller receives is exactly what the service returned.

    Otherwise a callback written for logging could quietly rewrite the item its
    caller is about to use, which would be nearly impossible to trace back from
    the symptom.

    Copying is skipped when the body is empty, since there is nothing to protect
    and this runs on every single item call. The empty result here is one that
    reports itself as falsey while still being a real result, so the decision
    cannot be made by simply testing the value's truth.
    """
    copy = MagicMock(wraps=_response_parse.deepcopy)
    monkeypatch.setattr(_response_parse, "deepcopy", copy)

    class FalseyResult(CosmosDict):
        def __bool__(self):
            return False

    result = FalseyResult(
        {} if empty else {"nested": [1]},
        response_headers=CaseInsensitiveDict({"etag": "original"}),
    )

    def hook(headers, body):
        assert body is not result
        headers["etag"] = "callback"
        assert body.get_response_headers()["etag"] == "original"
        body.get_response_headers()["etag"] = "body"
        if not empty:
            body["nested"].append(2)
        body["added"] = True

    assert (
        _response_parse.complete_item_response(result, hook if has_hook else None, None)
        is result
    )
    assert copy.call_count == int(has_hook and not empty)
    assert dict(result) == ({} if empty else {"nested": [1]})
    assert result.get_response_headers()["etag"] == "original"
