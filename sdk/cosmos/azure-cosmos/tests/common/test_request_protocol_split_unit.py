# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for the exact shape of a request handed to the Rust side (no network).

Every operation crosses one boundary: Python builds a request and the Rust side
reads it. This file pins what may appear in that request, and it is deliberately
narrow -- wire headers and a fixed set of named settings, nothing else.

The reason for the narrowness is that the two sides are built separately. If
Python could attach anything it liked, the Rust side would need to guess at
values it did not expect, and the usual guess is to ignore them. A setting that
is ignored rather than refused is the worst outcome here: the customer asked for
a region, a priority, or no response body, the call succeeds, and nothing they
can see says their instruction went nowhere.

So the rules checked here are all forms of the same rule. An option this side
does not recognize is an error rather than a header. Settings the Rust side
needs are named, not smuggled through in headers. Things that belong to Python
alone -- the deadline, legacy addresses, raw bodies waiting to be serialized --
never cross at all.

Several tests call the real Rust entry points. They pass a handle that is not
registered, so the call is refused after the request has been read but before
anything is sent, which is enough to prove what the Rust side accepts.
"""
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
from copy import deepcopy
import inspect
from dataclasses import replace
from itertools import permutations

import pytest

from azure.cosmos._backend.contracts import PreparedRequest, PreparedPageRequest
from azure.cosmos._backend.rust_backend import build_binding_request_from_page as sync_page
from azure.cosmos.aio._backend.rust_backend import build_binding_request_from_page as async_page
from azure.cosmos._helpers import _request_item
from azure.cosmos._helpers._document import serialize_document
from common.typed_requests import legacy_preparation as prepare_request_headers
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings
from azure.cosmos._backend.request_settings import RequestSettings
from common.test_connection_free_items_unit import Backend, AsyncBackend, invoke
from azure.cosmos._helpers._item_operations import ItemHelper
from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_every_point_operation_has_only_headers_and_explicit_options(async_mode, op):
    """Each single-item operation produces a request holding only wire headers and named
    settings, and leaves the caller's options untouched.

    All six operations run on both the sync and async client. The split is the
    point: a trigger becomes a real header because that is how the service
    receives it, while whether to return the written item, which regions to
    avoid, and the availability strategy become named settings, because the Rust
    side has to act on them rather than pass them along.

    Anything landing on the wrong side of that line goes wrong quietly. A
    setting turned into a header would be sent to the service, which ignores
    what it does not know; a header turned into a setting would never reach the
    service at all.

    The partition key arrives in the single form the Rust side expects, no
    metadata lookup happens, and the caller's options object is unchanged
    afterwards so it can be reused for the next call.
    """
    backend = AsyncBackend() if async_mode else Backend()
    options = {
        "partitionKey": "p", "disableAutomaticIdGeneration": True,
        "initialHeaders": {"x-customer": "value"},
    }
    before = deepcopy(options)
    invoke((AsyncItemHelper if async_mode else ItemHelper)(backend), op,
           request_options=options, no_response=False,
           pre_trigger_include=["a", "b"], excluded_locations=["West US"],
           availability_strategy=False)
    request = backend.events[-1]
    assert wire_headers(request) == {
        "x-customer": "value",
        "x-ms-documentdb-pre-trigger-include": "a,b",
    }
    assert settings_options(request) == {
        "responsePayloadOnWriteDisabled": False,
        "excludedLocations": ["West US"],
        "availabilityStrategy": "disabled",
    }
    assert legacy_partition_key_from_request(request) == '["p"]'
    assert backend.events.count("metadata") == 0
    assert options == before


@pytest.mark.parametrize("operation", ["create_item", "upsert_item", "replace_item", "patch_item"])
def test_write_builders_require_snapshots_and_normalized_options(operation):
    """The builders for write operations demand an already-prepared body and already-sorted
    options, and refuse to accept the raw forms.

    Each builder must take the serialized body and the options, both required
    with no default. The raw body, the patch instructions, a catch-all for
    further arguments, and the two flags that steer serialization must all be
    absent.

    This keeps preparation in one place. If a builder could also accept the raw
    body it would have to serialize it too, and then there would be two answers
    to what the customer's item looks like on the wire -- differing in exactly
    the cases those flags control, which are the ones hardest to notice.

    Requiring rather than defaulting matters as much: a default would let a
    caller omit the prepared body and silently get the wrong one.
    """
    parameters = inspect.signature(getattr(_request_item, f"build_{operation}_request")).parameters
    snapshot = "body_bytes" if operation == "patch_item" else "document"
    assert {snapshot, "request_options"} <= parameters.keys()
    assert not {"body", "patch_operations", "kwargs", "compact_utf8", "enable_automatic_id_generation"} & parameters.keys()
    for name in (snapshot, "request_options"):
        assert parameters[name].default is inspect.Parameter.empty


@pytest.mark.parametrize("adapter", [sync_page, async_page])
def test_page_adapter_preserves_separate_options_without_a_deadline(adapter):
    """Turning a page request into a Rust request moves paging values into headers, copies
    the settings, and carries no deadline.

    The position and the page size become headers, since that is how the service
    receives them. The named settings are equal but are a separate object, so
    the Rust side cannot write into something the pager still holds and change
    what the next page asks for.

    Neither object has a deadline at all. How long is left is passed alongside
    the request each time, because it shrinks between pages -- storing it on the
    request would freeze the first page's remaining time and hand it to every
    page after, so a long listing would never time out.

    Both the sync and async adapters are checked, since they are written
    separately.
    """
    page = PreparedPageRequest(
        op="read_all_items", container_link="dbs/d/colls/c",
        headers={"x-customer": "value"}, settings=legacy_settings({"excludedLocations": ["West US"]}),
        continuation="token", max_item_count=2,
    )
    request = adapter(page)
    assert wire_headers(request) == {"x-customer": "value", "x-ms-continuation": "token", "x-ms-max-item-count": "2"}
    assert settings_options(request) == settings_options(page)
    assert settings_options(request) is not settings_options(page)
    assert not hasattr(request, "deadline")
    assert not hasattr(page, "deadline")


def test_unknown_options_do_not_become_headers_or_vanish():
    """An option nobody recognizes is refused by name rather than passed along or dropped.

    The two easy alternatives are both bad. Turning it into a header sends it to
    the service, which ignores anything it does not know, so the caller's
    instruction disappears with the call still succeeding. Dropping it is the
    same outcome with less ceremony.

    Naming the option in the error is what makes it actionable -- usually the
    cause is a spelling mistake or an option from a newer version, and both are
    obvious once the name is in front of you.
    """
    with pytest.raises(TypeError, match="unknownFutureOption"):
        build_request_headers_and_settings({"unknownFutureOption": True, "partitionKey": "p", "timeout": 2})


@pytest.mark.parametrize("condition_type,header", [
    ("IfMatch", "if-match"), ("IfNoneMatch", "if-none-match"),
])
@pytest.mark.parametrize("header_case", [str.lower, str.upper, str.title])
@pytest.mark.parametrize("source_order", list(permutations(("initial", "access", "direct"))))
@pytest.mark.parametrize("through_builder", [False, True])
def test_conditional_header_sources_resolve_case_insensitively_in_input_order(
    condition_type, header, header_case, source_order, through_builder
):
    """A conditional header can be given three ways, and whichever comes last in the
    caller's options wins, with only one of them reaching the wire.

    The three sources are a header inside the initial headers, an access
    condition, and the header written directly. Both conditions are covered,
    three spellings of the header name, all six orderings, and both routes
    through the code.

    Two rules follow from this. Spelling is ignored when deciding which sources
    are the same header, because customers copy names from documentation in
    whatever case they find them. And later wins, which is the ordinary meaning
    of setting the same thing twice.

    Exactly one instance ends up on the wire. Two would be the real danger:
    conditional headers decide whether a write happens at all, so a request
    carrying both an old and a new value could overwrite something the customer
    was protecting.

    Their options object is unchanged, since resolving this must not consume the
    sources it read.
    """
    sources = {
        "initial": ("initialHeaders", {header_case(header): '"initial"'}),
        "access": ("accessCondition", {"type": condition_type, "condition": "*"}),
        "direct": (header_case(header), '"expected-etag"'),
    }
    options = dict(sources[source] for source in source_order)
    before = deepcopy(options)
    if through_builder:
        request = _request_item.build_replace_item_request(
            container_link="dbs/Contoso/colls/Orders",
            document=serialize_document(
                {"id": "order-42", "customerId": "customer-17"}, operation="replace_item"
            ),
            item_id="order-42", partition_key_value="customer-17",
            container_rid="rid", request_options=options,
        )
        headers = wire_headers(request)
        assert settings_options(request) == {}
    else:
        headers, request_options = prepare_request_headers(options)
        assert request_options == {}
    expected = {"initial": '"initial"', "access": "*", "direct": '"expected-etag"'}[source_order[-1]]
    assert [(key, value) for key, value in headers.items() if key.lower() == header] == [(header, expected)]
    assert options == before


@pytest.mark.parametrize("method", [
    "create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item",
    "create_database", "read_database", "delete_database",
    "read_container", "delete_container", "replace_container",
    "list_databases", "list_containers", "read_offer", "replace_offer",
])
@pytest.mark.parametrize("async_mode", [False, True])
def test_native_every_extraction_family_reads_request_options_before_io(monkeypatch, method, async_mode):
    """Every Rust entry point reads the named settings and refuses a bad one before doing
    any work.

    Sixteen operations are covered on both the sync and async side -- items,
    databases, containers, listings, and throughput. Each is given a timeout
    that is true rather than a number and refuses it by name.

    True is chosen deliberately: Python treats it as the number one, so it is
    the value most likely to slip through a loose check and become a one-second
    timeout nobody asked for.

    Covering all sixteen is the point. The entry points are grouped into
    families that read settings in their own way, and a family that skipped the
    check would not fail here -- it would accept the value and act on whatever
    it made of it, on that group of operations only.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    monkeypatch.setenv("COSMOS_WIRE_STRICT", "1")
    request = PreparedRequest(
        op=method, container_link="dbs/d" if method == "list_containers" else "dbs/d/colls/c", item_id="item",
        body_bytes=b'{"id":"item"}', partition_key=key_from_legacy_header('["p"]'),
        headers={"x-customer": "value"},
    )
    settings = RequestSettings()
    object.__setattr__(settings, "timeout_seconds", True)
    request = replace(request, settings=settings)
    entrypoint = getattr(native, method + ("_async" if async_mode else ""))
    with pytest.raises(TypeError, match="timeout_seconds"):
        entrypoint("unused-handle", request)


