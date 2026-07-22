# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``AsyncItemHelper.patch_item`` -- no network.

``AsyncItemHelper`` shares the option-build, request-prep, and merge helpers
with the sync ``ItemHelper``, so the wire shape is already pinned by the sync
tests in ``tests/patch_item/sync/``. This file covers the async-specific
points:

1. ``PatchItem`` is awaited on the core-python path (``backend=None``,
   routed through the explicit ``AsyncLegacyBackend``), with the resolved
   ``document_link``, the operations forwarded unchanged, and id generation
   disabled.
2. A wired backend's ``BackendResponse`` is parsed into a ``CosmosDict`` and
   ``PatchItem`` is not awaited.
3. A ``filter_predicate`` or ``etag`` / ``match_condition`` patch falls through
   to the legacy ``PatchItem`` instead of the backend.

The partition key arrives as ``request_options={"partitionKey": ...}`` in
kwargs, the way the container method seeds it.
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


_OPERATIONS = [
    {"op": "add", "path": "/color", "value": "yellow"},
    {"op": "incr", "path": "/number", "value": 7},
]


class _CapturingBackend(AsyncCosmosBackend):
    """A real ``AsyncCosmosBackend`` whose ``execute`` is a spy: it records
    calls (so ``.execute_mock.assert_not_awaited()`` still works) and returns
    ``response``. Inheriting from ``AsyncCosmosBackend`` gives
    ``run_operation`` its genuine default implementation, so ``rust_eligible``
    is honoured exactly as it is for the real rust backend."""

    name = "rust"

    def __init__(self, response):
        self.execute_mock = AsyncMock(return_value=response)

    async def execute(self, prepared):
        return await self.execute_mock(prepared)


def _async_dispatch_backend(response):
    """A real ``AsyncCosmosBackend`` whose ``execute`` returns ``response``
    (the rust dispatch path -- the helper parses it instead of falling
    through to ``PatchItem``)."""
    return _CapturingBackend(response)


def _connection_with_cache(rid="rid"):
    cc = MagicMock()
    cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": rid}}
    cc.PatchItem = AsyncMock(return_value="async-patch-result")
    return cc


class TestAsyncPatchItem(unittest.TestCase):
    """The core-python and rust-dispatch paths for async patch."""

    def test_async_dispatch_falls_through_to_patch_item(self):
        """Core-python (``backend=None``) awaits ``PatchItem`` and returns
        its value; the resolved ``document_link`` and the ``operations`` are
        forwarded unchanged and id generation is disabled (a patch never
        mints)."""
        cc = _connection_with_cache()

        async def _run():
            return await AsyncItemHelper(None, cc).patch_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/patch_item",
                item_id="patch_item",
                patch_operations=_OPERATIONS,
                request_options={"partitionKey": "a"},
            )

        result = asyncio.run(_run())
        self.assertEqual(result, "async-patch-result")
        cc.PatchItem.assert_awaited_once()
        call = cc.PatchItem.call_args
        self.assertEqual(call.kwargs["document_link"], "dbs/db/colls/c/docs/patch_item")
        self.assertEqual(call.kwargs["operations"], _OPERATIONS)
        self.assertIs(call.kwargs["options"]["disableAutomaticIdGeneration"], True)

    def test_async_backend_dispatch_parses_response_and_skips_legacy(self):
        """When the backend returns a ``BackendResponse`` (rust path), the
        helper parses it into a ``CosmosDict`` and never awaits the legacy
        ``PatchItem``."""
        cc = _connection_with_cache()
        response = BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v2"}),
            body=b'{"id":"patch_item","number":10}',
        )

        async def _run():
            return await AsyncItemHelper(_async_dispatch_backend(response), cc).patch_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/patch_item",
                item_id="patch_item",
                patch_operations=_OPERATIONS,
                request_options={"partitionKey": "a"},
            )

        result = asyncio.run(_run())
        self.assertEqual(result["id"], "patch_item")
        self.assertEqual(result.get_response_headers()["etag"], "v2")
        cc.PatchItem.assert_not_awaited()

    def test_async_filter_predicate_falls_back_to_legacy(self):
        """A ``filter_predicate`` patch never reaches the backend (its payload
        has no condition field); ``execute`` is not awaited and the call falls
        through to the legacy ``PatchItem``, which honours the filter."""
        cc = _connection_with_cache()
        backend = _async_dispatch_backend(
            BackendResponse(status_code=200, sub_status=0, headers=None, body=b"{}")
        )

        async def _run():
            await AsyncItemHelper(backend, cc).patch_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/patch_item",
                item_id="patch_item",
                patch_operations=_OPERATIONS,
                filter_predicate="from root where root.number = 3",
                request_options={"partitionKey": "a"},
            )

        asyncio.run(_run())
        backend.execute_mock.assert_not_awaited()
        cc.PatchItem.assert_awaited_once()
        self.assertEqual(
            cc.PatchItem.call_args.kwargs["options"]["filterPredicate"],
            "from root where root.number = 3",
        )

    def test_async_version_guard_falls_back_to_legacy(self):
        """An ``etag`` / ``match_condition`` patch never reaches the backend
        (the driver owns ``If-Match`` for its loop and rejects a caller
        precondition); ``execute`` is not awaited and the call falls through
        to the legacy ``PatchItem``, which honours the guard."""
        cc = _connection_with_cache()
        backend = _async_dispatch_backend(
            BackendResponse(status_code=200, sub_status=0, headers=None, body=b"{}")
        )

        async def _run():
            await AsyncItemHelper(backend, cc).patch_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/patch_item",
                item_id="patch_item",
                patch_operations=_OPERATIONS,
                etag="abc",
                match_condition=MatchConditions.IfNotModified,
                request_options={"partitionKey": "a"},
            )

        asyncio.run(_run())
        backend.execute_mock.assert_not_awaited()
        cc.PatchItem.assert_awaited_once()
        self.assertEqual(
            cc.PatchItem.call_args.kwargs["options"]["accessCondition"],
            {"type": "IfMatch", "condition": "abc"},
        )

    def test_async_cache_miss_awaits_refresh_and_stamps_rid(self):
        """Async cache miss: ``_refresh_container_properties_cache`` is
        awaited and the refreshed rid is stamped into the options."""
        cc = MagicMock()
        cache = {}

        async def refresh(link):
            cache[link] = {"_rid": "rid-after-async-refresh"}

        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = AsyncMock(side_effect=refresh)
        cc.PatchItem = AsyncMock(return_value="ok")

        async def _run():
            await AsyncItemHelper(None, cc).patch_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/x",
                item_id="x",
                patch_operations=_OPERATIONS,
                request_options={"partitionKey": "a"},
            )

        asyncio.run(_run())
        cc._refresh_container_properties_cache.assert_awaited_once_with("dbs/db/colls/c")
        options = cc.PatchItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-async-refresh")


if __name__ == "__main__":
    unittest.main()

