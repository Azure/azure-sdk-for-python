 # -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for the synchronous ``ItemHelper.create_item`` — no network, no Cosmos emulator.

What this file covers
---------------------
``ItemHelper`` is the layer that sits between the customer-facing
``Container.create_item`` and the backend that actually talks to
Cosmos. For every call it has to:

1. Look up (or refresh) the container's *rid* from the cache.
2. Build a ``PreparedRequest`` (op tag, container link, body bytes,
   partition-key header, request options).
3. Hand that ``PreparedRequest`` to the wired backend's ``execute``.
4. Either parse the ``BackendResponse`` it gets back into a
   ``CosmosDict``, **or** — if the backend signals "I did nothing"
   by returning ``None`` — fall through to the legacy
   ``client_connection.CreateItem`` path with the right option-dict
   shape (``disableAutomaticIdGeneration``, ``indexingDirective``,
   ``Constants.ContainerRID``, …).

These tests cover every one of those steps in isolation. Backend
*selection* itself (rust vs core-python) is covered end-to-end by
``tests/common/test_backend_wiring_unit.py``; this file does not
duplicate that.

The async sibling (``AsyncItemHelper.create_item``) lives in
``tests/create_item/aio/test_item_helper_async_unit.py``.
"""
import unittest
from unittest.mock import MagicMock

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers.item_helper import ItemHelper


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_cc_with_cache_hit(rid="rid-cached"):
    """Build a mock ``client_connection`` with the container's rid pre-cached.

    Avoids the ``_refresh_container_properties_cache`` branch in the
    helper, so each test can stay focused on whatever it cares about.
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

    ``None`` is the "fall through to legacy ``CreateItem``" contract
    the helper honors when a backend's ``execute`` produces nothing.
    Today no production backend uses this — the "core-python"
    selection is encoded as ``self._backend is None`` — but the
    contract is useful in tests that want to assert what the helper
    forwards to ``CreateItem`` without the helper's parse-side branch
    running on a junk ``BackendResponse``.
    """
    backend = MagicMock()
    backend.name = name
    backend.execute = MagicMock(return_value=None)
    return backend


# ---------------------------------------------------------------------------
# Sync helper — fall-through path (backend.execute returns None)
# ---------------------------------------------------------------------------

class TestItemHelperFallThrough(unittest.TestCase):
    """When ``backend.execute`` returns ``None`` the helper runs the legacy ``CreateItem``.

    These tests cover the exact shape of the call the helper makes
    into ``client_connection.CreateItem`` on the fall-through path:
    prepared-request handoff to the backend, the
    three option mappings (``disableAutomaticIdGeneration``,
    ``indexingDirective``), container-rid stamping (cache hit and
    cache miss).
    """

    def test_backend_execute_offered_a_prepared_request(self):
        """Even on the fall-through path the helper hands the backend a real ``PreparedRequest``.

        That's the contract that lets a wired adapter slot in without
        changing the call site: the helper always builds and offers
        the prepared request, regardless of whether the backend
        chooses to act on it.
        """
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")
        backend = _fall_through_backend("core-python")

        ItemHelper(backend, cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        backend.execute.assert_called_once()
        prepared = backend.execute.call_args.args[0]
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(prepared.container_link, "dbs/db/colls/c")
        self.assertEqual(prepared.body_bytes, b'{"id":"x"}')

    def test_disable_automatic_id_generation_lands_in_options(self):
        """``enable_automatic_id_generation=False`` → ``options["disableAutomaticIdGeneration"]`` is True."""
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
        """``enable_automatic_id_generation=True`` → ``options["disableAutomaticIdGeneration"]`` is False."""
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
        """``indexing_directive=N`` → ``options["indexingDirective"] == N``."""
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
        """Cache hit: the cached ``_rid`` is stamped under ``Constants.ContainerRID`` in the options."""
        cc = _make_cc_with_cache_hit(rid="rid-from-cache")
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-from-cache")

    def test_cache_miss_triggers_refresh(self):
        """Cache miss: the helper calls ``_refresh_container_properties_cache`` and stamps the refreshed rid."""
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

class TestItemHelperConfiguredBackend(unittest.TestCase):
    """When ``backend.execute`` returns a real ``BackendResponse`` the legacy path is bypassed.

    The helper hands the response to ``parse_backend_response`` and
    surfaces a ``CosmosDict``. ``client_connection.CreateItem`` must
    not be called — this is the production-path contract for the
    Rust backend.
    """

    def test_real_backend_response_parsed_into_cosmos_dict(self):
        """A 201 ``BackendResponse`` from the backend → ``CosmosDict`` to the customer; legacy ``CreateItem`` is not invoked."""
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


if __name__ == "__main__":
    unittest.main()

