# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fast, in-process tests for the sync create helper (no network, no emulator).

The create helper sits between the public create call and the backend. On
each call it finds the container's resource id, builds the request, and
then drives it through the configured backend: the real (or a Rust-shaped
test) backend builds+sends+parses a prepared request, while the explicit
``LegacyBackend`` runs the existing client.
These tests check each of those steps on its own.

The async version is covered in
``tests/create_item/aio/test_item_helper_async_unit.py``. Which backend a
client uses is covered in ``tests/common/test_backend_wiring_unit.py``.
"""
from common.request_preparation import call_create_item_helper
from common.typed_requests import legacy_partition_key_from_request
import logging
import unittest
from unittest.mock import MagicMock

from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.contracts import ContainerMetadata
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._item_operations import ItemHelper
from azure.cosmos._helpers._legacy_item_operations import LegacyItemHelper
from azure.cosmos._backend.errors import BindingProtocolError


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


def _capturing_backend(response):
    """Build a real ``CosmosBackend`` that captures the prepared request it
    receives and returns ``response`` from ``execute``.

    Inheriting from ``CosmosBackend`` (rather than a bare ``MagicMock``) means
    ``run_operation`` is the genuine default implementation -- build the
    request, call ``execute``, parse the reply -- so these tests exercise the
    real dispatch template, not a mocked stand-in for it.
    """
    class _CapturingBackend(CosmosBackend):
        name = "rust"

        def __init__(self) -> None:
            self.prepared = None

        def get_container_metadata(self, link):
            return ContainerMetadata("rid-cached")

        def execute(self, prepared, *, deadline=None):
            self.prepared = prepared
            return response

    return _CapturingBackend()


# ---------------------------------------------------------------------------
# When no backend handles the call, the helper uses the existing client
# ---------------------------------------------------------------------------

class TestItemHelperFallThrough(unittest.TestCase):
    """When no Rust backend is set, the helper calls the
    existing client via the explicit ``LegacyBackend``.

    These tests check the call the helper makes: the id-generation and
    indexing options, and the container resource id (both when it is
    already cached and when it has to be refreshed). The request the
    helper builds *for a backend* is checked separately in
    ``test_backend_execute_offered_a_prepared_request`` below, which uses a
    real (non-``None``) backend.
    """

    def test_disable_automatic_id_generation_lands_in_options(self):
        """Turning off automatic id generation sets the matching option."""
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(return_value="ok")

        call_create_item_helper(LegacyItemHelper(cc),
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

        call_create_item_helper(LegacyItemHelper(cc),
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

        call_create_item_helper(LegacyItemHelper(cc),
            container_link="dbs/db/colls/c",
            body={"id": "x"},
            indexing_directive=1,
        )
        options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(options["indexingDirective"], 1)

    def test_cached_container_resource_id_is_added_to_options(self):
        """When the container is already cached, its resource id is added
        to the options."""
        cc = _make_cc_with_cache_hit(rid="rid-from-cache")
        cc.CreateItem = MagicMock(return_value="ok")

        call_create_item_helper(LegacyItemHelper(cc),
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

        call_create_item_helper(LegacyItemHelper(cc),
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

    def test_backend_offered_a_well_formed_prepared_request(self):
        """The helper builds a request and offers it to the backend. This
        checks the request carries the right operation, container, and body.
        """
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(side_effect=AssertionError("legacy must not run"))
        backend = _capturing_backend(BackendResponse(
            status_code=201,
            sub_status=0,
            headers=None,
            body=b'{"id":"x"}',
            diagnostics=None,
        ))

        call_create_item_helper(ItemHelper(backend),
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        cc.CreateItem.assert_not_called()
        prepared = backend.prepared
        self.assertIsNotNone(prepared)
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(prepared.container_link, "dbs/db/colls/c")
        self.assertEqual(prepared.body_bytes, b'{"id":"x"}')

    def test_real_backend_response_parsed_into_cosmos_dict(self):
        """A successful backend response is returned to the caller as a
        dict; the existing client is not called."""
        cc = _make_cc_with_cache_hit()
        cc.CreateItem = MagicMock(side_effect=AssertionError("legacy must not run"))

        backend = _capturing_backend(BackendResponse(
            status_code=201,
            sub_status=0,
            headers=None,
            body=b'{"id":"x","_etag":"\\"v1\\""}',
            diagnostics=None,
        ))

        result = call_create_item_helper(ItemHelper(backend),
            container_link="dbs/db/colls/c",
            body={"id": "x"},
        )

        self.assertIsNotNone(backend.prepared)
        cc.CreateItem.assert_not_called()
        # The result is a dict, so the caller reads fields by key.
        self.assertEqual(result["id"], "x")
        self.assertEqual(result["_etag"], '"v1"')


class TestItemHelperMetadataIndependence(unittest.TestCase):
    """Python does not resolve metadata before dispatching an item."""

    def test_item_does_not_call_python_metadata_getter(self):
        backend = _capturing_backend(BackendResponse(201, 0, {}, b'{"id":"x"}'))
        backend.get_container_metadata = MagicMock(side_effect=BindingProtocolError("Missing metadata"))
        result = call_create_item_helper(ItemHelper(backend),container_link="dbs/db/colls/c", body={"id": "x"})
        self.assertEqual(result["id"], "x")
        self.assertIsNone(legacy_partition_key_from_request(backend.prepared))
        backend.get_container_metadata.assert_not_called()


if __name__ == "__main__":
    unittest.main()
