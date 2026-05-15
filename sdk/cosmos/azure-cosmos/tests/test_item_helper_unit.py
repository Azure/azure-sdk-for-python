# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``ItemHelper`` and ``AsyncItemHelper`` — no network, no Cosmos emulator.

Backend *selection* (rust vs core-python) is the responsibility of
``pick_backend(client_connection)`` in ``_helpers/_item_dispatch.py``
and is covered end-to-end by ``tests/test_backend_wiring_unit.py``.
This module covers the helper class itself in isolation:

* The helper stamps the chosen backend's name into ``kwargs`` so the
  user-agent policy can append ``backend=<name>`` to the wire.
* The helper hands a real ``PreparedRequest`` to the backend's
  ``execute`` (it does *not* call the binding directly).
* When the backend signals fall-through (returns ``None``, the
  CorePythonBackend placeholder contract), the helper runs the legacy
  ``CreateItem`` path with the legacy-shape options dict —
  ``disableAutomaticIdGeneration``, ``indexingDirective``,
  ``Constants.ContainerRID`` all stamped correctly.
* When the backend returns a real ``BackendResponse`` (the wired
  RustBackend path), the helper hands it to ``parse_backend_response``
  and surfaces a ``CosmosDict``. The legacy ``CreateItem`` is *not*
  called in that case.
* Container-rid lookup reads the cache, triggers
  ``_refresh_container_properties_cache`` on miss, and tolerates a
  bare-mock connection where the cache lookup can't produce a real rid.
* The async sibling does the same with ``await`` in the right places.
"""
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._backend.constants import REQUEST_OPTION_BACKEND_KEY
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_cc_with_cache_hit(rid="rid-cached"):
    """Build a MagicMock client_connection with the rid pre-cached.

    Avoids the ``_refresh_container_properties_cache`` branch in the
    helper, so each test can stay focused on the bit it cares about.
    The connection's ``_AddPartitionKey`` is wired to return the
    options dict unchanged with a stub partition key — enough for the
    helper to build a ``PreparedRequest`` without exploding.
    """
    cc = MagicMock()
    cc._container_properties_cache = {"dbs/db/colls/c": {"_rid": rid}}

    def _add_pk(_link, _doc, options):
        new_options = dict(options)
        new_options.setdefault("partitionKey", "stub-pk")
        return new_options
    cc._AddPartitionKey = MagicMock(side_effect=_add_pk)
    return cc


def _fall_through_backend(name):
    """Build a backend mock whose ``execute`` returns ``None``.

    ``None`` is the documented "fall through to legacy ``CreateItem``"
    contract that ``CorePythonBackend`` actually implements. Tests that
    want to assert what the helper forwards to ``CreateItem`` use this
    so the helper's parse-side branch doesn't run on a junk
    ``BackendResponse``.
    """
    backend = MagicMock()
    backend.name = name
    backend.execute = MagicMock(return_value=None)
    return backend


def _async_fall_through_backend(name):
    """Async sibling of ``_fall_through_backend``."""
    backend = MagicMock()
    backend.name = name
    backend.execute = AsyncMock(return_value=None)
    return backend


# ---------------------------------------------------------------------------
# Sync helper — fall-through (CorePythonBackend placeholder) path
# ---------------------------------------------------------------------------

class TestItemHelperFallThrough(unittest.TestCase):
    """Helper drives the legacy ``CreateItem`` when the backend returns ``None``."""

    def test_user_agent_stamp_lands_in_kwargs(self):
        """The chosen backend's name must reach ``CreateItem`` under
        ``REQUEST_OPTION_BACKEND_KEY`` so the user-agent policy can
        append ``backend=<name>`` to the wire."""
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        cc.CreateItem.assert_called_once()
        forwarded = cc.CreateItem.call_args.kwargs
        self.assertEqual(forwarded[REQUEST_OPTION_BACKEND_KEY], "core-python")

    def test_backend_execute_offered_a_prepared_request(self):
        """Even on the fall-through path the helper hands the backend a
        real ``PreparedRequest`` — that's the contract that lets a wired
        adapter slot in without changing the call site."""
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")
        backend = _fall_through_backend("core-python")

        ItemHelper(backend, cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        backend.execute.assert_called_once()
        prepared = backend.execute.call_args.args[0]
        # PreparedRequest carries the op tag and the link.
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(prepared.container_link, "dbs/db/colls/c")
        self.assertEqual(prepared.body_bytes, b'{"id":"x"}')

    def test_disable_automatic_id_generation_lands_in_options(self):
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            enable_automatic_id_generation=False,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertTrue(options["disableAutomaticIdGeneration"])

    def test_enable_automatic_id_generation_inverts_disable_flag(self):
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            enable_automatic_id_generation=True,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertFalse(options["disableAutomaticIdGeneration"])

    def test_indexing_directive_lands_when_supplied(self):
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            indexing_directive=1,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options["indexingDirective"], 1)

    def test_container_rid_stamped_from_cache(self):
        cc = _make_cc_with_cache_hit(rid="rid-from-cache")
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-from-cache")

    def test_cache_miss_triggers_refresh(self):
        cc = MagicMock()
        cache = {}

        def refresh(link):
            cache[link] = {"_rid": "rid-after-refresh"}

        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = MagicMock(side_effect=refresh)
        cc._AddPartitionKey = MagicMock(
            side_effect=lambda _l, _d, opts: dict(opts, partitionKey="stub-pk")
        )
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )
        cc._refresh_container_properties_cache.assert_called_once_with("dbs/db/colls/c")
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-after-refresh")


# ---------------------------------------------------------------------------
# Sync helper — wired-backend path (real BackendResponse from execute)
# ---------------------------------------------------------------------------

class TestItemHelperWiredBackend(unittest.TestCase):
    """When ``backend.execute`` returns a real ``BackendResponse``, the
    helper parses it instead of running the legacy ``CreateItem``."""

    def test_real_backend_response_parsed_into_cosmos_dict(self):
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(side_effect=AssertionError("legacy must not run"))

        backend = MagicMock()
        backend.name = "rust"
        backend.execute = MagicMock(return_value=BackendResponse(
            status_code=201,
            sub_status=0,
            headers=None,
            body=b'{"id":"x","_etag":"\\"v1\\""}',
            diagnostics=None,
        ))

        result = ItemHelper(backend, cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        backend.execute.assert_called_once()
        cc.CreateItem.assert_not_called()
        # CosmosDict subclasses dict — key lookup works the v4 way.
        self.assertEqual(result["id"], "x")
        self.assertEqual(result["_etag"], '"v1"')


# ---------------------------------------------------------------------------
# Async sibling
# ---------------------------------------------------------------------------

class TestAsyncItemHelper(unittest.TestCase):

    def test_async_dispatch_falls_through_to_create_item(self):
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

