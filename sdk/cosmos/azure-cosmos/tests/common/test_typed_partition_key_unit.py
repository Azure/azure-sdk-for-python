# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Typed partition values, source states and native protocol agreement."""

from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace
import json

import pytest

from azure.cosmos._backend.contracts import PreparedRequest, PreparedQuery
from azure.cosmos._backend.partition_key import (
    PartitionKeyInput,
    UNDEFINED_PARTITION_KEY,
)
from azure.cosmos._backend.request_settings import RequestSettings
from azure.cosmos._helpers._partition_key import (
    normalize_partition_key,
    query_partition_key_components,
    partition_key_bookmark_value,
    parse_customer_partition_key_header,
)
from azure.cosmos._helpers._request_item import build_read_item_request
from azure.cosmos.partition_key import _Empty, _Undefined, NonePartitionKeyValue


@pytest.mark.parametrize(
    "value,kind,values",
    [
        ("customer-17", "components", ("customer-17",)),
        (True, "components", (True,)),
        (0, "components", (0,)),
        (None, "components", (None,)),
        (_Undefined(), "components", (UNDEFINED_PARTITION_KEY,)),
        (_Empty(), "empty_sentinel", ()),
        (NonePartitionKeyValue, "empty_sentinel", ()),
        ([], "empty_sequence", ()),
        ((), "empty_sequence", ()),
        (["tenant", _Undefined()], "components", ("tenant", None)),
    ],
)
def test_point_and_feed_range_normalization_preserves_source(value, kind, values):
    assert normalize_partition_key(value) == PartitionKeyInput(kind, values)


def test_query_components_do_not_erase_undefined():
    key = query_partition_key_components(["tenant", _Undefined(), None])
    assert key.values == ("tenant", UNDEFINED_PARTITION_KEY, None)
    assert partition_key_bookmark_value(key) == '["tenant",{},null]'


def test_component_snapshots_and_identity_are_immutable_and_type_sensitive():
    values = ["tenant", 7]
    key = normalize_partition_key(values)
    values[0] = "changed"
    assert key.values == ("tenant", 7)
    with pytest.raises(FrozenInstanceError):
        key.values = ()
    assert normalize_partition_key(True) != normalize_partition_key(1)
    assert normalize_partition_key(-0.0) != normalize_partition_key(0.0)
    assert normalize_partition_key(1) != normalize_partition_key(1.0)


def test_scalar_subclasses_keep_their_underlying_values():
    class Text(str):
        def __str__(self):
            return "wrong"

    class Number(int):
        def __int__(self):
            return 999

    class Real(float):
        def __float__(self):
            return 999.0

    assert normalize_partition_key(Text("tenant")).values == ("tenant",)
    assert normalize_partition_key(Text("\ud83d\ude00")).values == ("\U0001f600",)
    assert normalize_partition_key(Number(7)).values == (7,)
    assert normalize_partition_key(Real(1.25)).values == (1.25,)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("tenant", "tenant"),
        ("\u4e2d\U0001f600", "\u4e2d\U0001f600"),
        ("\ud800\udc00", "\U00010000"),
        ("\ud83d\ude00", "\U0001f600"),
        ("\udbff\udfff", "\U0010ffff"),
        ("a\ud83d\ude00\ud800\udc00z", "a\U0001f600\U00010000z"),
        ("\ud800", "\ud800"),
        ("\udc00", "\udc00"),
        ("\udc00\ud800", "\udc00\ud800"),
    ],
)
def test_unicode_normalization_preserves_key_shapes_and_bookmarks(value, expected):
    assert normalize_partition_key(value).values == (expected,)
    components = ["tenant", value, None]
    for key in (
        normalize_partition_key(components),
        query_partition_key_components(components),
    ):
        assert key.values == ("tenant", expected, None)
        assert partition_key_bookmark_value(key) == json.dumps(
            components, separators=(",", ":"), allow_nan=False
        )
    assert components == ["tenant", value, None]


