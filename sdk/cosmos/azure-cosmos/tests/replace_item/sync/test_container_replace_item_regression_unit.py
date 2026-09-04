# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Regression tests for the ``Container.replace_item`` slim-down.

``Container.replace_item`` used to build the request options, populate
the container-properties cache, stamp the container rid, and call
``client_connection.ReplaceItem`` all in one method body. The migration
moved the last three steps into ``ItemHelper`` (the same path
``create_item`` / ``read_item`` / ``delete_item`` / ``upsert_item``
already use) so both backends share the prep code.

These tests pin the **core-python fall-through path**: with no rust
backend wired (``_backend = LEGACY_BACKEND``), the helper builds the options,
stamps the rid, and calls ``client_connection.ReplaceItem`` -- exactly
the path the default (v4) client takes. The rust backend's own
``replace_item`` dispatch is covered separately by
``tests/replace_item/test_backend_dispatches_replace_unit.py``. What this
file pins:

* the ``item`` argument still resolves to the document link the legacy
  ``ReplaceItem`` consumes (bare id string and document-dict shapes),
* the new ``body`` reaches ``ReplaceItem`` unchanged (a replace never
  rewrites the body and never mints an id),
* the cache-hit rid still reaches the options dict (drop-and-recreate
  guard),
* ``disableAutomaticIdGeneration`` is always set,
* ``etag`` / ``match_condition`` still become the ``accessCondition``
  the legacy ``ReplaceItem`` honours (the version-guarded replace),
* the deprecated sync-only ``populate_query_metrics`` still warns and
  reaches the legacy options,
* per-call options (``excluded_locations``) still reach the
  cache-refresh read.

