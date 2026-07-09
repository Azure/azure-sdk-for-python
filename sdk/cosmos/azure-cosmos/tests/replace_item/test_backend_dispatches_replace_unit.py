# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The rust backend routes ``replace_item`` through the compiled binding.

``replace_item`` is a first-class rust operation: the driver exposes
``CosmosOperation::replace_item`` (mapped to ``OperationType::Replace``,
an overwrite-only PUT), and the binding's ``replace_item`` entry point
maps to it. ``RustBackend.execute`` therefore dispatches an
``OP_REPLACE_ITEM`` request to ``_rust_module.replace_item`` -- the same
dispatch shape create / read / delete / upsert use -- and wraps the
returned 4-tuple as a ``BackendResponse``.

These tests mock the compiled binding so they exercise the dispatch path
without a real Cosmos account or a built ``_rust.pyd``. The most
important assertion is that an ``OP_REPLACE_ITEM`` op routes to the
binding's ``replace_item`` and **never** to ``upsert_item`` -- the two
write-with-body ops share prep code but must hit different driver entry
points (insert-or-replace vs overwrite-only).

Sibling of ``tests/upsert_item/test_backend_dispatches_upsert_unit.py``.
"""
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend.base import OP_REPLACE_ITEM, PreparedRequest
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos.aio._backend.rust import AsyncRustBackend


def _replace_prepared() -> PreparedRequest:
    return PreparedRequest(
        op=OP_REPLACE_ITEM,
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"order-42","pk":"customerA","total":129.0}',
        partition_key_header='["customerA"]',
        headers={},
        item_id="order-42",
    )


def test_sync_rust_backend_dispatches_replace_to_binding(monkeypatch):
    """The sync backend calls the binding's ``replace_item`` (not
    ``upsert_item`` and not ``create_item``) for a replace op and wraps the
    4-tuple it returns. A 200 here models the overwrite."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.replace_item.return_value = (200, 0, {"etag": "v2"}, b'{"id":"order-42"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = _replace_prepared()
    resp = backend.execute(prepared)

    fake_module.replace_item.assert_called_once_with("handle-1", prepared)
    # The op discriminator must route to replace, never to the sibling
    # write-with-body ops.
    fake_module.upsert_item.assert_not_called()
    fake_module.create_item.assert_not_called()
    assert resp.status_code == 200
    assert resp.body == b'{"id":"order-42"}'


def test_sync_rust_backend_replace_surfaces_412(monkeypatch):
    """A version-guarded replace whose etag is stale comes back as a 412
    4-tuple (not a raised binding error). The backend wraps it as a
    ``BackendResponse`` for the parser to map to the typed exception."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.replace_item.return_value = (412, 0, {}, b'{"message":"precondition failed"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    resp = backend.execute(_replace_prepared())

    assert resp.status_code == 412
    fake_module.replace_item.assert_called_once()


def test_async_rust_backend_dispatches_replace_to_binding(monkeypatch):
    """Async sibling: the replace op is awaited on the binding's async
    ``replace_item_async`` function, never the sync ``replace_item`` and never a
    sibling write-with-body op."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.replace_item_async = AsyncMock(
        return_value=(200, 0, {"etag": "v2"}, b'{"id":"order-42"}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = _replace_prepared()
        resp = await backend.execute(prepared)
        fake_module.replace_item_async.assert_awaited_once_with("handle-1", prepared)
        fake_module.upsert_item_async.assert_not_called()
        fake_module.create_item_async.assert_not_called()
        # The true-async path must not touch the blocking sync entry point.
        fake_module.replace_item.assert_not_called()
        assert resp.status_code == 200
        assert resp.body == b'{"id":"order-42"}'

    asyncio.run(_run())


def test_sync_rust_backend_replace_raises_when_binding_not_built(monkeypatch):
    """Before ``maturin develop`` builds ``_rust.pyd``, a replace on the
    rust backend raises the same clear ``NotImplementedError`` every other
    op raises -- never a silent wrong-op dispatch."""
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", None)
    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    with pytest.raises(NotImplementedError, match="not present"):
        backend.execute(_replace_prepared())


def test_async_rust_backend_replace_raises_when_binding_not_built(monkeypatch):
    """Async sibling of the not-built guard."""
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", None)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        with pytest.raises(NotImplementedError, match="not present"):
            await backend.execute(_replace_prepared())

    asyncio.run(_run())


if __name__ == "__main__":

    sys.exit(pytest.main([__file__, "-v"]))

