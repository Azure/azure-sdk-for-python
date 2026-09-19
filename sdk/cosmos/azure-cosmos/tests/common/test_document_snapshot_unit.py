# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""How an item body is turned into bytes, and when.

The body is encoded once, early, and the same bytes are used from then on. Two things
follow from that and both are checked here. The bytes must match what the older path
produced, down to the last byte, or the same item written through the two paths would
not be the same item. And once taken, the bytes must stop tracking the caller's
dictionary, so that changing it afterwards cannot change what is already on its way.

Nothing here reaches an account. The encoding is compared against the older encoder
running in the same process, and in places against fixed bytes written out by hand, so
that a change to both encoders at once would still be caught.
"""

import asyncio
import json
from dataclasses import FrozenInstanceError
from types import MappingProxyType
from unittest.mock import MagicMock

import pytest

from azure.cosmos import _synchronized_request
from azure.cosmos._helpers import _document, _item_prep, legacy_item_helper
from azure.cosmos._helpers._document import SerializedDocument, serialize_document
from azure.cosmos._helpers._item_context import ItemClientDefaults
from azure.cosmos._helpers.item_helper import (
    ItemHelper,
    build_item_request,
    normalize_item_arguments,
)
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper
from common.test_connection_free_items_unit import AsyncBackend, Backend

from common.request_preparation import call_item_helper


WRITES = ("create_item", "upsert_item", "replace_item", "patch_item")
DOCUMENT_WRITES = WRITES[:3]


def arguments(operation, body):
    """Build the call arguments for one of the four writes, carrying the given body.

    Three of the four take the body directly. The fourth takes a list of changes instead,
    so the body is placed inside one change and a partition key is supplied, since that
    operation cannot work it out from a body it was never given.

    Having one place that knows this difference is what lets the tests below run the same
    body through all four without each one repeating the special case.
    """
    result = {"container_link": "dbs/d/colls/c", "item_id": "target"}
    if operation == "patch_item":
        result["patch_operations"] = [{"op": "set", "path": "/value", "value": body}]
        result["request_options"] = {"partitionKey": "p"}
    else:
        result["body"] = body
    return result


@pytest.mark.parametrize("operation", WRITES)
@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        "",
        "plain",
        "\u00e9",
        "\u65e5\u672c",
        "\U0001f600",
        "e\u0301",
        '"\\/\b\f\n\r\t\x00',
        "\ud83d\ude00",
        "\ud800",
        "\udfff",
        "\ude00\ud83d",
        "literal \\ud800 and \u00e9",
    ],
)
def test_encoding_matches_legacy(operation, compact, text):
    """The bytes are identical to the older encoder's, for text and numbers that are easy
    to get wrong.

    Same byte for byte, not merely the same meaning. Two encoders that agree on meaning
    can still disagree on spacing or on which characters get escaped, and a customer
    comparing stored items written before and after the change would see the difference.

    The text covers nothing, plain text, an accented letter, characters outside the Latin
    alphabet, an emoji, a letter with a combining mark, every character JSON has to
    escape, and several lone halves of a surrogate pair. That last group is the awkward
    one: they are not valid text on their own, and an encoder that tries to repair them
    silently changes the customer's data.

    The numbers alongside are equally awkward on purpose: negative zero, an integer far
    past what a double can hold, the smallest number that is not zero, and a very large
    one. Both escaping settings are run.
    """
    body = {
        "id": "item",
        "value": text,
        "nested": (
            None,
            True,
            False,
            -0.0,
            2**128 - 1,
            1.2345678901234567,
            5e-324,
            1e300,
        ),
    }
    args, options = normalize_item_arguments(
        operation, arguments(operation, body), compact_utf8=compact
    )
    request = build_item_request(operation, args, options, ItemClientDefaults())
    payload = (
        {"operations": [{"op": "set", "path": "/value", "value": body}]}
        if operation == "patch_item"
        else body
    )
    legacy = _synchronized_request._request_body_from_data(
        payload, ensure_ascii=not compact
    )
    expected = legacy.encode("utf-8") if isinstance(legacy, str) else legacy
    assert isinstance(request.body_bytes, bytes)
    assert request.body_bytes == expected


@pytest.mark.parametrize(
    "text,escaped,compact",
    [
        ("\u00e9", b"\\u00e9", b"\xc3\xa9"),
        ("\u65e5\u672c", b"\\u65e5\\u672c", b"\xe6\x97\xa5\xe6\x9c\xac"),
        ("\U0001f600", b"\\ud83d\\ude00", b"\xf0\x9f\x98\x80"),
        ("\ud83d\ude00", b"\\ud83d\\ude00", b"\xf0\x9f\x98\x80"),
        ("\ud800", b"\\ud800", b"\\ud800"),
        ("\udfff", b"\\udfff", b"\\udfff"),
        ("\ude00\ud83d", b"\\ude00\\ud83d", b"\\ude00\\ud83d"),
        ("\\ud800", b"\\\\ud800", b"\\\\ud800"),
    ],
)
def test_encoding_has_independent_golden_bytes(text, escaped, compact):
    """The same cases again, against bytes written out by hand rather than a second encoder.

    The test above compares one encoder to another. If both were changed together the
    comparison would still pass while every stored item changed. These bytes were written
    down once and are not produced by any code, so they catch exactly that.

    Both settings are listed for each case. They differ for characters that have a
    shorter form outside the Latin alphabet, and are the same for the broken surrogate
    halves, which are escaped either way because there is no valid shorter form to use.

    The last case is a string that merely looks like an escape sequence. It must come out
    with its backslash doubled, as ordinary text, and not be read as the character it
    resembles.
    """
    body = {"id": "item", "value": text}
    for enabled, expected in ((False, escaped), (True, compact)):
        result = serialize_document(body, operation="create_item", compact_utf8=enabled)
        assert result.body_bytes == b'{"id":"item","value":"' + expected + b'"}'


@pytest.mark.parametrize("operation", WRITES)
def test_builders_only_reuse_snapshots(operation, monkeypatch):
    """After the bytes are taken, the caller's dictionary is gone and is never encoded again.

    First the raw body is checked to have been removed from the arguments entirely, in
    the plain arguments and in the leftover keywords. If any copy of it survived,
    something later could still read it and pick up a change.

    Then the caller's dictionary is changed, at the top level and one level down, and the
    encoder is replaced with one that fails if called. Building the request twice must
    hand back the very same bytes, with no trace of the new values.

    Twice, because the first build could plausibly cache; the second proves it really is
    reuse. The identifier is checked as well: two of the four take it from the call and
    two from the body, and the one taken from the body must be the old value, since that
    is what was encoded.
    """
    source = {"id": "before", "nested": {"pk": "before"}}
    args, options = normalize_item_arguments(operation, arguments(operation, source))
    assert "body" not in args
    assert "patch_operations" not in args
    assert "body" not in args["kwargs"]
    assert "patch_operations" not in args["kwargs"]
    snapshot = (
        args["body_bytes"] if operation == "patch_item" else args["document"].body_bytes
    )
    source["id"] = "after"
    source["nested"]["pk"] = "after"
    forbidden = MagicMock(side_effect=AssertionError("builder tried to serialize"))
    monkeypatch.setattr(_document, "serialize_body_to_bytes", forbidden)
    monkeypatch.setattr(_item_prep, "serialize_body_to_bytes", forbidden)
    for _ in range(2):
        prepared = build_item_request(operation, args, options, ItemClientDefaults())
        assert prepared.body_bytes is snapshot
        assert b"after" not in prepared.body_bytes
        assert prepared.item_id == (
            "target" if operation in ("replace_item", "patch_item") else "before"
        )
    forbidden.assert_not_called()


@pytest.mark.parametrize("operation", WRITES)
@pytest.mark.parametrize("async_mode", [False, True])
def test_snapshot_once_before_execute_and_async_yield(
    operation, async_mode, monkeypatch
):
    """The body is encoded once, before the request is sent, even across a pause.

    The caller's dictionary is changed from inside the send itself. On the asynchronous
    side the send pauses first, which hands control back to the caller mid-flight -- the
    realistic version of this, where the same dictionary is reused by other work while a
    request is outstanding.

    The encoder is counted. Exactly one call, checked both at the moment of sending and
    again at the end, so a second encode afterwards would be caught too. The request that
    reached the sender must carry none of the later values, including a change added to
    the list of changes rather than to the body.
    """
    backend = AsyncBackend() if async_mode else Backend()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend)
    body = {"id": "before", "nested": {"pk": "before"}}
    call = arguments(operation, body)
    original = backend.execute
    owner = _item_prep if operation == "patch_item" else _document
    serialize = MagicMock(wraps=owner.serialize_body_to_bytes)
    monkeypatch.setattr(owner, "serialize_body_to_bytes", serialize)

    def mutate():
        serialize.assert_called_once()
        body["id"] = "after"
        body["nested"]["pk"] = "after"
        if operation == "patch_item":
            call["patch_operations"].append({"op": "remove", "path": "/other"})

    def run_sync(prepared, **kwargs):
        mutate()
        return original(prepared, **kwargs)

    async def run_async(prepared, **kwargs):
        await asyncio.sleep(0)
        mutate()
        return await original(prepared, **kwargs)

    monkeypatch.setattr(
        backend, "execute", run_async if async_mode else run_sync
    )
    result = call_item_helper(helper, operation, **call)
    if async_mode:
        asyncio.run(result)
    serialize.assert_called_once()
    request = backend.events[-1]
    assert b"after" not in request.body_bytes
    assert b"other" not in request.body_bytes
    assert request.item_id == (
        "target" if operation in ("replace_item", "patch_item") else "before"
    )


@pytest.mark.parametrize("operation", WRITES)
def test_wrapper_does_not_deepcopy_documents_or_call_legacy(operation, monkeypatch):
    """Nothing copies the item body, and none of the older preparation code runs.

    Copying was the obvious way to stop the caller changing a body in flight, and it
    works, but it costs a full duplicate of every item written. Encoding once achieves
    the same thing for free. The body used here refuses to be copied, so any attempt
    fails loudly instead of quietly costing time.

    The two older preparation functions are replaced with ones that fail if called. They
    are still present for the older path, and calling them here would mean the work was
    being done twice -- once wastefully, once for real.

    Exactly one request must reach the sender, which rules out a retry hiding a second
    attempt at preparation.
    """
    class NoDeepcopy(dict):
        def __deepcopy__(self, memo):
            raise AssertionError("document was deep-copied")

    forbidden = MagicMock(side_effect=AssertionError("legacy preparation was called"))
    monkeypatch.setattr(_synchronized_request, "_request_body_from_data", forbidden)
    monkeypatch.setattr(
        legacy_item_helper, "_prepare_legacy_create_item_body", forbidden
    )
    body = NoDeepcopy(id="item", value=NoDeepcopy(nested=[1, 2, 3]))
    backend = Backend()
    call_item_helper(ItemHelper(backend), operation, **arguments(operation, body))
    assert len(backend.events) == 1
    forbidden.assert_not_called()


def test_generated_id_is_resolved_once_without_mutating_a_mapping(monkeypatch):
    """A generated identifier is settled once, appears in the bytes, and leaves the caller's
    mapping untouched.

    When the caller asks for an identifier to be made for them, the obvious approach is to
    write it into their dictionary. That fails outright if what they passed cannot be
    written to, and it is rude even when it works. Here the body is passed as a read-only
    view and the original must come back unchanged.

    The generator is counted, so a second call cannot happen: building the request twice
    must give the same identifier both times. If it were generated again per build, a
    retry could store the item under a different identifier than the first attempt.

    The identifier reported alongside the bytes must be the one actually inside them, not
    a value held separately that could drift. The partition key is checked to be the kind
    read out of the body, and the finished bytes are checked to be unwritable, which is
    what makes reuse safe.
    """
    generated = MagicMock(return_value="generated")
    monkeypatch.setattr("azure.cosmos._helpers._document.uuid.uuid4", generated)
    original = {"nested": {"value": 1}}
    args, options = normalize_item_arguments(
        "create_item",
        {
            "container_link": "dbs/d/colls/c",
            "body": MappingProxyType(original),
            "enable_automatic_id_generation": True,
        },
    )
    document = args["document"]
    assert isinstance(document, SerializedDocument)
    assert original == {"nested": {"value": 1}}
    assert document.body_id == json.loads(document.body_bytes)["id"] == "generated"
    for _ in range(2):
        request = build_item_request("create_item", args, options, ItemClientDefaults())
        assert request.item_id == "generated"
        assert request.partition_key.kind == "extract"
    generated.assert_called_once()
    with pytest.raises(FrozenInstanceError):
        document.body_bytes = b"changed"


@pytest.mark.parametrize("operation", ("upsert_item", "replace_item"))
@pytest.mark.parametrize("body_id", [None, "", False, 42, "body-id"])
def test_upsert_and_replace_do_not_generate_or_rewrite_ids(
    operation, body_id, monkeypatch
):
    """These two never make up an identifier, even when asked to, and never alter the body.

    Making one up only makes sense for a write that creates something new. These two act
    on an item the caller has already named, so inventing a name would send the request
    somewhere the caller did not intend. The request asks for generation anyway and the
    generator is replaced with one that fails if called.

    The encoded bytes must read back as exactly the body that was passed in, whatever was
    in the identifier field -- absent, empty, the word false, a number, or real text. The
    identifier reported alongside is only set when the body held real text; everything
    else reports nothing rather than being repaired into something.
    """
    forbidden = MagicMock(side_effect=AssertionError("ID generation was called"))
    monkeypatch.setattr("azure.cosmos._helpers._document.uuid.uuid4", forbidden)
    body = {"id": body_id}
    call = arguments(operation, body)
    call["enable_automatic_id_generation"] = True
    normalized, _ = normalize_item_arguments(operation, call)
    document = normalized["document"]
    assert json.loads(document.body_bytes) == body
    assert document.body_id == (
        body_id if isinstance(body_id, str) and body_id else None
    )
    forbidden.assert_not_called()


@pytest.mark.parametrize("operation", DOCUMENT_WRITES)
def test_body_id_matches_the_encoded_dictionary_not_an_overridden_get(operation):
    """The reported identifier comes from what was encoded, not from asking the body for it.

    The body here is a dictionary subclass that lies when asked for a named field but
    holds the true value underneath, which is what the encoder writes out. Code that
    asked the body would get one answer and the bytes would say another, so the request
    would be addressed to one item and carry a different one.

    Unusual, but a dictionary subclass with its own lookup is an ordinary thing for a
    customer to write, and they would have no reason to expect it to matter here.
    """
    class MisleadingGet(dict):
        def get(self, name, default=None):
            return "wrong" if name == "id" else super().get(name, default)

    result = serialize_document(MisleadingGet(id="right"), operation=operation)
    assert result.body_id == json.loads(result.body_bytes)["id"] == "right"


@pytest.mark.parametrize("operation", DOCUMENT_WRITES)
@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("body_id", ["\u65e5\u672c", "\U0001f600", "\ud83d\ude00"])
def test_unicode_body_id_matches_json_and_utf8(operation, compact, body_id):
    """An identifier outside the Latin alphabet still matches its bytes and survives the
    trip into a header.

    The identifier is read back out of the encoded bytes and compared, under both
    escaping settings, so the escaping cannot change which item is named. Then it is
    encoded on its own, because it also travels in the request line and in headers, where
    anything that cannot be encoded fails far from here and with a much less helpful
    message.

    Both a real emoji and the pair of halves that spell the same one are covered: they
    must be treated as the same identifier, not as two different items.
    """
    document = serialize_document(
        {"id": body_id}, operation=operation, compact_utf8=compact
    )
    assert document.body_id == json.loads(document.body_bytes)["id"]
    document.body_id.encode("utf-8")


@pytest.mark.parametrize("operation", WRITES)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_policy_is_not_silently_unified(operation, value):
    """The four writes do not agree about numbers JSON cannot express, and that split is
    pinned here deliberately.

    Not a number and the two infinities have no JSON spelling. Two of the four refuse the
    call outright. The other two encode them the way the older path did, which produces
    output that is not strictly valid JSON, because changing that would break customers
    who are storing such values today.

    So this does not assert the behavior is right. It asserts that nobody quietly makes
    the four agree, in either direction, without it being a deliberate decision: today
    the same value is rejected by one write and accepted by another.
    """
    call = arguments(operation, {"id": "item", "value": value})
    if operation in ("create_item", "patch_item"):
        with pytest.raises(ValueError):
            normalize_item_arguments(operation, call)
    else:
        args, _ = normalize_item_arguments(operation, call)
        expected = _synchronized_request._request_body_from_data(call["body"]).encode(
            "utf-8"
        )
        assert args["document"].body_bytes == expected


@pytest.mark.parametrize("operation", WRITES)
@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("circular", [False, True])
def test_invalid_json_fails_before_backend_dispatch(operation, async_mode, circular):
    """A body that cannot be encoded fails before anything is sent.

    Two ways to be unencodable: a body that contains itself, and a body holding an object
    JSON knows nothing about. They raise different errors, and both must arrive before a
    request leaves.

    Failing early is the whole point. If the encoding happened further along, the caller
    would be charged for a request, might consume a retry, and would get the error back
    from somewhere much harder to connect to the line they wrote. The check is that
    nothing at all reached the sender.
    """
    body = {"id": "item"}
    body["value"] = body if circular else object()
    backend = AsyncBackend() if async_mode else Backend()
    helper = (AsyncItemHelper if async_mode else ItemHelper)(backend)
    with pytest.raises(ValueError if circular else TypeError):
        result = call_item_helper(helper, operation, **arguments(operation, body))
        if async_mode:
            asyncio.run(result)
    assert backend.events == []


@pytest.mark.parametrize(
    "body", [b'{"id":"body"}', bytearray(b'{"id":"body"}'), '{"id":"body"}', None]
)
def test_replacement_keeps_existing_preencoded_body_support(body):
    """A body that is already encoded is passed along untouched, and nothing at all becomes
    empty bytes.

    Some callers hand over bytes they encoded themselves, as raw bytes, as a writable
    byte buffer, or as text. All three must arrive as the same bytes: encoding text that
    is already JSON would wrap it in quotes and turn a real item into a string.

    Passing nothing sends an empty body rather than failing. The identifier still comes
    from the call in every case, since there may be no body to read one from.
    """
    args, options = normalize_item_arguments(
        "replace_item", arguments("replace_item", body)
    )
    prepared = build_item_request("replace_item", args, options, ItemClientDefaults())
    assert prepared.item_id == "target"
    assert prepared.body_bytes == (b"" if body is None else b'{"id":"body"}')
