# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Write snapshots and legacy encoding parity, without account access."""

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
    body = {"id": "item", "value": text}
    for enabled, expected in ((False, escaped), (True, compact)):
        result = serialize_document(body, operation="create_item", compact_utf8=enabled)
        assert result.body_bytes == b'{"id":"item","value":"' + expected + b'"}'


@pytest.mark.parametrize("operation", WRITES)
def test_builders_only_reuse_snapshots(operation, monkeypatch):
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
    class MisleadingGet(dict):
        def get(self, name, default=None):
            return "wrong" if name == "id" else super().get(name, default)

    result = serialize_document(MisleadingGet(id="right"), operation=operation)
    assert result.body_id == json.loads(result.body_bytes)["id"] == "right"


@pytest.mark.parametrize("operation", DOCUMENT_WRITES)
@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("body_id", ["\u65e5\u672c", "\U0001f600", "\ud83d\ude00"])
def test_unicode_body_id_matches_json_and_utf8(operation, compact, body_id):
    document = serialize_document(
        {"id": body_id}, operation=operation, compact_utf8=compact
    )
    assert document.body_id == json.loads(document.body_bytes)["id"]
    document.body_id.encode("utf-8")


@pytest.mark.parametrize("operation", WRITES)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_policy_is_not_silently_unified(operation, value):
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
    args, options = normalize_item_arguments(
        "replace_item", arguments("replace_item", body)
    )
    prepared = build_item_request("replace_item", args, options, ItemClientDefaults())
    assert prepared.item_id == "target"
    assert prepared.body_bytes == (b"" if body is None else b'{"id":"body"}')
