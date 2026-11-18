# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original batch serialization vectors at the Python/native boundary, not HTTP."""

import asyncio
import json
from unittest.mock import MagicMock

import pytest

from azure.cosmos._base import _format_batch_operations
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from execute_item_batch.test_batch_unit import AsyncBatchBackend, BatchBackend

ITEM = {"id": "item-\u65e5\u672c", "text": "\u0e44\u0e17\u0e22 \U0001f389"}
READ = ("read", (ITEM["id"],))
DELETE = ("delete", (ITEM["id"],))
WRITES = [
    ("create", (ITEM,)),
    ("upsert", (ITEM,)),
    ("replace", (ITEM["id"], ITEM)),
    (
        "patch",
        (ITEM["id"], [{"op": "add", "path": "/text", "value": "\u0e44\u0e17\u0e22"}]),
    ),
]
VECTORS = [
    ([READ, ("read", ("item-\u0e44\u0e17\u0e22",))], False),
    ([DELETE, ("delete", ("item-\u0e44\u0e17\u0e22",))], False),
    ([READ, ("delete", ("item-\u0e44\u0e17\u0e22",))], False),
    ([], False),
    *[([operation], True) for operation in WRITES],
    ([READ, WRITES[0]], True),
]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("operations,has_body", VECTORS)
def test_original_batch_serialization_vectors_rust(
    asynchronous, compact, operations, has_body
):
    backend = AsyncBatchBackend() if asynchronous else BatchBackend()
    context = ItemClientContext(
        backend, defaults=ItemClientDefaults(enable_compact_utf8_item_writes=compact)
    )
    connection = MagicMock()
    connection.Batch.side_effect = AssertionError(
        "Native serialization used legacy Batch"
    )
    proxy = AsyncContainerProxy if asynchronous else ContainerProxy
    container = proxy(connection, "dbs/db", "orders", _item_context=context)
    result = container.execute_item_batch(operations, "p")
    if asynchronous:
        asyncio.run(result)
    connection.Batch.assert_not_called()
    body = backend.send.call_args.args[0].body_bytes
    expected = json.dumps(
        _format_batch_operations(operations),
        separators=(",", ":"),
        ensure_ascii=not (compact and has_body),
    )
    assert isinstance(body, bytes)
    assert body == expected.encode("utf-8")
    assert len(body) == len(expected.encode("utf-8"))
    if operations:
        assert ("\u65e5\u672c" in body.decode("utf-8")) is (compact and has_body)
        assert ("\\u65e5" in body.decode("utf-8")) is not (compact and has_body)


def test_original_batch_wire_shape_rust():
    with_body = _format_batch_operations(WRITES)
    without_body = _format_batch_operations([READ, DELETE])
    for operation in with_body:
        assert "resourceBody" in operation
    for operation in without_body:
        assert "resourceBody" not in operation
        assert "id" in operation