@pytest.mark.parametrize("key_shape", ["scalar", "hierarchical", "query"])
@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_native_unicode_key_extraction_matches_legacy(key_shape, async_mode):
    from azure.cosmos._helpers._legacy_partition_key import legacy_partition_key_header

    native = pytest.importorskip("azure.cosmos._rust")
    value = "\ud83d\ude00"
    components = ["tenant", value, None]
    if key_shape == "scalar":
        key = normalize_partition_key(value)
        legacy_values = json.loads(legacy_partition_key_header(value))
    else:
        key = (
            normalize_partition_key(components)
            if key_shape == "hierarchical"
            else query_partition_key_components(components)
        )
        legacy_values = json.loads(legacy_partition_key_header(components))
    request = build_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="item",
        partition_key_value=value,
        container_rid=None,
        request_options={},
    )
    method = native.read_item_async if async_mode else native.read_item
    # Both representations must pass extraction and reach driver lookup, without I/O.
    for typed_key in (key, normalize_partition_key(legacy_values)):
        with pytest.raises(RuntimeError, match="no driver registered for handle"):
            result = method(
                "unicode-partition-key-test-unused-handle",
                replace(request, partition_key=typed_key),
            )
            if async_mode:
                await result


def test_change_feed_does_not_turn_the_empty_sentinel_into_null():
    from azure.cosmos._helpers._change_feed import _settings

    assert (
        _settings({"partition_key": _Empty()}, rust=True)["partition_key"].kind
        == "empty_sentinel"
    )


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        10**500,
        {"invalid": 1},
        [1, 2, 3, 4],
        b"bytes",
        [[1]],
        Ellipsis,
        [Ellipsis],
    ],
)
def test_invalid_public_components_fail_explicitly(value):
    with pytest.raises((ValueError, TypeError)):
        normalize_partition_key(value)


@pytest.mark.parametrize(
    "kind,values",
    [
        ("unknown", ()),
        ("components", ()),
        ("components", ["a"]),
        ("cross_partition", ("a",)),
        ("extract", (None,)),
        ("components", ({},)),
    ],
)
def test_invalid_private_shapes_are_rejected(kind, values):
    with pytest.raises((ValueError, TypeError)):
        PartitionKeyInput(kind, values)


@pytest.mark.parametrize(
    "value,expected",
    [("customer-17", "customer-17"), ("\ud83d\ude00", "\U0001f600")],
)
def test_read_preparation_does_not_encode_or_decode_partition_json(
    monkeypatch, value, expected
):
    def forbidden(*args, **kwargs):
        raise AssertionError("Internal partition-key JSON conversion")

    monkeypatch.setattr(json, "dumps", forbidden)
    monkeypatch.setattr(json, "loads", forbidden)
    prepared = build_read_item_request(
        container_link="dbs/d/colls/c",
        item_id="item",
        partition_key_value=value,
        container_rid=None,
        request_options={},
    )
    assert prepared.partition_key == PartitionKeyInput("components", (expected,))
    assert not hasattr(prepared, "partition_key_header")


def test_customer_header_is_decoded_only_at_the_external_input_boundary():
    assert parse_customer_partition_key_header("[null,true,{}]") == PartitionKeyInput(
        "components", (None, True, UNDEFINED_PARTITION_KEY)
    )
    assert parse_customer_partition_key_header("[]").kind == "cross_partition"


@pytest.mark.parametrize(
    "resource,options,expected",
    [
        (
            "docs",
            {"partitionKey": "explicit"},
            PartitionKeyInput("components", ("explicit",)),
        ),
        ("dbs", {}, PartitionKeyInput("cross_partition")),
        ("colls", {}, PartitionKeyInput("cross_partition")),
    ],
)
def test_unused_raw_headers_are_not_parsed(resource, options, expected):
    from azure.cosmos._query_rust_routing import _build_feed_request

    request = _build_feed_request(
        op="read_all_items",
        container_link="dbs/d/colls/c",
        resource_type=resource,
        options=options,
        req_headers={"x-ms-documentdb-partitionkey": "invalid-json"},
    )
    assert request.partition_key == expected


