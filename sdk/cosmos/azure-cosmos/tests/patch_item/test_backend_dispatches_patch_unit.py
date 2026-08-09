# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The rust backend routes ``patch_item`` through the compiled binding.

``RustBackend.execute`` dispatches an ``OP_PATCH_ITEM`` request to the
binding's ``patch_item`` entry point and wraps the returned tuple as a
``BackendResponse``.

These tests mock the compiled binding, so they run without a real Cosmos
account or a built ``_rust.pyd``. The key assertion is that an
``OP_PATCH_ITEM`` request routes to ``patch_item`` and never to
``replace_item``.
"""
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend.base import OP_PATCH_ITEM, PreparedRequest
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos.aio._backend.rust import AsyncRustBackend


def _patch_prepared() -> PreparedRequest:
    """Build a patch request for the item routing tests."""
    return PreparedRequest(
        op=OP_PATCH_ITEM,
        container_link="dbs/d/colls/c",
        # The body is the driver's PatchInstructions payload, not a document.
        body_bytes=b'{"operations":[{"op":"set","path":"/status","value":"shipped"}]}',
        partition_key_header='["customerA"]',
        headers={},
        item_id="order-42",
    )


def test_sync_rust_backend_dispatches_patch_to_binding(monkeypatch):
    """The sync backend calls the binding's ``patch_item`` (not
    ``replace_item`` and not ``create_item``) for a patch op and wraps the
    4-tuple it returns. A 200 here models the patched document coming
    back."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.patch_item.return_value = (200, 0, {"etag": "v2"}, b'{"id":"order-42","status":"shipped"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = _patch_prepared()
    resp = backend.execute(prepared)

    fake_module.patch_item.assert_called_once_with("handle-1", prepared)
    # The op discriminator must route to patch, never to the overwrite-only
    # replace entry point or any other op.
    fake_module.replace_item.assert_not_called()
    fake_module.create_item.assert_not_called()
    fake_module.upsert_item.assert_not_called()
    assert resp.status_code == 200
    assert resp.body == b'{"id":"order-42","status":"shipped"}'


def test_sync_rust_backend_patch_surfaces_404(monkeypatch):
    """Patching a missing item: the driver's read leg returns 404, which
    arrives as a 404 4-tuple (not a raised binding error). The backend wraps
    it as a ``BackendResponse`` for the parser to map to the typed
    ``CosmosResourceNotFoundError``."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.patch_item.return_value = (404, 0, {}, b'{"message":"not found"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    resp = backend.execute(_patch_prepared())

    assert resp.status_code == 404
    fake_module.patch_item.assert_called_once()


def test_async_rust_backend_dispatches_patch_to_binding(monkeypatch):
    """Async sibling: the patch op is awaited on the binding's async
    ``patch_item_async`` function, never the sync ``patch_item`` and never
    ``replace_item_async``."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.patch_item_async = AsyncMock(
        return_value=(200, 0, {"etag": "v2"}, b'{"id":"order-42","status":"shipped"}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = _patch_prepared()
        resp = await backend.execute(prepared)
        fake_module.patch_item_async.assert_awaited_once_with("handle-1", prepared)
        fake_module.replace_item_async.assert_not_called()
        fake_module.create_item_async.assert_not_called()
        fake_module.patch_item.assert_not_called()
        assert resp.status_code == 200
        assert resp.body == b'{"id":"order-42","status":"shipped"}'

    asyncio.run(_run())


def test_sync_rust_backend_patch_raises_when_binding_not_built(monkeypatch):
    """Before ``maturin develop`` builds ``_rust.pyd``, a patch on the rust
    backend raises the same clear ``NotImplementedError`` every other op
    raises -- never a silent wrong-op dispatch."""
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", None)
    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    with pytest.raises(NotImplementedError, match="not present"):
        backend.execute(_patch_prepared())


def test_async_rust_backend_patch_raises_when_binding_not_built(monkeypatch):
    """Async sibling of the not-built guard."""
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", None)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        with pytest.raises(NotImplementedError, match="not present"):
            await backend.execute(_patch_prepared())

    asyncio.run(_run())


if __name__ == "__main__":

    sys.exit(pytest.main([__file__, "-v"]))

