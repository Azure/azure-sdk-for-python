# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for turning a caller's partition key into the single typed form the rest
of the code uses, and for keeping the Python and Rust views of it in step.

A partition key used to become a piece of JSON text early on and stay text the rest of the
way. Several distinct situations ended up looking alike once written down, and telling
them apart again meant reading the text back. It is now a small record that says which
situation it is, and the text is only produced where something outside actually needs it.

The situations are: real values the caller gave; a container that has no partition key at
all; an empty list, which is not the same thing; no key at all, meaning search every
partition; and take the key out of the item body. Anything that flattened these together
would change which items a request reaches.

Much of this file is about values that survive a round trip unchanged -- unusual text,
numbers that must not be rounded or re-typed, and the exact text of a saved paging
bookmark, which customers store and hand back later.
"""

from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace
import json

import pytest

from azure.cosmos._backend.contracts import PreparedRequest, PreparedPageRequest
from azure.cosmos._backend.partition_key_input import (
    BindingPartitionKey,
    UNDEFINED_PARTITION_KEY,
)
from azure.cosmos._backend.request_settings import RequestSettings
from azure.cosmos._helpers._partition_key import (
    normalize_partition_key,
    query_partition_key_components,
    serialize_partition_key_for_continuation,
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
    """Each accepted input keeps its own meaning instead of collapsing into a shared one.

    The cases worth reading carefully are the ones that used to look alike. A container
    with no partition key and an empty list both used to arrive as something empty, but
    they are different requests. Nothing-as-a-value stays a real value, distinct from
    having no value at all.

    The last case is inherited oddness, kept on purpose: on its own, "the key path is
    missing from the item" is recorded as such, but the same marker inside a list of
    components becomes nothing. That is exactly what the old header rules did, so it is
    preserved rather than tidied up.
    """
    assert normalize_partition_key(value) == BindingPartitionKey(kind, values)


def test_query_components_do_not_erase_undefined():
    """Queries keep "the path is missing" apart from "the value is nothing".

    This is where the two differ. Point operations follow the old rule and turn a missing
    path inside a list into nothing; queries keep it, because a query matches on what it
    is given and the two select different items.

    The saved bookmark text is checked alongside, since it is what customers store and
    hand back: a missing path is written as an empty object, nothing is written as null.
    """
    key = query_partition_key_components(["tenant", _Undefined(), None])
    assert key.values == ("tenant", UNDEFINED_PARTITION_KEY, None)
    assert serialize_partition_key_for_continuation(key) == '["tenant",{},null]'


def test_component_snapshots_and_identity_are_immutable_and_type_sensitive():
    """The caller's list is copied, the result cannot be changed, and types stay distinct.

    The first part is the same reuse problem as elsewhere: the caller's list is edited
    right after the key is built, and the key must not have moved.

    The rest is about values that compare equal in Python but are different keys to the
    service. True and one, zero and minus zero, and one as a whole number and one as a
    fraction all land in different places. If any pair were treated as the same, a lookup
    could be sent to the wrong partition and find nothing.
    """
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
    """A caller's own type based on text or a number is read for its value, not its behavior.

    Each of the three classes here overrides the method Python would normally use to turn
    it into text or a number, and each returns something deliberately wrong. The key that
    comes out has to carry the real underlying value.

    This is not far-fetched: wrappers built on top of text and numbers are common, and
    they are often the thing being used as a key. Asking such an object how it prefers to
    be displayed would send the request to a partition chosen by that answer.
    """
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
    """Text arriving in either encoding form becomes one key, and saved bookmarks still match.

    Characters outside the common range can reach Python as a single character or as the
    two halves that encode it. Both must produce the same key, or the same customer id
    would reach two different partitions depending on where the string came from.

    Halves that are not part of a pair are left exactly as they are rather than repaired
    or rejected, because they may be what the caller genuinely stored.

    The bookmark check is the compatibility one: however the text arrived, the saved
    paging text comes out identical to what the old code wrote, so a bookmark stored
    before this change still works. The caller's list is checked afterwards to confirm it
    was not altered along the way.
    """
    assert normalize_partition_key(value).values == (expected,)
    components = ["tenant", value, None]
    for key in (
        normalize_partition_key(components),
        query_partition_key_components(components),
    ):
        assert key.values == ("tenant", expected, None)
        assert serialize_partition_key_for_continuation(key) == json.dumps(
            components, separators=(",", ":"), allow_nan=False
        )
    assert components == ["tenant", value, None]


@pytest.mark.parametrize("key_shape", ["scalar", "hierarchical", "query"])
@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_native_unicode_key_extraction_matches_legacy(key_shape, async_mode):
    """The Rust side accepts such a key, whether built directly or read back from old text.

    Two keys are tried for each shape: one built from the value as the caller gave it, and
    one built from the text the old code would have produced. Both have to get past the
    Rust side's own reading of the key and fail only at the point of looking for a driver,
    which is the first thing after the key is accepted.

    Failing with "no driver registered" is therefore the success condition here -- it
    proves the key was read without complaint and nothing was sent. Single values,
    multi-part keys and query keys are each checked, for both call styles.
    """
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
    """Reading a change feed on a container with no partition key keeps that meaning.

    This is the one place the distinction was most easily lost. Asking for changes in a
    container that has no partition key, and asking for changes where the key is nothing,
    are different requests; the first covers the whole container. Turning one into the
    other would quietly return a different set of changes.
    """
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
    """Values the service cannot store as a key are refused here, with a reason.

    Three groups, each verified by running them. Numbers that are not a finite value the
    service can hold: not-a-number, infinity, and a whole number too large to represent.
    More than three parts, which is the most a key can have. And types that are not keys
    at all: a mapping with something in it, raw bytes, a nested list, and a placeholder
    object.

    Refusing early means the caller sees the value they passed named in the error, rather
    than a rejection from the service or an item written where they cannot find it.
    """
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
    """The record refuses to exist in a state that does not make sense.

    These are mistakes only SDK code could make, and each is checked by running it: a
    situation name nobody knows; saying there are values but giving none; giving them in
    a form that can still be changed afterwards; attaching values to a situation that by
    definition has none, such as searching every partition or taking the key from the
    item; and an empty mapping where the missing-path marker belongs, since the empty
    mapping is how that case is written down on the wire, not how it is held here.

    Checking at construction is what lets everything downstream trust the record without
    re-checking it.
    """
    with pytest.raises((ValueError, TypeError)):
        BindingPartitionKey(kind, values)


@pytest.mark.parametrize(
    "value,expected",
    [("customer-17", "customer-17"), ("\ud83d\ude00", "\U0001f600")],
)
def test_read_preparation_does_not_encode_or_decode_partition_json(
    monkeypatch, value, expected
):
    """Preparing a read never writes the key out as text or reads it back.

    Both JSON functions are replaced with ones that fail the test if called, so this is
    proof rather than inspection. The key goes straight from the caller's value into the
    record, and the finished request has no text form of it at all.

    Two things follow. Every read avoids work that used to happen on each call. And there
    is no second copy that could disagree with the first, which is what made the old code
    hard to follow: the text was written, passed on, and read back to recover what was
    already known.
    """
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
    assert prepared.partition_key == BindingPartitionKey("components", (expected,))
    assert not hasattr(prepared, "partition_key_header")


def test_customer_header_is_decoded_only_at_the_external_input_boundary():
    """Reading a key from text happens only where a customer actually supplied text.

    A caller may set the partition key header themselves, and that text has to be read.
    This is the only place reading is correct, and the three special values survive it:
    nothing, true, and the missing-path marker written as an empty object.

    An empty list here means search every partition, not a container without a key. That
    is the reading that matches what a caller writing the header by hand means by it.
    """
    assert parse_customer_partition_key_header("[null,true,{}]") == BindingPartitionKey(
        "components", (None, True, UNDEFINED_PARTITION_KEY)
    )
    assert parse_customer_partition_key_header("[]").kind == "cross_partition"


@pytest.mark.parametrize(
    "resource,options,expected",
    [
        (
            "docs",
            {"partitionKey": "explicit"},
            BindingPartitionKey("components", ("explicit",)),
        ),
        ("dbs", {}, BindingPartitionKey("cross_partition")),
        ("colls", {}, BindingPartitionKey("cross_partition")),
    ],
)
def test_unused_raw_headers_are_not_parsed(resource, options, expected):
    """A leftover header that nobody needs is ignored rather than read and rejected.

    Each case carries a partition key header holding text that is not valid JSON. If the
    code read headers on the chance that one mattered, every case here would fail.

    Instead the key comes from where it should: the named option when there is one, and
    otherwise no key at all, because listing databases or containers is not scoped to a
    partition. Reading the header would turn a harmless leftover into an error.
    """
    from azure.cosmos._query_rust_routing import _build_prepared_page_request

    request = _build_prepared_page_request(
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
    """Nine Rust entry points refuse a key component they do not understand, before sending.

    The request here is deliberately not the real record -- it is a stand-in whose key
    holds a bare empty mapping. That shape could only arrive from code that went around
    the checked record, so this is the Rust side not trusting what it is handed.

    It matters because the alternative is worse than an error: a component that cannot be
    read could be skipped or guessed at, and the request would then go to a partition the
    caller never asked for. The driver handle is not real, so anything reaching the point
    of using it would fail differently.
    """
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
    """An older request that still carries the key as text is refused on the version alone.

    The stand-in here has the previous version number and a key in the old text form. The
    Rust side must stop at the version and never look at that text, even though the text
    is right there and readable.

    If it read the text instead, a version that has moved on in other ways would appear
    to work, and the mismatch would show up later as wrong behavior rather than a clear
    error. Four entry points are checked, in both call styles.
    """
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
    """A request cannot be built with the key as text, for either point calls or queries.

    Passing the old text form is refused at construction. Without this the two forms
    could coexist and every reader would have to handle both, which is the situation this
    work set out to end.
    """
    with pytest.raises(TypeError, match="BindingPartitionKey"):
        PreparedRequest("read_item", "dbs/d/colls/c", b"", '["tenant"]')
    with pytest.raises(TypeError, match="BindingPartitionKey"):
        PreparedPageRequest("query_items", "dbs/d/colls/c", partition_key='["tenant"]')


@pytest.mark.parametrize(
    "op,payload,error,message",
    [
        (
            "query_items",
            {"query": {"query": "SELECT * FROM c"}, "allow_cross_partition": True},
            TypeError,
            "typed query_scope",
        ),
        (
            "query_items_change_feed", {"mode": "LatestVersion", "start": "Now"},
            ValueError, "Invalid retained feed request",
        ),
    ],
)
@pytest.mark.parametrize("async_mode", [False, True])
def test_retained_native_readers_reject_old_body_scope_contract(
    op, payload, error, message, async_mode
):
    """Neither feed accepts the old body as a substitute for typed routing.

    Retained SQL now requires query_scope outside its service body. Change feed
    still decodes its mode/start body and rejects an embedded legacy key.
    Both failures occur before driver lookup.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    request = PreparedRequest(
        op,
        "dbs/d/colls/c",
        json.dumps({**payload, "partition_key": '["tenant"]'}).encode(),
        BindingPartitionKey("cross_partition"),
    )
    method = (
        native.fetch_page_with_cursor_async if async_mode else native.fetch_page_with_cursor
    )
    with pytest.raises(error, match=message):
        method("unused-handle", request, native._ItemFeedCursor())


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
    """Asking which range of the container a key belongs to keeps the inputs apart.

    A container with no partition key and an empty list stay distinct from each other and
    from a real value. Answering the wrong one hands back a range covering the wrong part
    of the container, and a caller who then reads with that range quietly sees the wrong
    items.

    The last two cases -- a missing key path and nothing as a value -- both count as
    having a value, so they agree here; what separates them is the value itself, which
    this test does not look at. The empty body is checked because this asks a question
    rather than sending anything.
    """
    from azure.cosmos._feed_ranges_rust_routing import (
        build_feed_range_from_partition_key_prepared_request,
    )

    request = build_feed_range_from_partition_key_prepared_request(
        container_link="dbs/d/colls/c",
        partition_key_value=value,
    )
    assert request.partition_key.kind == kind
    assert request.body_bytes == b""
