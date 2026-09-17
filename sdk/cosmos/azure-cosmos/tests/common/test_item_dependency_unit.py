# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Preparation ownership, legacy-only addressing and reusable item helpers."""

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
from azure.cosmos._helpers.item_helper import ItemHelper, normalize_item_arguments
from azure.cosmos._helpers.legacy_item_helper import (
    LegacyItemHelper,
    prepare_legacy_item_arguments,
)
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper
from azure.cosmos.aio._helpers.legacy_item_helper import AsyncLegacyItemHelper
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from common.test_connection_free_items_unit import Backend, AsyncBackend
from create_item.test_create_item_contract_unit import point_create
from read_item.test_read_item_contract_unit import point_read


def finish(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


@pytest.mark.parametrize("timeout", [None, 2.0])
def test_create_prepares_once_even_without_a_timeout(
    point_create, monkeypatch, timeout
):
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
    if point_read.rust:
        return
    first = point_read.proxy._get_item_helper()
    second = point_read.proxy._get_item_helper()
    assert first is not second
    assert point_read.proxy._item_helper_cache is None


@pytest.mark.parametrize("async_mode", [False, True])
def test_cached_helper_keeps_concurrent_request_and_result_state_local(async_mode):
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
    with pytest.raises(KeyError) as raised:
        call_target(point_read.proxy, operation, item)
    assert raised.value.args == (missing,)
    assert point_read.events == []
    assert point_read.native_calls == 0


def test_rust_preparation_retains_no_legacy_address():
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
