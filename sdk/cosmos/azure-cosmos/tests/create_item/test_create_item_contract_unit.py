# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline create-item contracts with controlled responses and clocks.

Tests using point_create exercise the public method in four combinations:
sync/async and legacy/Rust. Rust binding calls and legacy connection methods
are replaced by fakes; these tests do not send requests to the service backend.
Other tests use item helpers directly with fake backends.

The point_create.events list records simulated metadata and write phases with
their budgets. It checks local dispatch ordering, not network attempts or
stored items. Coverage includes argument validation, prepared bodies,
response conversion, callbacks, and isolation of customer-owned input.
"""
import asyncio
import inspect
import json
import logging
from dataclasses import replace
from functools import partial
from types import MappingProxyType
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
from common.test_connection_free_items_unit import FakeSender, AsyncFakeSender, invoke
from read_item.test_read_item_contract_unit import point_read

from azure.cosmos import CosmosDict
from azure.cosmos._backend import binding_adapter as sync_rust
from azure.cosmos.aio._backend import binding_adapter as async_rust
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._helpers import _item_prep, _document, _response_parse
from azure.cosmos._helpers._client_context import ClientOperationDefaults
from azure.cosmos._helpers._response_parse import process_backend_response
from azure.cosmos._helpers._item_operations import ItemHelper
from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceExistsError


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
def test_retired_options_are_rejected_before_metadata_rust(point_create, name, value):
    """Arguments that used to be accepted now raise ``TypeError``, naming the argument.

    ``etag`` and ``match_condition`` never applied to create, and
    ``populate_query_metrics`` was dropped. Passing any of them is a mistake
    worth reporting loudly rather than ignoring, so the call must fail even when
    the value is ``None``. The empty ``events`` list proves nothing was sent.
    """
    with pytest.raises(TypeError, match=name):
        point_create.call({"id": "item"}, **{name: value})
    assert point_create.events == []


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("name", [
    "retry_total", "retry_connect", "retry_read", "retry_status",
    "retry_backoff_factor", "retry_backoff_max", "retry_on_methods",
])
@pytest.mark.parametrize("value", [None, 0, 1])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_retry_policy_controls_are_rejected_before_create_dispatch_rust(point_create, name, value, source):
    options = {name: value}
    kwargs = options if source == "keyword" else {source: options}
    hook = MagicMock()
    with pytest.raises(TypeError, match=f"create_item.*{name}"):
        point_create.call({"id": "order-42"}, response_hook=hook, **kwargs)
    assert options == {name: value}
    assert point_create.events == []
    assert point_create.native_calls == 0
    hook.assert_not_called()
    point_create.cc.CreateItem.assert_not_called()
    point_create.proxy.read.assert_not_called()
    point_create.proxy._client_context.adapter._ensure_driver_handle.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("name,value", [
    ("proxy", None), ("proxy", False), ("proxy", "http://unused.invalid:3128"),
    ("stream", None), ("stream", False), ("stream", True),
    ("retry_writes", None), ("retry_writes", 1), ("unknown_setting", False),
    ("tracing_enable", False),
])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_unknown_and_transport_create_options_fail_before_dispatch_rust(point_create, name, value, source):
    options = {name: value}
    kwargs = options if source == "keyword" else {source: options}
    hook = MagicMock()
    with pytest.raises(TypeError, match=name):
        point_create.call({"id": "order-42"}, response_hook=hook, **kwargs)
    assert options == {name: value}
    assert point_create.events == []
    assert point_create.native_calls == 0
    hook.assert_not_called()
    point_create.cc.CreateItem.assert_not_called()
    point_create.proxy.read.assert_not_called()
    point_create.proxy._client_context.adapter._ensure_driver_handle.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("name,internal,value", [
    ("filter_predicate", "filterPredicate", "FROM c WHERE false"),
    ("patch_operations", "patch_operations", []),
    ("max_item_count", "maxItemCount", 1),
    ("populate_query_metrics", "populateQueryMetrics", True),
    ("continuation", "continuation", "next-page"),
    ("is_query_plan_request", "isQueryPlanRequest", True),
    ("max_integrated_cache_staleness_in_ms", "maxIntegratedCacheStaleness", 1000),
    ("offer_enable_ru_per_minute_throughput", "offerEnableRUPerMinuteThroughput", True),
    ("if_match", "if_match", '"version"'),
    ("if_none_match", "if_none_match", "*"),
    ("access_condition", "accessCondition", {"type": "IfMatch", "condition": '"version"'}),
    ("item_id", "item_id", "another-item"),
])
@pytest.mark.parametrize("empty", [None, False, "supplied"])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_inapplicable_create_options_fail_before_dispatch_rust(
    point_create, name, internal, value, empty, source
):
    value = value if empty == "supplied" else empty
    key = name if source == "keyword" else internal
    options = {key: value}
    kwargs = options if source == "keyword" else {source: options}
    hook = MagicMock()
    with pytest.raises(TypeError, match=key):
        point_create.call({"id": "order-42"}, response_hook=hook, **kwargs)
    assert options == {key: value}
    assert point_create.events == []
    assert point_create.native_calls == 0
    hook.assert_not_called()
    point_create.cc.CreateItem.assert_not_called()
    point_create.proxy.read.assert_not_called()
    point_create.proxy._client_context.adapter._ensure_driver_handle.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("header", [
    "X-MS-MAX-ITEM-COUNT", "x-ms-documentdb-populatequerymetrics", "If-Match", "If-None-Match",
])
@pytest.mark.parametrize("source", ["initial_headers", "request_options", "feed_options", "nested_headers"])
def test_inapplicable_create_header_aliases_fail_before_dispatch_rust(point_create, header, source):
    options = {header: "1"}
    kwargs = (
        {"request_options": {"initialHeaders": options}} if source == "nested_headers" else {source: options}
    )
    with pytest.raises(TypeError, match=f"(?i){header}"):
        point_create.call({"id": "order-42"}, **kwargs)
    assert options == {header: "1"}
    assert point_create.events == []
    assert point_create.native_calls == 0
    point_create.cc.CreateItem.assert_not_called()
    point_create.proxy._client_context.adapter._ensure_driver_handle.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
def test_create_validation_preserves_selected_option_mapping_rust(point_create):
    ignored = {"maxItemCount": 1}
    result = point_create.call({"id": "order-42"}, request_options=None, feed_options=ignored)
    assert result["id"] == "order-42"
    assert ignored == {"maxItemCount": 1}
    assert point_create.native_calls == 1


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("source", ["request_options", "feed_options"])
def test_supported_nested_create_options_still_dispatch_rust(point_create, source):
    options = MappingProxyType({
        "partitionKey": "customer-17", "indexingDirective": 2,
        "sessionToken": "0:-1#1", "throughputBucket": 7,
        "contentType": "application/json", "utf8DecodingMode": "Strict",
        "responsePayloadOnWriteDisabled": False, "timeout": 5,
        "x-ms-custom": "value", "x-ms-activity-id": "create-activity",
    })
    result = point_create.call({"id": "order-42", "pk": "customer-17"}, **{source: options})
    assert result["id"] == "order-42"
    assert point_create.native_calls == 1
    settings = point_create.prepared.settings
    assert settings.item.indexing_directive == 2
    assert settings.session_token == "0:-1#1"
    assert settings.throughput_bucket == 7
    assert settings.activity_id == "create-activity"
    assert settings.resource.content_type == "application/json"
    assert legacy_partition_key_from_request(point_create.prepared) == '["customer-17"]'
    assert wire_headers(point_create.prepared)["x-ms-custom"] == "value"
    assert point_create.events[-1] == ("write", 5)
    point_create.cc.CreateItem.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
def test_supported_create_request_and_telemetry_options_still_dispatch_rust(point_create):
    hook = MagicMock()
    options = {"priorityLevel": "Low"}
    result = point_create.call(
        {"id": "order-42"}, request_options=options, priority="High",
        timeout=5, connection_timeout=None, response_hook=hook,
        excluded_locations=["East US"], initial_headers={"x-ms-custom": "value"},
        tracing_options={"enabled": False}, tracing_attributes={"test": "create"},
        logger=logging.getLogger(__name__), logging_enable=False,
    )
    assert result["id"] == "order-42"
    assert options == {"priorityLevel": "Low"}
    assert point_create.native_calls == 1
    assert point_create.prepared.settings.priority == "High"
    assert point_create.prepared.settings.excluded_locations == ("East US",)
    assert point_create.events[-1] == ("write", 5)
    assert wire_headers(point_create.prepared)["x-ms-custom"] == "value"
    hook.assert_called_once()
    point_create.cc.CreateItem.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, False), (True, False)], ids=["sync-legacy", "async-legacy"], indirect=True
)
@pytest.mark.parametrize("name,value", [
    ("retry_total", 0), ("retry_connect", 0), ("retry_read", 0), ("retry_status", 0),
    ("retry_backoff_factor", 0), ("retry_backoff_max", 0), ("retry_on_methods", ["POST"]),
])
def test_retry_policy_controls_still_reach_explicit_legacy_create_rust(point_create, name, value):
    assert point_create.call({"id": "order-42"}, **{name: value})["id"] == "order-42"
    point_create.cc.CreateItem.assert_called_once()
    assert point_create.cc.CreateItem.call_args.kwargs[name] == value


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("name,internal,value", [
    ("retry_write", "retry_write", 0),
    ("retry_write", "retry_write", False),
    ("retry_write", "retry_write", 1),
    ("connection_timeout", "connection_timeout", 0),
    ("connection_timeout", "connection_timeout", False),
    ("connection_timeout", "connection_timeout", 2),
    ("initial_headers", "initialHeaders", {"Accept": "custom"}),
    ("initial_headers", "initialHeaders", {"Cache-Control": "custom"}),
    ("initial_headers", "initialHeaders", {"uSeR-aGeNt": "custom"}),
    ("initial_headers", "initialHeaders", {"x-ms-version": "custom"}),
    ("availability_strategy", "availabilityStrategy", True),
    ("availability_strategy", "availabilityStrategy", {}),
    ("availability_strategy", "availabilityStrategy", {"threshold_ms": 100}),
    ("availability_strategy", "availability_strategy", True),
])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_unsupported_create_settings_raise_type_error_before_dispatch_rust(
    point_create, name, internal, value, source
):
    kwargs = {name: value} if source == "keyword" else {source: {internal: value}}
    hook = MagicMock()
    with pytest.raises(TypeError, match=name):
        point_create.call({"id": "order-42"}, response_hook=hook, **kwargs)
    assert point_create.events == []
    assert point_create.native_calls == 0
    hook.assert_not_called()
    point_create.cc.CreateItem.assert_not_called()
    point_create.proxy.read.assert_not_called()
    point_create.proxy._client_context.adapter._ensure_driver_handle.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, True), (True, True)], ids=["sync-rust", "async-rust"], indirect=True
)
@pytest.mark.parametrize("strategy", [None, False])
@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_create_without_unsupported_overrides_still_dispatches_rust(point_create, strategy, source):
    options = {"retry_write": None}
    if source == "keyword":
        options.update(
            connection_timeout=None, availability_strategy=strategy,
            initial_headers={"x-ms-custom": "value"},
        )
        kwargs = options
    else:
        options.update(availabilityStrategy=strategy, initialHeaders={"x-ms-custom": "value"})
        kwargs = {source: options}
    assert point_create.call({"id": "order-42"}, **kwargs)["id"] == "order-42"
    assert point_create.native_calls == 1
    assert wire_headers(point_create.prepared)["x-ms-custom"] == "value"
    point_create.cc.CreateItem.assert_not_called()


@pytest.mark.parametrize(
    "point_read", [(False, False), (True, False)], ids=["sync-legacy", "async-legacy"], indirect=True
)
@pytest.mark.parametrize("options", [
    {"retry_write": 0}, {"connection_timeout": 2},
    {"initial_headers": {"User-Agent": "custom"}}, {"availability_strategy": True},
])
def test_explicit_legacy_create_keeps_its_supported_settings_rust(point_create, options):
    assert point_create.call({"id": "order-42"}, **options)["id"] == "order-42"
    point_create.cc.CreateItem.assert_called_once()


def test_only_body_is_positional_rust(point_create):
    """``body`` is the one positional argument; everything else is keyword-only.

    This pins the calling shape so later argument additions or reordering cannot
    silently change what a positional call means. Passing a second positional
    argument must raise rather than be absorbed by some other parameter.
    """
    parameters = inspect.signature(point_create.proxy.create_item).parameters
    assert [name for name, value in parameters.items()
            if value.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD] == ["body"]
    for name in ("pre_trigger_include", "post_trigger_include"):
        assert name not in parameters
    for name in ("indexing_directive",):
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
def test_invalid_input_has_same_early_error_on_both_backends_rust(point_create, body, error):
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
def test_auto_id_precedes_partition_key_extraction_and_does_not_mutate_input_rust(point_create, hierarchical):
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


def test_mapping_and_request_options_are_not_mutated_rust(point_create):
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
def test_falsey_hook_gets_independent_body_and_headers_rust(point_create, no_response):
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


@pytest.mark.parametrize("hook", [False, 0, "not callable", {}])
def test_invalid_hook_is_rejected_before_metadata_rust(point_create, hook):
    with pytest.raises(TypeError, match="response_hook must be callable"):
        point_create.call({"id": "order-42"}, response_hook=hook)
    assert point_create.events == []


@pytest.mark.parametrize("kind", [
    "function", "method", "partial", "callable", "partial-callable", "async-generator",
])
def test_async_hook_is_rejected_before_create_dispatch_rust(point_create, kind):
    async def hook(_headers, _body):
        pytest.fail("An asynchronous response hook must not run")

    class AsyncHook:
        async def __call__(self, headers, body):
            pytest.fail("An asynchronous response hook must not run")

    async def generator_hook(_headers, body):
        pytest.fail("An asynchronous generator hook must not run")
        yield body

    callable_hook = AsyncHook()
    hooks = {
        "function": hook,
        "method": callable_hook.__call__,
        "partial": partial(hook),
        "callable": callable_hook,
        "partial-callable": partial(callable_hook),
        "async-generator": generator_hook,
    }
    with pytest.raises(TypeError, match="create_item response_hook must be synchronous"):
        point_create.call({"id": "item"}, response_hook=hooks[kind])
    assert point_create.events == []
    point_create.cc.CreateItem.assert_not_called()
    if point_create.rust:
        point_create.proxy._client_context.adapter._ensure_driver_handle.assert_not_called()


@pytest.mark.parametrize("callable_object", [False, True])
def test_sync_partial_hook_still_runs_once_rust(point_create, callable_object):
    calls = []

    def hook(headers, body):
        calls.append((headers["etag"], body["id"]))

    class Hook:
        def __call__(self, headers, body):
            hook(headers, body)

    result = point_create.call({"id": "item"}, response_hook=partial(Hook() if callable_object else hook))
    assert result["id"] == "item"
    assert calls == [('"current"', "item")]


@pytest.mark.parametrize("option_name", ["feed_options", "request_options"])
def test_nested_options_reach_create_without_mutation_rust(point_create, option_name):
    options = MappingProxyType({
        "timeout": 2,
        "responsePayloadOnWriteDisabled": True,
        "initialHeaders": {"x-ms-test": "orders"},
    })
    result = point_create.call({"id": "order-42"}, **{option_name: options})
    assert result == {}
    assert point_create.events == [("metadata", 2), ("write", 2)]
    headers = wire_headers(point_create.prepared) if point_create.rust else point_create.options["initialHeaders"]
    assert headers["x-ms-test"] == "orders"
    assert dict(options) == {
        "timeout": 2,
        "responsePayloadOnWriteDisabled": True,
        "initialHeaders": {"x-ms-test": "orders"},
    }


@pytest.mark.parametrize("request_options,timeout", [(None, None), ({}, None), ({"timeout": 3}, 3)])
def test_request_options_take_precedence_over_feed_options_rust(point_create, request_options, timeout):
    result = point_create.call(
        {"id": "order-42"},
        feed_options={"timeout": 2, "responsePayloadOnWriteDisabled": True},
        request_options=request_options,
    )
    assert result["id"] == "order-42"
    assert point_create.events == [("metadata", timeout), ("write", timeout)]


@pytest.mark.parametrize("timeout", [None, 3])
def test_explicit_options_override_feed_options_rust(point_create, timeout):
    result = point_create.call(
        {"id": "order-42"},
        feed_options={"timeout": 2, "responsePayloadOnWriteDisabled": True},
        timeout=timeout,
        no_response=False,
    )
    assert result["id"] == "order-42"
    assert point_create.events == [("metadata", timeout), ("write", timeout)]


def test_invalid_feed_timeout_is_rejected_before_metadata_rust(point_create):
    with pytest.raises(ValueError, match="create_item timeout"):
        point_create.call({"id": "order-42"}, feed_options={"timeout": 0})
    assert point_create.events == []


def test_explicit_body_response_overrides_client_default_rust(point_create):
    """``no_response=False`` on the call beats a client configured to suppress bodies.

    The client default is switched on, then overridden per call. The created
    item must come back with its ``id``, proving the per-call value wins.
    """
    context = point_create.proxy._client_context
    point_create.proxy._client_context = replace(context, defaults=ClientOperationDefaults(no_response_on_write=True))
    point_create.default_no_response = True
    assert point_create.call({"id": "item"}, no_response=False)["id"] == "item"


@pytest.mark.parametrize("with_hook", [False, True])
@pytest.mark.parametrize("parse_delay", [0.25, 0.5])
def test_parsing_exhausts_create_budget_without_replay_rust(
    point_create, monkeypatch, with_hook, parse_delay,
):
    """Expire during response parsing after a fake successful write, at or past the deadline."""
    point_create.write_delay = 0.75
    parse = _response_parse.parse_response_body
    parsed = []

    def delayed_parse(response):
        result = parse(response)
        parsed.append(result)
        point_create.clock.now += parse_delay
        return result

    monkeypatch.setattr(_response_parse, "parse_response_body", delayed_parse)
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        point_create.call(
            {"id": "item"}, timeout=1, response_hook=hook if with_hook else None,
        )
    assert parsed == [{"id": "item"}]
    assert [phase for phase, _ in point_create.events] == ["metadata", "write"]
    hook.assert_not_called()


def test_hook_failure_does_not_replay_create_rust(point_create):
    """Propagate a hook exception without repeating the simulated write.

    After the fake write returns success, the hook raises the original exception
    object. Recorded phases must contain one metadata lookup and one write;
    no service-side creation or driver retry behavior is exercised.
    """
    error = NotImplementedError("customer hook")
    hook = MagicMock(side_effect=error)
    with pytest.raises(NotImplementedError) as raised:
        point_create.call({"id": "item"}, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert [phase for phase, _ in point_create.events] == ["metadata", "write"]


def test_service_conflict_remains_typed_and_does_not_invoke_success_hook_rust(point_create):
    """Translate a synthetic 409 into CosmosResourceExistsError and skip the hook.

    The fake response supplies the conflict status; no existing item is created
    in a service account. Recorded phases confirm dispatch reached the simulated
    write before the public call raised.
    """
    point_create.status = 409
    hook = MagicMock()
    with pytest.raises(CosmosResourceExistsError):
        point_create.call({"id": "item"}, response_hook=hook)
    hook.assert_not_called()
    assert [phase for phase, _ in point_create.events] == ["metadata", "write"]


def test_remaining_subsecond_budget_reaches_create_rust(point_create):
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
def test_metadata_and_write_share_one_budget_rust(point_create, metadata_delay, write_delay, phases):
    """Share one deadline across simulated metadata and write phases.

    Three cases: metadata alone overruns the budget; metadata consumes it
    exactly, leaving nothing for the write; metadata leaves too little for the
    write to finish. The recorded phases show how far the call got, which is
    what distinguishes a shared budget from a per-phase one.

    Each case raises CosmosClientTimeoutError without invoking the success hook.
    The fake clock does not test wall-clock timing or service-side cancellation.
    """
    point_create.metadata_delay = metadata_delay
    point_create.write_delay = write_delay
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        point_create.call({"id": "item"}, timeout=1, response_hook=hook)
    assert [phase for phase, _ in point_create.events] == phases
    hook.assert_not_called()


def test_create_charges_lazy_initialization_to_budget_rust(point_create):
    """Charge simulated driver acquisition to the Rust call's existing budget.

    The fake acquisition advances the clock beyond the one-second allowance.
    The call must raise before simulated metadata or write dispatch. This does
    not exercise real driver creation; legacy fixture cases return early.
    """
    if not point_create.rust:
        return
    point_create.init_delay = 2
    with pytest.raises(CosmosClientTimeoutError):
        point_create.call({"id": "item"}, timeout=1)
    assert point_create.events == []


def test_create_serializes_once_before_metadata_rust(point_create, monkeypatch):
    """Count one document-encoder invocation for a Rust-path create.

    Wrapping the real encoder catches repeated serialization in the Python
    wrapper. The binding is mocked, so this does not measure driver work or
    end-to-end write cost. Legacy fixture cases return early.
    """
    if not point_create.rust:
        return
    serialize = MagicMock(wraps=_document.serialize_body_to_bytes)
    monkeypatch.setattr(_document, "serialize_body_to_bytes", serialize)
    point_create.call({"id": "item", "pk": "pk"})
    serialize.assert_called_once()


@pytest.mark.parametrize("point_read", [(True, True)], ids=["async-rust"], indirect=True)
def test_async_create_snapshots_body_and_starts_budget_when_awaited_rust(point_create, monkeypatch):
    """Unscheduled time consumes no create budget and precedes the request snapshot."""
    serialize = MagicMock(wraps=_document.serialize_body_to_bytes)
    monkeypatch.setattr(_document, "serialize_body_to_bytes", serialize)
    body = {"id": "item", "pk": "pk", "total": 125.5}
    pending = point_create.proxy.create_item(body, no_response=True, timeout=1)
    try:
        serialize.assert_not_called()
        assert point_create.events == []
        point_create.clock.now += 5
        body["total"] = 200
        result = asyncio.run(pending)
    finally:
        pending.close()

    assert result == {}
    serialize.assert_called_once()
    assert json.loads(point_create.prepared.body_bytes)["total"] == 200
    assert point_create.events == [("metadata", 1), ("write", 1)]


def test_partition_key_and_wire_body_use_the_same_nested_snapshot_rust(point_create):
    """Retain the original nested value after mutation during simulated metadata lookup.

    A test callback changes the caller's nested key to ``after``. The fake
    response still contains ``before``; on Rust, the prepared body does too,
    and partition-key extraction remains delegated to the binding.

    This does not execute native key extraction, routing, or service storage.
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
def test_compact_utf8_applies_to_all_singleton_write_bodies_rust(async_mode, compact, op):
    """Check compact UTF-8 encoding in prepared sync and async single-item writes.

    The fake backend captures body bytes: the accented e uses ``\\u00e9``
    with the setting off and its two UTF-8 bytes with it on.

    Create, upsert and replace encode a document; patch encodes an operation
    value inside its request body. Each prepared body must parse as JSON.
    This test does not send requests to the service backend.
    """
    backend = AsyncFakeSender() if async_mode else FakeSender()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(
        backend, ClientOperationDefaults(enable_compact_utf8_item_writes=compact)
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
