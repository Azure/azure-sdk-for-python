# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fast, in-process tests for the sync create helper (no network, no emulator).

The create helper sits between the public create call and the backend. On
each call it finds the container's resource id, builds the request, and
then either lets the backend handle it or, when no backend is set, calls
the existing client. These tests check each of those steps on its own.

The async version is covered in
``tests/create_item/aio/test_item_helper_async_unit.py``. Which backend a
client uses is covered in ``tests/common/test_backend_wiring_unit.py``.
"""
import logging
import unittest
from unittest.mock import MagicMock

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers.item_helper import ItemHelper


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_cc_with_cache_hit(rid="rid-cached"):
    """Build a fake connection with the container's resource id already cached.

    This skips the cache-refresh step so each test can focus on what it
    checks. The fake also returns a stub partition key so the helper can
    build a request without failing.
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
    """Build a fake backend that does nothing and returns ``None``.

    Returning ``None`` tells the helper to use the existing client
    instead. These tests use it to check what the helper passes to that
    client.
    """
    backend = MagicMock()
    backend.name = name
    backend.execute = MagicMock(return_value=None)
    return backend


# ---------------------------------------------------------------------------
# When no backend handles the call, the helper uses the existing client
# ---------------------------------------------------------------------------

class TestItemHelperFallThrough(unittest.TestCase):
    """When the backend does nothing, the helper calls the existing client.

    These tests check the call the helper makes: the request it builds,
    the id-generation and indexing options, and the container resource id
    (both when it is already cached and when it has to be refreshed).
    """

    def test_backend_execute_offered_a_prepared_request(self):
        """The helper builds a request and offers it to the backend, even
        when the backend does nothing with it. This checks the request
        carries the right operation, container, and body.
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
        """Turning off automatic id generation sets the matching option."""
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
        """Turning on automatic id generation clears the matching option."""
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
        """The indexing directive value is passed through to the options."""
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
        """When the container is already cached, its resource id is added
        to the options."""
        cc = _make_cc_with_cache_hit(rid="rid-from-cache")
        cc.CreateItem = MagicMock(return_value="ok")

        ItemHelper(_fall_through_backend("core-python"), cc).create_item(
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options[Constants.ContainerRID], "rid-from-cache")

    def test_cache_miss_triggers_refresh(self):
        """When the container is not cached, the helper refreshes the cache
        and then uses the freshly fetched resource id."""
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
# When the backend handles the call, the existing client is not used
# ---------------------------------------------------------------------------

class TestItemHelperConfiguredBackend(unittest.TestCase):
    """When the backend handles the call, the existing client is not used.

    The helper turns the backend's response into the dict the caller
    expects and does not call the existing client.
    """

    def test_real_backend_response_parsed_into_cosmos_dict(self):
        """A successful backend response is returned to the caller as a
        dict; the existing client is not called."""
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
        # The result is a dict, so the caller reads fields by key.
        self.assertEqual(result["id"], "x")
        self.assertEqual(result["_etag"], '"v1"')


class TestItemHelperRidResolutionLogging(unittest.TestCase):
    """When the container resource id can't be found, the helper logs it.

    A real connection should always find the id. If it can't, the request
    still goes out, but without the header that guards against a recreated
    container. The helper logs a warning so this is not silent.
    """

    def test_unresolvable_rid_logs_warning_and_returns_none(self):
        """A missing resource id is logged and the helper returns nothing."""
        cc = MagicMock()
        cc._container_properties_cache = {}  # empty: the container is not here
        # The refresh does not add it, so the later lookup fails -- the
        # case a real connection would only hit on a genuine problem.
        cc._refresh_container_properties_cache = MagicMock()

        helper = ItemHelper(None, cc)

        with self.assertLogs(
            "azure.cosmos._helpers.item_helper", level=logging.WARNING
        ) as captured:
            rid = helper._resolve_container_rid("dbs/db/colls/c", {})

        self.assertIsNone(rid)
        self.assertTrue(
            any("intended-collection-rid" in line for line in captured.output),
            captured.output,
        )


if __name__ == "__main__":
    unittest.main()

