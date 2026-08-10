# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the sync read path (no network).

A real container is wired to a fake connection so each test can see what
the read sends on. They check two things:

1. When no Rust backend is set, the read goes to the existing client with
   the right document, partition key, and options -- and any options the
   caller passed are kept, not thrown away.
2. When a Rust backend is set, the read goes to it and the existing client
   is not called.
"""
import unittest
from unittest.mock import MagicMock, patch

from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import CosmosBackend
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_READ_ITEM
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.container import ContainerProxy


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Build a real container over a fake connection.

    The container's own methods stay real -- that is what these tests
    exercise. Only the connection is faked, so a test can see what the read
    forwarded and what reached the cache refresh.
    """
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # the container also reads the cache under this name

    # No Rust backend, so the read goes to the existing client.
    cc._backend = None
    cc.ReadItem = MagicMock(return_value={"id": "read_item", "_rid": rid})

    proxy = ContainerProxy(cc, "dbs/db", "c")

    def _fake_read(**kwargs):
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerReadItemPreservesLegacyBehaviour(unittest.TestCase):
    """When no Rust backend is set, the read still behaves exactly as before."""

    def test_string_item_resolves_to_document_link(self):
        """A read by id string targets that document."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.read_item("read_item", "a")

        cc.ReadItem.assert_called_once()
        self.assertEqual(
            cc.ReadItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/read_item",
        )

    def test_dict_item_resolves_to_its_self_link(self):
        """A read by item dict targets the document the dict points to."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        item = {"id": "read_item", "pk": "a", "_self": "dbs/db/colls/c/docs/rid-abc"}

        proxy.read_item(item, "a")

        self.assertEqual(
            cc.ReadItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/rid-abc",
        )

    def test_partition_key_becomes_partition_key_option(self):
        """The partition key passed in is forwarded in the options."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.read_item("read_item", "a")

        self.assertEqual(cc.ReadItem.call_args.kwargs["options"]["partitionKey"], "a")

    def test_caller_request_options_are_merged_not_overwritten(self):
        """Options the caller passes are kept alongside the partition key,
        not thrown away. This guards against the bug where the container
        replaced the caller's options instead of adding to them."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.read_item(
            "read_item", "a",
            request_options={"customKey": "customValue"},
        )

        forwarded_options = cc.ReadItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["customKey"], "customValue")
        self.assertEqual(forwarded_options["partitionKey"], "a")

    def test_cache_hit_path_stamps_rid_into_options(self):
        """When the container is already cached, its resource id is added
        to the options."""
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.read_item("read_item", "a")

        self.assertEqual(
            cc.ReadItem.call_args.kwargs["options"][Constants.ContainerRID], "rid-hot"
        )

    def test_etag_if_none_match_becomes_access_condition(self):
        """An etag with "if modified" becomes an if-none-match condition in
        the options (a conditional read)."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.read_item(
            "read_item", "a",
            etag="abc", match_condition=MatchConditions.IfModified,
        )

        self.assertEqual(
            cc.ReadItem.call_args.kwargs["options"]["accessCondition"],
            {"type": "IfNoneMatch", "condition": "abc"},
        )

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        """When the container is not cached, options like excluded locations
        are passed through to the cache fetch."""
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.read_item("read_item", "a", excluded_locations=["West US"])

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
            proxy.read_item("read_item", "a")
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
            status_code=200,
            sub_status=0,
            headers=CaseInsensitiveDict({"etag": "v1"}),
            body=b'{"id":"read_item","number":5}',
        )


class TestContainerReadItemBackendRouting(unittest.TestCase):
    """When a Rust backend is set, it handles the read and the existing
    client is not used."""

    def test_read_routes_to_backend_with_item_id(self):
        """A read goes to the Rust backend with the document id, and the
        existing client is not called; the backend's result is returned."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        backend = _CapturingBackend()
        cc._backend = backend

        result = proxy.read_item("read_item", "a")

        self.assertTrue(backend.executed)
        cc.ReadItem.assert_not_called()
        self.assertEqual(backend.prepared.op, OP_READ_ITEM)
        self.assertEqual(backend.prepared.item_id, "read_item")
        self.assertEqual(result["id"], "read_item")


if __name__ == "__main__":
    unittest.main()

