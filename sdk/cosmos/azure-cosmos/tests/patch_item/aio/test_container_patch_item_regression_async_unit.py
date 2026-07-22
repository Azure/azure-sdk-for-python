# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the async patch path (no network).

The async version of the sync patch tests. They check that options the
caller passes are kept, that a plain patch goes to the Rust backend, and
that a patch with a filter goes to the existing client instead.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse, OP_PATCH_ITEM
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._container import ContainerProxy


_OPERATIONS = [
    {"op": "add", "path": "/color", "value": "yellow"},
    {"op": "incr", "path": "/number", "value": 7},
]


def _make_async_proxy(rid="rid-cached"):
    """Build a real async container over a fake connection."""
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {container_link: {"_rid": rid}}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache

    cc._backend = None
    cc.PatchItem = AsyncMock(return_value={"id": "patch_item", "_rid": rid})

    proxy = ContainerProxy(cc, "dbs/db", "c")
    return proxy, cc


class _CapturingAsyncBackend(AsyncCosmosBackend):
    """A fake async backend that records the request it was given."""

    name = "rust"

    def __init__(self):
        self.executed = False
        self.prepared = None

    async def execute(self, prepared):
        self.executed = True
        self.prepared = prepared
        return BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v2"}),
            body=b'{"id":"patch_item","number":10}',
        )


class TestAsyncContainerPatchItemRouting(unittest.IsolatedAsyncioTestCase):
    """The async patch behaves the same as the sync patch."""

    async def test_caller_request_options_are_merged_not_overwritten(self):
        """Options the caller passes are kept alongside the partition key
        (the async half of the merge guard)."""
        proxy, cc = _make_async_proxy()

        await proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            request_options={"customKey": "customValue"},
        )

        forwarded_options = cc.PatchItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["customKey"], "customValue")
        self.assertEqual(forwarded_options["partitionKey"], "a")

    async def test_plain_patch_routes_to_backend(self):
        """A plain patch goes to the Rust backend; the existing client is
        not called."""
        proxy, cc = _make_async_proxy()
        backend = _CapturingAsyncBackend()
        cc._backend = backend

        await proxy.patch_item("patch_item", "a", _OPERATIONS)

        self.assertTrue(backend.executed)
        cc.PatchItem.assert_not_awaited()
        self.assertEqual(backend.prepared.op, OP_PATCH_ITEM)
        self.assertEqual(backend.prepared.item_id, "patch_item")

    async def test_filter_predicate_patch_falls_back_to_legacy(self):
        """A patch with a filter goes to the existing client, not the Rust
        backend."""
        proxy, cc = _make_async_proxy()
        backend = _CapturingAsyncBackend()
        cc._backend = backend

        await proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            filter_predicate="from root where root.number = 3",
        )

        self.assertFalse(backend.executed)
        cc.PatchItem.assert_awaited_once()
        self.assertEqual(
            cc.PatchItem.call_args.kwargs["options"]["filterPredicate"],
            "from root where root.number = 3",
        )


if __name__ == "__main__":
    unittest.main()

