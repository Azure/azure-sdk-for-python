# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Regression tests for the ``Container.upsert_item`` slim-down.

``Container.upsert_item`` used to build the request options, populate
the container-properties cache, stamp the container rid, and call
``client_connection.UpsertItem`` all in one method body. The migration
moved the last three steps into ``ItemHelper`` (the same path
``create_item`` / ``read_item`` / ``delete_item`` already use) so both
backends share the prep code.

These tests pin the **core-python fall-through path**: with no rust
backend wired (``_backend = None``), the helper builds the
options, stamps the rid, and calls ``client_connection.UpsertItem`` --
exactly the path the default (v4) client takes. The rust backend now
has its own ``upsert_item`` entry point; that dispatch path is covered
separately by ``test_backend_dispatches_upsert_unit.py``. What this
file pins:

* the cache-hit rid still reaches the options dict (drop-and-recreate
  guard),
* ``disableAutomaticIdGeneration`` is always set (an upsert never mints
  an id),
* ``etag`` / ``match_condition`` still become the ``accessCondition``
  the legacy ``UpsertItem`` honours (insert-only / version-guarded
  replace) -- the create-vs-upsert difference,
* the body is forwarded unchanged (no id minting),
* per-call options (``excluded_locations`` / ``timeout``) still reach
  the cache-refresh read, under the proxy's ``container_cache_lock``.

All tests use a mocked ``client_connection`` plus a fake cache. No
network, no emulator, runs in milliseconds. Sibling of
``test_container_create_item_regression_unit.py``.
"""
import unittest
from unittest.mock import MagicMock, patch

from azure.core import MatchConditions

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.container import ContainerProxy


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Build a real ``ContainerProxy`` wired to a mocked ``client_connection``.

    The proxy's own ``container_cache_lock`` and
    ``_get_properties_with_options`` stay real -- that's what these
    tests check. Only the underlying connection is mocked, so the test
    can observe what was forwarded into ``UpsertItem`` and what kwargs
    reached the cache-refresh ``read``.
    """
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # legacy alias used by the proxy

    # No rust backend wired -- absence of ``_backend`` makes the
    # dispatch fall through to ``client_connection.UpsertItem``.
    cc._backend = None
    cc.UpsertItem = MagicMock(return_value={"id": "x", "_rid": rid})

    proxy = ContainerProxy(cc, "dbs/db", "c")

    def _fake_read(**kwargs):
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerUpsertItemPreservesLegacyBehaviour(unittest.TestCase):
    """The fall-through path must stay byte-for-byte the legacy upsert."""

    def test_cache_hit_path_stamps_rid_into_options(self):
        """Cache hit: the cached ``_rid`` ends up in the options dict sent to ``UpsertItem``."""
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.upsert_item({"id": "x", "pk": "a"})

        cc.UpsertItem.assert_called_once()
        forwarded_options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options[Constants.ContainerRID], "rid-hot")

    def test_fall_through_forwards_body_and_link_unchanged(self):
        """The document and container link reach ``UpsertItem`` exactly as
        the customer passed them -- an upsert never rewrites the body."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        body = {"id": "order-42", "pk": "customerA", "total": 109.5}

        proxy.upsert_item(body)

        call = cc.UpsertItem.call_args
        self.assertEqual(call.kwargs["database_or_container_link"], "dbs/db/colls/c")
        self.assertEqual(call.kwargs["document"], body)
        self.assertNotIn("id_minted", body)  # body object untouched

    def test_options_always_disable_id_generation(self):
        """Every upsert sets ``disableAutomaticIdGeneration`` -- the legacy
        flag that stops the connection minting an id."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.upsert_item({"id": "x", "pk": "a"})

        forwarded_options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertIs(forwarded_options["disableAutomaticIdGeneration"], True)

    def test_if_missing_becomes_insert_only_access_condition(self):
        """``match_condition=IfMissing`` (the insert-only idiom) still
        becomes the ``accessCondition`` the legacy ``UpsertItem``
        honours -- the upsert-meaningful precondition that create drops."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.upsert_item({"id": "x", "pk": "a"}, match_condition=MatchConditions.IfMissing)

        forwarded_options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertEqual(
            forwarded_options["accessCondition"],
            {"type": "IfNoneMatch", "condition": "*"},
        )

    def test_etag_if_not_modified_becomes_guarded_replace_access_condition(self):
        """``etag`` + ``IfNotModified`` (version-guarded replace) becomes
        the ``If-Match`` access condition on the legacy path."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.upsert_item(
            {"id": "x", "pk": "a"},
            etag="abc",
            match_condition=MatchConditions.IfNotModified,
        )

        forwarded_options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertEqual(
            forwarded_options["accessCondition"],
            {"type": "IfMatch", "condition": "abc"},
        )

    def test_populate_query_metrics_warns_and_is_forwarded(self):
        """The deprecated sync-only ``populate_query_metrics`` still warns
        and still reaches the legacy options, exactly as before."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        with self.assertWarns(DeprecationWarning):
            proxy.upsert_item({"id": "x", "pk": "a"}, populate_query_metrics=True)

        forwarded_options = cc.UpsertItem.call_args.kwargs["options"]
        self.assertIs(forwarded_options["populateQueryMetrics"], True)

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        """Cache miss: ``excluded_locations`` from the call reaches the
        cache-refresh ``read`` (same contract create has)."""
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.upsert_item({"id": "x", "pk": "a"}, excluded_locations=["West US"])

        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get("excluded_locations"), ["West US"])
        self.assertIn("dbs/db/colls/c", cache)

    def test_cache_miss_forwards_timeout_kwargs_into_cache_fetch(self):
        """Cache miss: ``timeout`` / ``read_timeout`` reach the cache-refresh read."""
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)

        proxy.upsert_item({"id": "x", "pk": "a"}, timeout=10, read_timeout=5)

        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get(Constants.Kwargs.TIMEOUT), 10)
        self.assertEqual(read_kwargs.get(Constants.Kwargs.READ_TIMEOUT), 5)

    def test_cache_populate_step_takes_container_cache_lock(self):
        """Cache populate runs under ``container_cache_lock`` (thread-safety)."""
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)
        lock_use_recorder = MagicMock(wraps=proxy.container_cache_lock)
        with patch.object(proxy, "container_cache_lock", lock_use_recorder):
            proxy.upsert_item({"id": "x", "pk": "a"})
        lock_use_recorder.__enter__.assert_called()


if __name__ == "__main__":
    unittest.main()