All tests use a mocked ``client_connection`` plus a fake cache. No
network, no emulator, runs in milliseconds. Sibling of
``tests/upsert_item/sync/test_container_upsert_item_regression_unit.py``.
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from azure.core import MatchConditions

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.container import ContainerProxy
from azure.cosmos._backend.legacy import LEGACY_BACKEND


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Build a real ``ContainerProxy`` wired to a mocked ``client_connection``.

    The proxy's own ``container_cache_lock``,
    ``_get_properties_with_options``, and ``_get_document_link`` stay
    real -- that's what these tests check. Only the underlying connection
    is mocked, so the test can observe what was forwarded into
    ``ReplaceItem`` and what kwargs reached the cache-refresh ``read``.
    """
    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # legacy alias used by the proxy

    # No rust backend wired -- absence of ``_backend`` makes the
    # dispatch fall through to ``client_connection.ReplaceItem``.
    cc._backend = LEGACY_BACKEND
    cc.ReplaceItem = MagicMock(return_value={"id": "order-42", "_rid": rid})

    proxy = ContainerProxy(cc, "dbs/db", "c")

    def _fake_read(**kwargs):
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerReplaceItemPreservesLegacyBehaviour(unittest.TestCase):
    """The fall-through path must stay byte-for-byte the legacy replace."""

    def test_string_item_resolves_to_document_link(self):
        """A bare id string ``item`` resolves to ``<container>/docs/<id>`` --
        the document link the legacy ``ReplaceItem`` consumes."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.replace_item("order-42", {"id": "order-42", "pk": "a", "total": 129.0})

        cc.ReplaceItem.assert_called_once()
        self.assertEqual(
            cc.ReplaceItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/order-42",
        )

    def test_dict_item_resolves_to_its_self_link(self):
        """A document-dict ``item`` resolves via its ``_self`` link (the
        convenience shape a customer passes after a read)."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        item = {"id": "order-42", "pk": "a", "_self": "dbs/db/colls/c/docs/rid-abc"}

        proxy.replace_item(item, {"id": "order-42", "pk": "a", "total": 129.0})

        self.assertEqual(
            cc.ReplaceItem.call_args.kwargs["document_link"],
            "dbs/db/colls/c/docs/rid-abc",
        )

    def test_fall_through_forwards_body_unchanged(self):
        """The new ``body`` reaches ``ReplaceItem`` as ``new_document``,
        exactly as the customer passed it -- a replace never rewrites the
        body."""
        proxy, cc, _ = _make_proxy_with_mock_connection()
        body = {"id": "order-42", "pk": "customerA", "total": 129.0}

        proxy.replace_item("order-42", body)

        call = cc.ReplaceItem.call_args
        self.assertEqual(call.kwargs["new_document"], body)
        self.assertNotIn("id_minted", body)  # body object untouched

    def test_cache_hit_path_stamps_rid_into_options(self):
        """Cache hit: the cached ``_rid`` ends up in the options dict sent
        to ``ReplaceItem`` (the drop-and-recreate guard)."""
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.replace_item("order-42", {"id": "order-42", "pk": "a"})

        forwarded_options = cc.ReplaceItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options[Constants.ContainerRID], "rid-hot")

    def test_options_always_disable_id_generation(self):
        """Every replace sets ``disableAutomaticIdGeneration`` -- a replace
        targets an existing id and never mints one."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.replace_item("order-42", {"id": "order-42", "pk": "a"})

        forwarded_options = cc.ReplaceItem.call_args.kwargs["options"]
        self.assertIs(forwarded_options["disableAutomaticIdGeneration"], True)

    def test_etag_if_not_modified_becomes_guarded_replace_access_condition(self):
        """``etag`` + ``IfNotModified`` (the version-guarded replace) becomes
        the ``If-Match`` access condition on the legacy path -- the replace's
        headline precondition."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        proxy.replace_item(
            "order-42",
            {"id": "order-42", "pk": "a"},
            etag="abc",
            match_condition=MatchConditions.IfNotModified,
        )

        forwarded_options = cc.ReplaceItem.call_args.kwargs["options"]
        self.assertEqual(
            forwarded_options["accessCondition"],
            {"type": "IfMatch", "condition": "abc"},
        )

    def test_populate_query_metrics_warns_and_is_forwarded(self):
        """The deprecated sync-only ``populate_query_metrics`` still warns
        and still reaches the legacy options, exactly as the legacy
        ``replace_item`` did (warn-and-write, including for ``False``)."""
        proxy, cc, _ = _make_proxy_with_mock_connection()

        with self.assertWarns(DeprecationWarning):
            proxy.replace_item(
                "order-42", {"id": "order-42", "pk": "a"}, populate_query_metrics=True
            )

        forwarded_options = cc.ReplaceItem.call_args.kwargs["options"]
        self.assertIs(forwarded_options["populateQueryMetrics"], True)

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        """Cache miss: ``excluded_locations`` from the call reaches the
        cache-refresh ``read`` (same contract create / upsert have)."""
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.replace_item(
            "order-42", {"id": "order-42", "pk": "a"}, excluded_locations=["West US"]
        )

        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get("excluded_locations"), ["West US"])
        self.assertIn("dbs/db/colls/c", cache)

    def test_cache_populate_step_takes_container_cache_lock(self):
        """Cache populate runs under ``container_cache_lock`` (thread-safety)."""
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)
        lock_use_recorder = MagicMock(wraps=proxy.container_cache_lock)
        with patch.object(proxy, "container_cache_lock", lock_use_recorder):
            proxy.replace_item("order-42", {"id": "order-42", "pk": "a"})
        lock_use_recorder.__enter__.assert_called()

    def test_backend_path_uses_item_id_from_item_not_body(self):
        """On the rust backend path, the id the binding puts on the wire URL
        is resolved from ``item`` (a string id as-is, a dict's ``id`` field)
        and carried on ``PreparedRequest.item_id`` -- never re-derived from
        the body. Pins the parity fix: a body whose id disagrees with
        ``item`` must not retarget the write to the wrong document."""
        from azure.core.utils import CaseInsensitiveDict

        from azure.cosmos._backend.base import CosmosBackend
        from azure.cosmos._backend.contracts import BackendResponse

        proxy, cc, _ = _make_proxy_with_mock_connection()
        captured = {}

        class _CapturingBackend(CosmosBackend):
            name = "rust"

            def execute(self, prepared):
                captured["prepared"] = prepared
                return BackendResponse(
                    status_code=200,
                    sub_status=0,
                    headers=CaseInsensitiveDict({"etag": "v2"}),
                    body=b'{"id":"A","pk":"a"}',
                )

        cc._backend = _CapturingBackend()

        # Bare string id -> item_id is the string; the legacy ReplaceItem is
        # not called (the backend handled it).
        proxy.replace_item("A", {"id": "A", "pk": "a"})
        self.assertEqual(captured["prepared"].item_id, "A")
        cc.ReplaceItem.assert_not_called()

        # Document dict whose body carries a *different* id -> the URL still
        # targets the dict's id ("A"); the body keeps its own id ("B").
        item = {"id": "A", "pk": "a", "_self": "dbs/db/colls/c/docs/rid-A"}
        proxy.replace_item(item, {"id": "B", "pk": "a"})
        self.assertEqual(captured["prepared"].item_id, "A")
        self.assertEqual(json.loads(captured["prepared"].body_bytes)["id"], "B")


if __name__ == "__main__":
    unittest.main()
