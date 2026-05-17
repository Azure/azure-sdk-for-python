# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for the asynchronous ``AsyncItemHelper.create_item`` — no network, no Cosmos emulator.

What this file covers
---------------------
``AsyncItemHelper`` mirrors the contract of the synchronous
``ItemHelper`` (see
``tests/create_item/sync/test_item_helper_unit.py`` for the full
description of what the helper class does on every call).

This file covers only the two awaitable touchpoints the async
sibling adds:

1. ``CreateItem`` itself is awaited on the fall-through path.
2. ``_refresh_container_properties_cache`` is awaited on a
   cache-miss.

Everything else (option translation, container-rid stamping,
prepared-request handoff to the backend, user-agent stamping) is
identical between the two helpers and is exercised in the sync
tests, so we don't duplicate it here.
"""
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


def _async_fall_through_backend(name):
    """Build an async backend mock whose ``execute`` returns ``None``.

    ``None`` is the "fall through to legacy ``CreateItem``" contract
    the helper honors when a backend's ``execute`` produces nothing.
    Today no production backend uses this, but the contract is
    useful in tests that want to assert what the helper forwards to
    ``CreateItem`` without the helper's parse-side branch running on
    a junk ``BackendResponse``.
    """
    backend = MagicMock()
    backend.name = name
    backend.execute = AsyncMock(return_value=None)
    return backend


class TestAsyncItemHelper(unittest.TestCase):
    """``AsyncItemHelper`` mirrors the sync helper's contract with ``await`` in the right places.

    The two tests below cover the two awaitable touchpoints the
    async path adds compared to the sync helper: awaiting
    ``CreateItem`` itself on the fall-through path, and awaiting
    ``_refresh_container_properties_cache`` on a cache miss.
    """

    def test_async_dispatch_falls_through_to_create_item(self):
        """Async fall-through: ``CreateItem`` is awaited (the fall-through path is reached and produces the helper's return value)."""
        cc = MagicMock()
        cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": "rid"}}
        cc._AddPartitionKey = AsyncMock(
            side_effect=lambda _l, _d, opts: dict(opts, partitionKey="stub-pk")
        )
        cc.CreateItem = AsyncMock(return_value="async-result")

        async def _run():
            return await AsyncItemHelper(
                _async_fall_through_backend("core-python"), cc
            ).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

        result = asyncio.run(_run())
        self.assertEqual(result, "async-result")
        cc.CreateItem.assert_awaited_once()

    def test_async_cache_miss_awaits_refresh(self):
        """Async cache miss: ``_refresh_container_properties_cache`` is awaited and the refreshed rid is stamped."""
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
            await AsyncItemHelper(
                _async_fall_through_backend("core-python"), cc
            ).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

        asyncio.run(_run())
        cc._refresh_container_properties_cache.assert_awaited_once_with("dbs/db/colls/c")
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-async-refresh")


if __name__ == "__main__":
    unittest.main()