@pytest.mark.parametrize("consumed", ["partitionKey", "disableAutomaticIdGeneration"])
def test_native_consumed_options_have_no_dead_allowlist(monkeypatch, consumed):
    """Options that Python handles itself are not also accepted as settings for the Rust
    side.

    The partition key and the switch for automatic id generation are both used
    up in Python: one is resolved into the request, the other decides whether an
    id is generated before the body is serialized. Neither has any meaning
    further down.

    Still accepting them would leave a second way to set something that no
    longer does anything. Someone would eventually use it, and it would be
    ignored in silence -- an item written without the generated id, or to the
    wrong partition.
    """
    with pytest.raises(TypeError, match=consumed):
        RequestSettings(**{consumed: True})


def test_native_rejects_old_private_request_shape(monkeypatch):
    """A request in the older shape is refused rather than partly understood.

    The old object carried a version number and relied on the Rust side reading
    whatever attributes it happened to find. Something shaped like it, with the
    right address and partition key, is refused with a message asking for the
    typed settings.

    Accepting it by looking for familiar attributes is the failure mode worth
    preventing. The old shape has no place for the named settings, so the
    request would go out with every one of them silently unset -- no timeout, no
    region preferences, no response preference -- while looking entirely normal.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    from types import SimpleNamespace
    old = SimpleNamespace(op="read_item", container_link="dbs/d/colls/c", protocol_version=3, partition_key=key_from_legacy_header('["p"]'), headers={}, item_id="item")
    with pytest.raises(TypeError, match="typed settings"):
        native.read_item("unused-handle", old)


def test_native_driver_handle_exports_and_keyword_contract():
    """The Rust side offers exactly one way to take and give back a driver, with a fixed
    argument list.

    The older pair of client functions is gone, so there is no second route that
    could acquire a driver the bookkeeping never learns about -- which would
    defeat the whole reservation scheme built on top of it.

    The remaining function's arguments are pinned in order and every one but the
    account address defaults to nothing, so callers can name only what they
    have. Asking for a driver with neither a key nor a credential is refused
    rather than producing one that cannot authenticate and fails later on a real
    request.

    Releasing a handle nobody knows succeeds quietly. Cleanup runs while things
    are already going wrong, so it must not raise over a handle that is already
    gone.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    assert not hasattr(native, "init_client")
    assert not hasattr(native, "close_client")
    acquire = inspect.signature(native.acquire_driver_handle).parameters
    assert tuple(acquire) == ("endpoint", "master_key", "config", "credential")
    assert acquire["endpoint"].default is inspect.Parameter.empty
    assert all(acquire[name].default is None for name in ("master_key", "config", "credential"))
    assert tuple(inspect.signature(native.release_driver_handle).parameters) == ("driver_handle",)
    with pytest.raises(ValueError, match="acquire_driver_handle requires either"):
        native.acquire_driver_handle(
            endpoint="https://unused.invalid", master_key=None, config=None, credential=None
        )
    assert native.release_driver_handle(driver_handle="unused-protocol-test-handle") is None
