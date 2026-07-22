# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fast, in-process tests for the async create helper (no network, no emulator).

The async helper does the same work as the sync one, which is covered in
``tests/create_item/sync/test_item_helper_unit.py``. These two tests check
only the parts that are awaited on the async side: the call to the
existing client, and the cache refresh when the container is not cached
yet. ``backend=None`` (core-python) routes through the explicit
``AsyncLegacyBackend`` so the existing client is what actually runs.
"""
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


class TestAsyncItemHelper(unittest.TestCase):
    """Checks the two steps the async create helper awaits.

    When no backend handles the call, the helper awaits the existing
    client; and when the container is not cached yet, it awaits the cache
    refresh first.
    """

    def test_async_dispatch_falls_through_to_create_item(self):
        """When the backend does nothing, the helper calls the existing
        client and returns its result."""
        cc = MagicMock()
        cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": "rid"}}
        cc._AddPartitionKey = AsyncMock(
            side_effect=lambda _l, _d, opts: dict(opts, partitionKey="stub-pk")
        )
        cc.CreateItem = AsyncMock(return_value="async-result")

        async def _run():
            return await AsyncItemHelper(None, cc).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

        result = asyncio.run(_run())
        self.assertEqual(result, "async-result")
        cc.CreateItem.assert_awaited_once()

    def test_async_cache_miss_awaits_refresh(self):
        """When the container is not cached yet, the helper refreshes the
        cache and then uses the freshly fetched resource id."""
        cc = MagicMock()
        cache = {}

        async def refresh(link):
            cache[link] = {"_rid": "rid-after-async-refresh"}

        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = AsyncMock(side_effect=refresh)
        cc._AddPartitionKey = AsyncMock(
            side_effect=lambda _l, _d, opts: dict(opts, partitionKey="stub-pk")
        )
        cc.CreateItem = AsyncMock(return_value="ok")

        async def _run():
            await AsyncItemHelper(None, cc).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

        asyncio.run(_run())
        cc._refresh_container_properties_cache.assert_awaited_once_with("dbs/db/colls/c")
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-async-refresh")


if __name__ == "__main__":
    unittest.main()