@pytest.mark.parametrize(
    "method",
    [
        "create_item",
        "upsert_item",
        "replace_item",
        "read_item",
        "delete_item",
        "patch_item",
        "query_items",
        "read_all_items",
        "feed_range_from_partition_key",
    ],
)
@pytest.mark.parametrize("async_mode", [False, True])
def test_native_consumers_reject_untyped_components_before_io(method, async_mode):
    native = pytest.importorskip("azure.cosmos._rust")
    request = SimpleNamespace(
        protocol_version=3,
        op=method,
        container_link="dbs/d/colls/c",
        partition_key=SimpleNamespace(kind="components", values=({},)),
        headers={},
        settings=RequestSettings(),
        body_bytes=b'{"id":"item"}',
        item_id="item",
    )
    with pytest.raises(TypeError, match="Unsupported partition-key component"):
        getattr(native, method + ("_async" if async_mode else ""))(
            "unused-handle", request
        )


@pytest.mark.parametrize(
    "method",
    [
        "read_item",
        "read_feed_ranges",
        "is_feed_range_subset",
        "feed_range_from_partition_key",
    ],
)
@pytest.mark.parametrize("async_mode", [False, True])
def test_old_request_envelope_fails_before_reading_its_legacy_header(
    method, async_mode
):
    native = pytest.importorskip("azure.cosmos._rust")
    request = SimpleNamespace(
        protocol_version=2,
        container_link="dbs/d/colls/c",
        partition_key_header='["tenant"]',
        headers={},
        settings=RequestSettings(),
        item_id="item",
    )
    with pytest.raises(ValueError, match="protocol version"):
        getattr(native, method + ("_async" if async_mode else ""))(
            "unused-handle", request
        )


def test_prepared_records_require_typed_keys():
    with pytest.raises(TypeError, match="PartitionKeyInput"):
        PreparedRequest("read_item", "dbs/d/colls/c", b"", '["tenant"]')
    with pytest.raises(TypeError, match="PartitionKeyInput"):
        PreparedQuery("query_items", "dbs/d/colls/c", partition_key='["tenant"]')


@pytest.mark.parametrize(
    "op,payload",
    [
        (
            "query_items",
            {"query": {"query": "SELECT * FROM c"}, "allow_cross_partition": True},
        ),
        ("query_items_change_feed", {"mode": "LatestVersion", "start": "Now"}),
    ],
)
@pytest.mark.parametrize("async_mode", [False, True])
def test_retained_native_readers_reject_embedded_legacy_key_strings(
    op, payload, async_mode
):
    native = pytest.importorskip("azure.cosmos._rust")
    request = PreparedRequest(
        op,
        "dbs/d/colls/c",
        json.dumps({**payload, "partition_key": '["tenant"]'}).encode(),
        PartitionKeyInput("cross_partition"),
    )
    method = (
        native.fetch_page_with_cursor_async if async_mode else native.fetch_page_with_cursor
    )
    with pytest.raises(ValueError, match="Invalid retained feed request"):
        method("unused-handle", request, native.ItemFeedCursor())


@pytest.mark.parametrize(
    "value,kind",
    [
        (_Empty(), "empty_sentinel"),
        ([], "empty_sequence"),
        (_Undefined(), "components"),
        (None, "components"),
    ],
)
def test_feed_range_builder_keeps_source_provenance(value, kind):
    from azure.cosmos._feed_ranges_rust_routing import (
        build_feed_range_from_partition_key_prepared_request,
    )

    request = build_feed_range_from_partition_key_prepared_request(
        container_link="dbs/d/colls/c",
        partition_key_value=value,
    )
    assert request.partition_key.kind == kind
    assert request.body_bytes == b""
