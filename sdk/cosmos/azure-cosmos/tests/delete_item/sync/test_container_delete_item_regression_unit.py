# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the sync delete path (no network).

A real container is wired to a fake connection so each test can see what
the delete sends on. They check two things:

1. When no Rust backend is set, the delete goes to the existing client
   with the right document, partition key, etag guard, and options -- and
   any options the caller passed are kept, not thrown away.
2. When a Rust backend is set, the delete goes to it and the existing
   client is not called.
"""
import unittest
from unittest.mock import MagicMock, patch

from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse, CosmosBackend, OP_DELETE_ITEM
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.container import ContainerProxy


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Build a real container over a fake connection.

    The container's own methods stay real -- that is what these tests
    exercise. Only the connection is faked, so a test can see what the
    delete forwarded and what reached the cache refresh.
    """
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # the container also reads the cache under this name

    # No Rust backend, so the delete goes to the existing client.
    cc._backend = None
    cc.DeleteItem = MagicMock(return_value=None)

    proxy = ContainerProxy(cc, "dbs/db", "c")

    def _fake_read(**kwargs):
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerDeleteItemPreservesLegacyBehaviour(unittest.TestCase):
    """When no Rust backend is set, the delete still behaves exactly as before."""

    def test_string_item_resolves_to_document_link(self):
        """A delete by id string targets that document."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.delete_item("delete_item", "a")

        cc.DeleteItem.assert_called_once()
        self.assertEqual(
            cc.DeleteItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/delete_item",
        )

    def test_dict_item_resolves_to_its_self_link(self):
        """A delete by item dict targets the document the dict points to."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        item = {"id": "delete_item", "pk": "a", "_self": "dbs/db/colls/c/docs/rid-abc"}

        proxy.delete_item(item, "a")

        self.assertEqual(
            cc.DeleteItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/rid-abc",
        )

    def test_partition_key_becomes_partition_key_option(self):
        """The partition key passed in is forwarded in the options."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.delete_item("delete_item", "a")

        self.assertEqual(cc.DeleteItem.call_args.kwargs["options"]["partitionKey"], "a")

    def test_caller_request_options_are_merged_not_overwritten(self):
        """Options the caller passes are kept alongside the partition key,
        not thrown away. This guards against the bug where the container
        replaced the caller's options instead of adding to them."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.delete_item(
            "delete_item", "a",
            request_options={"customKey": "customValue"},
        )

        forwarded_options = cc.DeleteItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["customKey"], "customValue")
        self.assertEqual(forwarded_options["partitionKey"], "a")

    def test_cache_hit_path_stamps_rid_into_options(self):
        """When the container is already cached, its resource id is added
        to the options."""
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.delete_item("delete_item", "a")

        self.assertEqual(
            cc.DeleteItem.call_args.kwargs["options"][Constants.ContainerRID], "rid-hot"
        )

    def test_etag_if_not_modified_becomes_access_condition(self):
        """An etag with "if not modified" becomes an if-match condition in
        the options (a delete only if the version still matches)."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.delete_item(
            "delete_item", "a",
            etag="abc", match_condition=MatchConditions.IfNotModified,
        )

        self.assertEqual(
            cc.DeleteItem.call_args.kwargs["options"]["accessCondition"],
            {"type": "IfMatch", "condition": "abc"},
        )

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        """When the container is not cached, options like excluded locations
        are passed through to the cache fetch."""
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.delete_item("delete_item", "a", excluded_locations=["West US"])

        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get("excluded_locations"), ["West US"])
        self.assertIn("dbs/db/colls/c", cache)

    def test_cache_populate_step_takes_container_cache_lock(self):
        """Filling the cache happens under the container's lock so two calls
        don't both refresh at once."""
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)
        lock_use_recorder = MagicMock(wraps=proxy.container_cache_lock)
        with patch.object(proxy, "container_cache_lock", lock_use_recorder):
            proxy.delete_item("delete_item", "a")
        lock_use_recorder.__enter__.assert_called()


class _CapturingBackend(CosmosBackend):
    """A fake backend that records the request it was given."""

    name = "rust"

    def __init__(self):
        self.executed = False
        self.prepared = None

    def execute(self, prepared):
        self.executed = True
        self.prepared = prepared
        return BackendResponse(
            status_code=204,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v1"}),
            body=b"",
        )


class TestContainerDeleteItemBackendRouting(unittest.TestCase):
    """When a Rust backend is set, it handles the delete and the existing
    client is not used."""

    def test_delete_routes_to_backend_with_item_id(self):
        """A delete goes to the Rust backend with the document id; the
        existing client is not called and the call returns nothing."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        backend = _CapturingBackend()
        cc._backend = backend

        result = proxy.delete_item("delete_item", "a")

        self.assertTrue(backend.executed)
        cc.DeleteItem.assert_not_called()
        self.assertEqual(backend.prepared.op, OP_DELETE_ITEM)
        self.assertEqual(backend.prepared.item_id, "delete_item")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

