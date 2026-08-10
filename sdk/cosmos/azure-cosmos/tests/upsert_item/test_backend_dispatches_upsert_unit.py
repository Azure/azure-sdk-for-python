# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The rust backend routes ``upsert_item`` through the compiled binding.

``upsert_item`` is a first-class rust operation: the driver exposes
``CosmosOperation::upsert_item``, and the binding's ``upsert_item`` entry
point maps to it (the driver stamps ``x-ms-documentdb-is-upsert`` and
POSTs to the collection feed, so an existing ``(partition_key, id)`` is
replaced rather than rejected with 409). ``RustBackend.execute`` therefore
dispatches an ``OP_UPSERT_ITEM`` request to ``_rust_module.upsert_item`` --
the same dispatch shape create / read / delete use -- and wraps the
returned 4-tuple as a ``BackendResponse``.

These tests mock the compiled binding so they exercise the dispatch path
without a real Cosmos account. Sibling of
``tests/common/test_backend_wiring_unit.py``.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend.operations import OP_UPSERT_ITEM
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos.aio._backend.rust import AsyncRustBackend


def _upsert_prepared() -> PreparedRequest:
    """Build an upsert request for the operation routing tests."""
    return PreparedRequest(
        op=OP_UPSERT_ITEM,
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"order-42","pk":"customerA"}',
        partition_key_header='["customerA"]',
        headers={},
    )


def test_sync_rust_backend_dispatches_upsert_to_binding(monkeypatch):
    """The sync backend calls the binding's ``upsert_item`` (not
    ``create_item``) for an upsert op and wraps the 4-tuple it returns.
    A 200 here models the replace half of insert-or-replace."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.upsert_item.return_value = (200, 0, {"etag": "v2"}, b'{"id":"order-42"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = _upsert_prepared()
    resp = backend.execute(prepared)

    fake_module.upsert_item.assert_called_once_with("handle-1", prepared)
    # The op discriminator must route to upsert, never to create.
    fake_module.create_item.assert_not_called()
    assert resp.status_code == 200
    assert resp.body == b'{"id":"order-42"}'


def test_async_rust_backend_dispatches_upsert_to_binding(monkeypatch):
    """Async sibling: the upsert op is awaited on the binding's async
    ``upsert_item_async`` function, never the sync ``upsert_item`` and never
    ``create_item_async``. A 201 here models the insert half."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.upsert_item_async = AsyncMock(
        return_value=(201, 0, {"etag": "v1"}, b'{"id":"order-42"}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = _upsert_prepared()
        resp = await backend.execute(prepared)
        fake_module.upsert_item_async.assert_awaited_once_with("handle-1", prepared)
        fake_module.create_item_async.assert_not_called()
        fake_module.upsert_item.assert_not_called()
        assert resp.status_code == 201
        assert resp.body == b'{"id":"order-42"}'

    asyncio.run(_run())


def test_sync_rust_backend_upsert_raises_when_binding_not_built(monkeypatch):
    """Before ``maturin develop``, an upsert on the rust backend raises
    the same clear ``NotImplementedError`` every other op raises --
    upsert is no longer special-cased to silently defer to legacy."""
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", None)
    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    with pytest.raises(NotImplementedError, match="not present"):
        backend.execute(_upsert_prepared())

