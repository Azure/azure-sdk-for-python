# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``AsyncItemHelper.upsert_item`` -- no network, no emulator.

``AsyncItemHelper`` mirrors the synchronous ``ItemHelper`` and shares
the option-build, request-prep, and merge helpers, so the wire-shape
behaviour is already pinned by the sync tests in
``tests/upsert_item/sync/``. This file covers only the async-specific
touchpoints upsert adds:

1. ``UpsertItem`` is awaited on the core-python path (``backend=None``,
   routed through the explicit ``AsyncLegacyBackend``).
2. The partition key is awaited out of the body (write-with-body), and
   ``etag`` / ``match_condition`` still reach the legacy options as the
   ``accessCondition`` an upsert honours.

Sibling of ``tests/create_item/aio/test_item_helper_async_unit.py``.
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.core import MatchConditions

from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


def _connection_with_cache(rid="rid"):
    """Provide cached routing data for async upsert tests."""
    cc = MagicMock()
    cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": rid}}
    # Write-with-body: the helper awaits the partition key out of the body.
    cc._AddPartitionKey = AsyncMock(
        side_effect=lambda _l, _d, opts: dict(opts, partitionKey="customerA")
    )
    cc.UpsertItem = AsyncMock(return_value="async-upsert-result")
    return cc


class TestAsyncUpsertItem(unittest.TestCase):
    """The core-python (``backend=None``) path is the async fall-through upsert path."""

    def test_async_dispatch_falls_through_to_upsert_item(self):
        """Core-python (``backend=None``) awaits ``UpsertItem`` and returns
        its value; the body and link are forwarded unchanged and id
        generation is disabled (an upsert never mints an id)."""
        cc = _connection_with_cache()
        body = {"id": "order-42", "pk": "customerA"}

        async def _run():
            return await AsyncItemHelper(None, cc).upsert_item(
                container_link="dbs/db/colls/c",
                body=body,
            )

        result = asyncio.run(_run())
        self.assertEqual(result, "async-upsert-result")
        cc.UpsertItem.assert_awaited_once()
        call = cc.UpsertItem.call_args
        self.assertEqual(call.kwargs["database_or_container_link"], "dbs/db/colls/c")
        self.assertEqual(call.kwargs["document"], body)
        self.assertIs(call.kwargs["options"]["disableAutomaticIdGeneration"], True)

    def test_async_upsert_threads_insert_only_access_condition(self):
        """``match_condition=IfMissing`` (insert-only) reaches the legacy
        options as the ``If-None-Match: *`` access condition on the async
        path too."""
        cc = _connection_with_cache()

        async def _run():
            await AsyncItemHelper(None, cc).upsert_item(
                container_link="dbs/db/colls/c",
                body={"id": "x", "pk": "customerA"},
                match_condition=MatchConditions.IfMissing,
            )

        asyncio.run(_run())
        options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertEqual(options["accessCondition"], {"type": "IfNoneMatch", "condition": "*"})

    def test_async_cache_miss_awaits_refresh_and_stamps_rid(self):
        """Async cache miss: ``_refresh_container_properties_cache`` is
        awaited and the refreshed rid is stamped into the options."""
        cc = MagicMock()
        cache = {}

        async def refresh(link):
            cache[link] = {"_rid": "rid-after-async-refresh"}

        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = AsyncMock(side_effect=refresh)
        cc._AddPartitionKey = AsyncMock(
            side_effect=lambda _l, _d, opts: dict(opts, partitionKey="a")
        )
        cc.UpsertItem = AsyncMock(return_value="ok")

        async def _run():
            await AsyncItemHelper(None, cc).upsert_item(
                container_link="dbs/db/colls/c",
                body={"id": "x", "pk": "a"},
            )

        asyncio.run(_run())
        cc._refresh_container_properties_cache.assert_awaited_once_with("dbs/db/colls/c")
        from azure.cosmos._constants import _Constants as Constants
        options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-async-refresh")


if __name__ == "__main__":
    unittest.main()

