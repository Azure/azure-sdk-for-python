# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``ItemHelper`` and ``AsyncItemHelper`` — no network, no Cosmos emulator.

The slim-down moved the
``Container.create_item`` body into ``ItemHelper.create_item``. The
backend dispatch tests in ``tests/test_backend_wiring_unit.py``
already cover the dispatch contract end-to-end through the container
proxy. This module covers the helper class itself in isolation:

* The helper actually consumes the backend attributes on the connection.
* The helper actually writes the request-options keys the legacy
  pipeline expects (``disableAutomaticIdGeneration``, ``indexingDirective``).
* The helper actually reads the container-properties cache off
  ``client_connection`` and triggers ``_refresh_container_properties_cache``
  on a miss.
* The helper actually forwards every kwarg to ``CreateItem``.
* The async sibling does the same with ``await`` in the right places.
"""
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from azure.cosmos._backend.constants import REQUEST_OPTION_BACKEND_KEY
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


def _make_cc_with_cache_hit(rid="rid-cached"):
    """Build a MagicMock client_connection that already has the rid in cache.

    Avoids the ``_refresh_container_properties_cache`` branch in the
    helper, so the test stays focused on the dispatch + options-build
    path.
    """
    cc = MagicMock()
    # The helper does ``container_link in cache`` — a real dict lets
    # that decision come out the way the test wants.
    cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": rid}}
    return cc


class TestItemHelperDispatchAndForwarding(unittest.TestCase):
    """Sync helper: dispatch + CreateItem invocation."""

    def test_dispatch_picks_core_python_when_no_rust_backend(self):
        cc = _make_cc_with_cache_hit()
        cc._rust_backend = None
        core_python = MagicMock()
        core_python.name = "core-python"
        core_python.create_item = MagicMock(return_value=None)
        cc._core_python_backend = core_python
        cc.CreateItem = MagicMock(return_value="result-sentinel")

        result = ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        # Backend was offered the call (so the UA suffix branch ran).
        core_python.create_item.assert_called_once_with(prepared=None)
        # Then we fell through to legacy CreateItem with the kwargs
        # carrying the cosmos_backend stamp.
        cc.CreateItem.assert_called_once()
        forwarded_kwargs = cc.CreateItem.call_args.kwargs
        self.assertEqual(forwarded_kwargs[REQUEST_OPTION_BACKEND_KEY], "core-python")
        self.assertEqual(result, "result-sentinel")

    def test_dispatch_picks_rust_backend_when_present_and_no_force_kwargs(self):
        cc = _make_cc_with_cache_hit()
        rust = MagicMock()
        rust.name = "rust"
        rust.create_item = MagicMock(side_effect=NotImplementedError("rust stub"))
        cc._rust_backend = rust
        cc._core_python_backend = MagicMock(name="not-used")

        with self.assertRaises(NotImplementedError):
            ItemHelper(cc).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

    def test_availability_strategy_forces_core_python(self):
        cc = _make_cc_with_cache_hit()
        rust = MagicMock(name="rust-backend")
        rust.name = "rust"
        rust.create_item = MagicMock(side_effect=AssertionError("rust must not run"))
        core_python = MagicMock(name="core-python-backend")
        core_python.name = "core-python"
        core_python.create_item = MagicMock(return_value=None)
        cc._rust_backend = rust
        cc._core_python_backend = core_python
        cc.CreateItem = MagicMock(return_value="ok")

        result = ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            availability_strategy={"threshold_ms": 500},
        )

        rust.create_item.assert_not_called()
        core_python.create_item.assert_called_once()
        self.assertEqual(result, "ok")

    def test_retry_write_forces_core_python(self):
        cc = _make_cc_with_cache_hit()
        rust = MagicMock(name="rust-backend")
        rust.name = "rust"
        rust.create_item = MagicMock(side_effect=AssertionError("rust must not run"))
        core_python = MagicMock(name="core-python-backend")
        core_python.name = "core-python"
        core_python.create_item = MagicMock(return_value=None)
        cc._rust_backend = rust
        cc._core_python_backend = core_python
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            **{Constants.Kwargs.RETRY_WRITE: 3},
        )

        rust.create_item.assert_not_called()
        core_python.create_item.assert_called_once()


class TestItemHelperOptionsAndCache(unittest.TestCase):
    """Sync helper: option-key writes + container-rid stamping."""

    def test_disable_automatic_id_generation_lands_in_options(self):
        cc = _make_cc_with_cache_hit()
        cc._rust_backend = None
        cc._core_python_backend = None
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            enable_automatic_id_generation=False,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertTrue(options["disableAutomaticIdGeneration"])

    def test_enable_automatic_id_generation_inverts_disable_flag(self):
        cc = _make_cc_with_cache_hit()
        cc._rust_backend = None
        cc._core_python_backend = None
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            enable_automatic_id_generation=True,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertFalse(options["disableAutomaticIdGeneration"])

    def test_indexing_directive_lands_when_supplied(self):
        cc = _make_cc_with_cache_hit()
        cc._rust_backend = None
        cc._core_python_backend = None
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            indexing_directive=1,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options["indexingDirective"], 1)

    def test_container_rid_stamped_from_cache(self):
        cc = _make_cc_with_cache_hit(rid="rid-from-cache")
        cc._rust_backend = None
        cc._core_python_backend = None
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-from-cache")

    def test_cache_miss_triggers_refresh(self):
        cc = MagicMock()
        # Real dict starts empty -> miss -> refresh callback runs ->
        # we populate the cache from the refresh, then read.
        cache = {}

        def refresh(link):
            cache[link] = {"_rid": "rid-after-refresh"}

        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = MagicMock(side_effect=refresh)
        cc._rust_backend = None
        cc._core_python_backend = None
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )
        cc._refresh_container_properties_cache.assert_called_once_with("dbs/db/colls/c")
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-refresh")


class TestAsyncItemHelper(unittest.TestCase):
    """Async sibling: same shape, ``await`` in the right places."""

    def test_async_dispatch_falls_through_to_create_item(self):
        cc = MagicMock()
        cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": "rid"}}
        cc._rust_backend = None
        core_python = MagicMock()
        core_python.name = "core-python"
        core_python.create_item = AsyncMock(return_value=None)
        cc._core_python_backend = core_python
        cc.CreateItem = AsyncMock(return_value="async-result")

        async def _run():
            return await AsyncItemHelper(cc).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

        result = asyncio.run(_run())
        self.assertEqual(result, "async-result")
        core_python.create_item.assert_awaited_once_with(prepared=None)
        cc.CreateItem.assert_awaited_once()
        self.assertEqual(
            cc.CreateItem.call_args.kwargs[REQUEST_OPTION_BACKEND_KEY],
            "core-python",
        )

    def test_async_cache_miss_awaits_refresh(self):
        cc = MagicMock()
        cache = {}

        async def refresh(link):
            cache[link] = {"_rid": "rid-after-async-refresh"}

        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = AsyncMock(side_effect=refresh)
        cc._rust_backend = None
        cc._core_python_backend = None
        cc.CreateItem = AsyncMock(return_value="ok")

        async def _run():
            await AsyncItemHelper(cc).create_item(
                container_link="dbs/db/colls/c",
                body={"id": "x"},
            )

        asyncio.run(_run())
        cc._refresh_container_properties_cache.assert_awaited_once_with("dbs/db/colls/c")
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-async-refresh")


if __name__ == "__main__":
    unittest.main()
