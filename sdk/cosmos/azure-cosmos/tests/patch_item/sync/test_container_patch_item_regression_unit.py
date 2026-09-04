# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the sync patch path (no network).

A real container is wired to a fake connection so each test can see what
the patch sends on. They check two things:

1. When no Rust backend is set, the patch goes to the existing client with
   the right document, the operations unchanged, the filter, the partition
   key, and the options.
2. Routing: a plain patch goes to the Rust backend, but a patch with a
   filter or a version guard goes to the existing client instead (the only
   path that can apply them).
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import CosmosBackend
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_PATCH_ITEM
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.container import ContainerProxy
from azure.cosmos._backend.legacy import LEGACY_BACKEND


_OPERATIONS = [
    {"op": "add", "path": "/color", "value": "yellow"},
    {"op": "incr", "path": "/number", "value": 7},
]


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Build a real container over a fake connection.

    The container's own methods stay real -- that is what these tests
    exercise. Only the connection is faked, so a test can see what the
    patch forwarded and what reached the cache refresh.
    """
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # the container also reads the cache under this name

    # No Rust backend, so the patch goes to the existing client.
    cc._backend = LEGACY_BACKEND
    cc.PatchItem = MagicMock(return_value={"id": "patch_item", "_rid": rid})

    proxy = ContainerProxy(cc, "dbs/db", "c")

    def _fake_read(**kwargs):
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerPatchItemPreservesLegacyBehaviour(unittest.TestCase):
    """When no Rust backend is set, the patch still behaves exactly as before."""

    def test_string_item_resolves_to_document_link(self):
        """A patch by id string targets that document."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.patch_item("patch_item", "a", _OPERATIONS)

        cc.PatchItem.assert_called_once()
        self.assertEqual(
            cc.PatchItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/patch_item",
        )

    def test_dict_item_resolves_to_its_self_link(self):
        """A patch by item dict targets the document the dict points to."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        item = {"id": "patch_item", "pk": "a", "_self": "dbs/db/colls/c/docs/rid-abc"}

        proxy.patch_item(item, "a", _OPERATIONS)

        self.assertEqual(
            cc.PatchItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/rid-abc",
        )

    def test_fall_through_forwards_operations_unchanged(self):
        """The list of patch operations reaches the existing client
        unchanged."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.patch_item("patch_item", "a", _OPERATIONS)

        self.assertEqual(cc.PatchItem.call_args.kwargs["operations"], _OPERATIONS)

    def test_filter_predicate_becomes_filter_predicate_option(self):
        """A filter is forwarded in the options for the server to apply."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            filter_predicate="from root where root.number = 3",
        )

        forwarded_options = cc.PatchItem.call_args.kwargs["options"]
        self.assertEqual(
            forwarded_options["filterPredicate"], "from root where root.number = 3"
        )

    def test_cache_hit_path_stamps_rid_into_options(self):
        """When the container is already cached, its resource id is added
        to the options."""
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.patch_item("patch_item", "a", _OPERATIONS)

        forwarded_options = cc.PatchItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options[Constants.ContainerRID], "rid-hot")

    def test_caller_request_options_are_merged_not_overwritten(self):
        """Options the caller passes are kept alongside the partition key,
        not thrown away. This guards against the bug where the container
        replaced the caller's options instead of adding to them."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            request_options={"customKey": "customValue"},
        )

        forwarded_options = cc.PatchItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["customKey"], "customValue")
        self.assertEqual(forwarded_options["partitionKey"], "a")

    def test_options_always_disable_id_generation(self):
        """A patch never generates a new id, so id generation is always
        turned off."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.patch_item("patch_item", "a", _OPERATIONS)

        forwarded_options = cc.PatchItem.call_args.kwargs["options"]
        self.assertIs(forwarded_options["disableAutomaticIdGeneration"], True)

    def test_etag_if_not_modified_becomes_access_condition(self):
        """An etag with "if not modified" becomes an if-match condition in
        the options (a patch only if the version still matches)."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            etag="abc", match_condition=MatchConditions.IfNotModified,
        )

        forwarded_options = cc.PatchItem.call_args.kwargs["options"]
        self.assertEqual(
            forwarded_options["accessCondition"],
            {"type": "IfMatch", "condition": "abc"},
        )

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        """When the container is not cached, options like excluded locations
        are passed through to the cache fetch."""
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.patch_item(
            "patch_item", "a", _OPERATIONS, excluded_locations=["West US"]
        )

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
            proxy.patch_item("patch_item", "a", _OPERATIONS)
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
            headers=CaseInsensitiveDict({"etag": "v2"}),
            body=b'{"id":"patch_item","number":10}',
        )


class TestContainerPatchItemBackendRouting(unittest.TestCase):
    """The routing decision specific to patch: when the Rust backend is used
    and when the existing client is used instead."""

    def test_plain_patch_routes_to_backend_with_item_id_and_operations_body(self):
        """A plain patch goes to the Rust backend with the document id and
        the operations as its body; the existing client is not called.

        The operations are sent with the driver's wording, so ``incr``
        becomes ``increment``.
        """
        proxy, cc, _ = _make_proxy_with_mock_connection()
        backend = _CapturingBackend()
        cc._backend = backend

        proxy.patch_item("patch_item", "a", _OPERATIONS)

        self.assertTrue(backend.executed)
        cc.PatchItem.assert_not_called()
        prepared = backend.prepared
        self.assertEqual(prepared.op, OP_PATCH_ITEM)
        self.assertEqual(prepared.item_id, "patch_item")
        # The body holds the operations, with ``incr`` renamed to ``increment``.
        body = json.loads(prepared.body_bytes)
        self.assertEqual(
            body,
            {"operations": [
                {"op": "add", "path": "/color", "value": "yellow"},
                {"op": "increment", "path": "/number", "value": 7},
            ]},
        )

    def test_filter_predicate_patch_falls_back_to_legacy(self):
        """A patch with a filter does not go to the Rust backend (which
        can't apply it). It goes to the existing client, which can."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        backend = _CapturingBackend()
        cc._backend = backend

        proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            filter_predicate="from root where root.number = 3",
        )

        self.assertFalse(backend.executed)
        cc.PatchItem.assert_called_once()
        self.assertEqual(
            cc.PatchItem.call_args.kwargs["options"]["filterPredicate"],
            "from root where root.number = 3",
        )

    def test_version_guarded_patch_falls_back_to_legacy(self):
        """A patch with a version guard (etag) does not go to the Rust
        backend. It goes to the existing client, which applies the guard."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        backend = _CapturingBackend()
        cc._backend = backend

        proxy.patch_item(
            "patch_item", "a", _OPERATIONS,
            etag="abc", match_condition=MatchConditions.IfNotModified,
        )

        self.assertFalse(backend.executed)
        cc.PatchItem.assert_called_once()
        self.assertEqual(
            cc.PatchItem.call_args.kwargs["options"]["accessCondition"],
            {"type": "IfMatch", "condition": "abc"},
        )


if __name__ == "__main__":
    unittest.main()
