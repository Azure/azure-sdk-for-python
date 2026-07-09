# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``AsyncItemHelper.replace_item`` -- no network.

``AsyncItemHelper`` mirrors the synchronous ``ItemHelper`` and shares the
option-build, request-prep, and merge helpers, so the wire-shape
behaviour is already pinned by the sync tests in
``tests/replace_item/sync/``. This file covers the async-specific
touchpoints replace adds:

1. ``ReplaceItem`` is awaited on the fall-through path (the core-python
   path, exercised with a fake backend whose ``execute`` returns ``None``)
   with the ``document_link`` the caller resolved from ``item`` and the
   ``body`` forwarded unchanged.
2. A wired backend's ``BackendResponse`` is parsed into a ``CosmosDict``
   and ``ReplaceItem`` is **not** awaited (the rust dispatch path).
3. ``etag`` / ``match_condition`` still reach the legacy options as the
   ``If-Match`` access condition (the version-guarded replace).
4. Cache miss awaits the refresh and stamps the rid.

Sibling of ``tests/upsert_item/aio/test_item_helper_async_unit.py``.
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


def _async_fall_through_backend():
    """An async backend whose ``execute`` returns ``None`` (the documented
    "caller runs the legacy path" signal -- the core-python / no-backend
    case)."""
    backend = MagicMock()
    backend.name = "core-python"
    backend.execute = AsyncMock(return_value=None)
    return backend


def _async_dispatch_backend(response):
    """An async backend whose ``execute`` returns a real ``BackendResponse``
    (the rust dispatch path -- the helper parses it instead of falling
    through to ``ReplaceItem``)."""
    backend = MagicMock()
    backend.name = "rust"
    backend.execute = AsyncMock(return_value=response)
    return backend


def _connection_with_cache(rid="rid"):
    cc = MagicMock()
    cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": rid}}
    # Write-with-body: the helper awaits the partition key out of the body.
    cc._AddPartitionKey = AsyncMock(
        side_effect=lambda _l, _d, opts: dict(opts, partitionKey="customerA")
    )
    cc.ReplaceItem = AsyncMock(return_value="async-replace-result")
    return cc


class TestAsyncReplaceItem(unittest.TestCase):
    """The async fall-through path is the core-python replace path."""

    def test_async_dispatch_falls_through_to_replace_item(self):
        """Async fall-through awaits ``ReplaceItem`` and returns its value;
        the resolved ``document_link`` and the new ``body`` are forwarded
        unchanged and id generation is disabled (a replace never mints)."""
        cc = _connection_with_cache()
        body = {"id": "order-42", "pk": "customerA", "total": 129.0}

        async def _run():
            return await AsyncItemHelper(_async_fall_through_backend(), cc).replace_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/order-42",
                item_id="order-42",
                body=body,
            )

        result = asyncio.run(_run())
        self.assertEqual(result, "async-replace-result")
        cc.ReplaceItem.assert_awaited_once()
        call = cc.ReplaceItem.call_args
        self.assertEqual(call.kwargs["document_link"], "dbs/db/colls/c/docs/order-42")
        self.assertEqual(call.kwargs["new_document"], body)
        self.assertIs(call.kwargs["options"]["disableAutomaticIdGeneration"], True)

    def test_async_backend_dispatch_parses_response_and_skips_legacy(self):
        """When the backend returns a ``BackendResponse`` (rust path), the
        helper parses it into a ``CosmosDict`` and never awaits the legacy
        ``ReplaceItem``."""
        cc = _connection_with_cache()
        response = BackendResponse(
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v2"}),
            body=b'{"id":"order-42","total":129.0}',
        )

        async def _run():
            return await AsyncItemHelper(_async_dispatch_backend(response), cc).replace_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/order-42",
                item_id="order-42",
                body={"id": "order-42", "pk": "customerA", "total": 129.0},
            )

        result = asyncio.run(_run())
        self.assertEqual(result["id"], "order-42")
        self.assertEqual(result.get_response_headers()["etag"], "v2")
        cc.ReplaceItem.assert_not_awaited()

    def test_async_replace_threads_version_guard_access_condition(self):
        """``etag`` + ``IfNotModified`` (the version-guarded replace) reaches
        the legacy options as the ``If-Match`` access condition on the async
        path too."""
        cc = _connection_with_cache()

        async def _run():
            await AsyncItemHelper(_async_fall_through_backend(), cc).replace_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/order-42",
                item_id="order-42",
                body={"id": "order-42", "pk": "customerA"},
                etag="abc",
                match_condition=MatchConditions.IfNotModified,
            )

        asyncio.run(_run())
        options = cc.ReplaceItem.call_args.kwargs["options"]
        self.assertEqual(options["accessCondition"], {"type": "IfMatch", "condition": "abc"})

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
        cc.ReplaceItem = AsyncMock(return_value="ok")

        async def _run():
            await AsyncItemHelper(_async_fall_through_backend(), cc).replace_item(
                container_link="dbs/db/colls/c",
                document_link="dbs/db/colls/c/docs/x",
                item_id="x",
                body={"id": "x", "pk": "a"},
            )

        asyncio.run(_run())
        cc._refresh_container_properties_cache.assert_awaited_once_with("dbs/db/colls/c")
        options = cc.ReplaceItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-async-refresh")


if __name__ == "__main__":
    unittest.main()

