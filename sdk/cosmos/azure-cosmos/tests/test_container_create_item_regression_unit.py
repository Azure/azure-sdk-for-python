# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""End-to-end regression tests for the ``Container.create_item`` slim-down.

The container method used to do four things in one body: build request
options, populate the container-properties cache (via
``self._get_properties_with_options(request_options)``), stamp the
container rid, and call ``client_connection.CreateItem``. The slim-down
moved the request-build, cache-populate, and CreateItem-call into
``ItemHelper`` so both backends can share the same prep code.

This module asserts the slim-down preserved the *customer-observable*
behaviour the legacy method had. Two specific contracts that earlier
drafts of the helper accidentally broke:

1. The cache-populate step must still go through the proxy's
   ``_get_properties_with_options`` so the proxy's ``container_cache_lock``
   is taken (thread-safety) **and** per-call options like
   ``excluded_locations``, ``timeout``, and ``read_timeout`` are
   forwarded into the cache-refresh call. Calling
   ``client_connection._refresh_container_properties_cache`` directly
   would silently drop those.
2. The container method must still forward every kwarg to
   ``client_connection.CreateItem`` with the same option-dict shape.

These are pure in-process tests using a mocked ``client_connection``
plus a fake cache; no Cosmos emulator, no network.
"""
import unittest
from unittest.mock import MagicMock, patch

from azure.cosmos._constants import _Constants as Constants


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Return a real ContainerProxy with a mocked client_connection.

    The proxy's own ``container_cache_lock`` and
    ``_get_properties_with_options`` are real; only the underlying
    connection is mocked so the test can observe what was forwarded
    into ``CreateItem`` and what kwargs reached the cache-fetch step.
    """
    from azure.cosmos.container import ContainerProxy

    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    # Container-properties cache. The proxy reads this through
    # ``__get_client_container_caches()`` which delegates to the
    # connection's container_properties_cache attribute.
    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # legacy alias used by the proxy

    cc._rust_backend = None
    core_python = MagicMock()
    core_python.name = "core-python"
    core_python.create_item = MagicMock(return_value=None)
    cc._core_python_backend = core_python

    cc.CreateItem = MagicMock(return_value={"id": "x", "_rid": rid})

    # Build the proxy through its real constructor; we only intercept
    # the call into ContainerProxy.read so a cache miss does not
    # actually go to the network. The proxy's _get_properties /
    # _get_properties_with_options stay real so the lock + option
    # forwarding behaviour is exercised.
    proxy = ContainerProxy(cc, "dbs/db", "c")

    def _fake_read(**kwargs):
        # Populate the cache the way the real ContainerProxy.read would.
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerCreateItemPreservesLegacyCacheBehaviour(unittest.TestCase):
    """Guard against the cache-refresh regression the slim-down introduced once."""

    def test_cache_hit_path_still_stamps_rid_into_options(self):
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.create_item({"id": "x", "pk": "a"})

        cc.CreateItem.assert_called_once()
        forwarded_options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options[Constants.ContainerRID], "rid-hot")

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        # The legacy ``_get_properties_with_options`` lifted
        # ``excludedLocations`` out of the request_options dict and
        # passed it as an ``excluded_locations`` kwarg into
        # ``ContainerProxy.read``. The slim-down must preserve this so
        # a customer who set ``excluded_locations=["West US"]`` on the
        # ``create_item`` call also has it honoured during the cache
        # refresh.
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.create_item(
            {"id": "x", "pk": "a"},
            excluded_locations=["West US"],
        )

        # ContainerProxy.read should have been invoked with the
        # excluded_locations kwarg derived from the request options.
        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get("excluded_locations"), ["West US"])
        # And the rid stamped into the final CreateItem call must
        # match what the (just-populated) cache holds.
        self.assertIn("dbs/db/colls/c", cache)

    def test_cache_miss_forwards_timeout_kwargs_into_cache_fetch(self):
        # Same contract for ``timeout`` and ``read_timeout`` — the
        # legacy ``_get_properties_with_options`` extracted them and
        # passed them into the read.
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)

        proxy.create_item(
            {"id": "x", "pk": "a"},
            timeout=10,
            read_timeout=5,
        )

        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get(Constants.Kwargs.TIMEOUT), 10)
        self.assertEqual(read_kwargs.get(Constants.Kwargs.READ_TIMEOUT), 5)

    def test_cache_populate_step_takes_container_cache_lock(self):
        # The legacy ``_get_properties`` used double-checked locking
        # under ``container_cache_lock``. The slim-down must preserve
        # that. We assert by monkey-patching the lock and observing
        # __enter__ / __exit__.
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)
        lock_use_recorder = MagicMock(wraps=proxy.container_cache_lock)
        with patch.object(proxy, "container_cache_lock", lock_use_recorder):
            proxy.create_item({"id": "x", "pk": "a"})
        # __enter__ on the lock must have happened at least once
        # during the cache populate.
        lock_use_recorder.__enter__.assert_called()

    def test_create_item_forwards_disable_id_generation_option(self):
        proxy, cc, _cache = _make_proxy_with_mock_connection()

        proxy.create_item(
            {"id": "x", "pk": "a"},
            enable_automatic_id_generation=False,
        )

        forwarded_options = cc.CreateItem.call_args.kwargs["options"]
        self.assertTrue(forwarded_options["disableAutomaticIdGeneration"])

    def test_create_item_forwards_indexing_directive(self):
        proxy, cc, _cache = _make_proxy_with_mock_connection()

        proxy.create_item(
            {"id": "x", "pk": "a"},
            indexing_directive=1,
        )

        forwarded_options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options["indexingDirective"], 1)


if __name__ == "__main__":
    unittest.main()

