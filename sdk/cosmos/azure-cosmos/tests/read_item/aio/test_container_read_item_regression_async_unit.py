# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the async read path (no network).

The async version of the sync read tests. They check that any options the
caller passes are kept (not thrown away) and that a Rust backend, when set,
handles the read instead of the existing client.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse, OP_READ_ITEM
from azure.cosmos.aio._container import ContainerProxy


def _make_async_proxy(rid="rid-cached"):
    """Build a real async container over a fake connection.

    The container is pre-cached so these tests stay focused on routing, not
    the cache refresh.
    """
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {container_link: {"_rid": rid}}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache

    cc._backend = None
    cc.ReadItem = AsyncMock(return_value={"id": "read_item", "_rid": rid})

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
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v1"}),
            body=b'{"id":"read_item","number":5}',
        )


class TestAsyncContainerReadItemRouting(unittest.IsolatedAsyncioTestCase):
    """The async read behaves the same as the sync read."""

    async def test_string_item_resolves_to_document_link(self):
        """A read by id string targets that document."""
        proxy, cc = _make_async_proxy()

        await proxy.read_item("read_item", "a")

        cc.ReadItem.assert_awaited_once()
        self.assertEqual(
            cc.ReadItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/read_item",
        )

    async def test_caller_request_options_are_merged_not_overwritten(self):
        """Options the caller passes are kept alongside the partition key
        (the async half of the merge guard)."""
        proxy, cc = _make_async_proxy()

        await proxy.read_item(
            "read_item", "a",
            request_options={"customKey": "customValue"},
        )

        forwarded_options = cc.ReadItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["customKey"], "customValue")
        self.assertEqual(forwarded_options["partitionKey"], "a")

    async def test_read_routes_to_backend_with_item_id(self):
        """A read goes to the Rust backend with the document id; the existing
        client is not called."""
        proxy, cc = _make_async_proxy()
        backend = _CapturingAsyncBackend()
        cc._backend = backend

        result = await proxy.read_item("read_item", "a")

        self.assertTrue(backend.executed)
        cc.ReadItem.assert_not_awaited()
        self.assertEqual(backend.prepared.op, OP_READ_ITEM)
        self.assertEqual(backend.prepared.item_id, "read_item")
        self.assertEqual(result["id"], "read_item")


if __name__ == "__main__":
    unittest.main()

