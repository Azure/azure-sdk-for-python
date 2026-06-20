# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the async delete path (no network).

The async version of the sync delete tests. They check that any options
the caller passes are kept (not thrown away) and that a Rust backend, when
set, handles the delete instead of the existing client.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse, OP_DELETE_ITEM
from azure.cosmos.aio._container import ContainerProxy


def _make_async_proxy(rid="rid-cached"):
    """Build a real async container over a fake connection."""
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {container_link: {"_rid": rid}}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache

    cc._backend = None
    cc.DeleteItem = AsyncMock(return_value=None)

    proxy = ContainerProxy(cc, "dbs/db", "c")
    return proxy, cc


class _CapturingAsyncBackend:
    """A fake async backend that records the request it was given."""

    name = "rust"

    def __init__(self):
        self.executed = False
        self.prepared = None

    async def execute(self, prepared):
        self.executed = True
        self.prepared = prepared
        return BackendResponse(
            status_code=204,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v1"}),
            body=b"",
        )


class TestAsyncContainerDeleteItemRouting(unittest.IsolatedAsyncioTestCase):
    """The async delete behaves the same as the sync delete."""

    async def test_string_item_resolves_to_document_link(self):
        """A delete by id string targets that document."""
        proxy, cc = _make_async_proxy()

        await proxy.delete_item("delete_item", "a")

        cc.DeleteItem.assert_awaited_once()
        self.assertEqual(
            cc.DeleteItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/delete_item",
        )

    async def test_caller_request_options_are_merged_not_overwritten(self):
        """Options the caller passes are kept alongside the partition key
        (the async half of the merge guard)."""
        proxy, cc = _make_async_proxy()

        await proxy.delete_item(
            "delete_item", "a",
            request_options={"customKey": "customValue"},
        )

        forwarded_options = cc.DeleteItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["customKey"], "customValue")
        self.assertEqual(forwarded_options["partitionKey"], "a")

    async def test_delete_routes_to_backend_with_item_id(self):
        """A delete goes to the Rust backend with the document id; the
        existing client is not called and the call returns nothing."""
        proxy, cc = _make_async_proxy()
        backend = _CapturingAsyncBackend()
        cc._backend = backend

        result = await proxy.delete_item("delete_item", "a")

        self.assertTrue(backend.executed)
        cc.DeleteItem.assert_not_awaited()
        self.assertEqual(backend.prepared.op, OP_DELETE_ITEM)
        self.assertEqual(backend.prepared.item_id, "delete_item")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

