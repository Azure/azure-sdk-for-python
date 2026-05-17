# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Regression tests for the ``Container.create_item`` slim-down.

``Container.create_item`` used to do four things in one method body:
build the request options, populate the container-properties cache,
stamp the container rid into the options, and call
``client_connection.CreateItem``. The slim-down refactor moved the
last three steps into ``ItemHelper`` so both backends share the same
prep code.

During that move, two contracts got broken in earlier drafts and had
to be re-fixed:

1. The cache-populate step must still go through the proxy's
   ``_get_properties_with_options`` so:
     * the proxy's ``container_cache_lock`` is taken (thread-safety),
     * per-call options like ``excluded_locations``, ``timeout`` and
       ``read_timeout`` are forwarded into the cache-refresh read.
   Calling ``client_connection._refresh_container_properties_cache``
   directly would silently drop both of those.
2. Every kwarg the customer passed to ``create_item`` must still
   reach ``client_connection.CreateItem`` in the same option-dict
   shape the legacy method produced.

The emulator-backed end-to-end tests cannot catch these regressions:
the lock is invisible at the HTTP level, and the dropped
``excluded_locations`` / ``timeout`` only manifests in multi-region
or slow-network production. So these in-process tests act as the
guard that covers the contract.

All tests use a mocked ``client_connection`` plus a fake cache. No
network, no emulator, runs in milliseconds.
"""
import unittest
from unittest.mock import MagicMock, patch

from azure.cosmos._constants import _Constants as Constants


def _make_proxy_with_mock_connection(rid="rid-cached", precached=True):
    """Build a real ``ContainerProxy`` wired to a mocked ``client_connection``.

    The proxy's own ``container_cache_lock`` and
    ``_get_properties_with_options`` stay real — that's what these
    tests are checking. Only the underlying connection is mocked, so
    the test can observe what was forwarded into ``CreateItem`` and
    what kwargs reached the cache-refresh ``read``.
    """
    from azure.cosmos.container import ContainerProxy

    cc = MagicMock()
    container_link = "dbs/db/colls/c"

    # Container-properties cache. The proxy reads this through
    # ``__get_client_container_caches()``, which delegates to the
    # connection's ``container_properties_cache`` attribute.
    cache = {}
    if precached:
        cache[container_link] = {"_rid": rid}
    cc._container_properties_cache = cache
    cc.container_properties_cache = cache  # legacy alias used by the proxy

    # No rust backend wired in this test fixture — the absence of
    # ``_rust_backend`` is the signal for the dispatch site to fall
    # through to ``client_connection.CreateItem`` directly.
    cc._rust_backend = None
    cc.CreateItem = MagicMock(return_value={"id": "x", "_rid": rid})

    proxy = ContainerProxy(cc, "dbs/db", "c")

    # Stub ``ContainerProxy.read`` so a cache miss does not actually
    # hit the network. The fake records the kwargs it received and
    # populates the cache the way the real ``read`` would.
    def _fake_read(**kwargs):
        cache[container_link] = {"_rid": rid, "_read_kwargs": kwargs}

    proxy.read = MagicMock(side_effect=_fake_read)
    return proxy, cc, cache


class TestContainerCreateItemPreservesLegacyCacheBehaviour(unittest.TestCase):
    """Cover the four invariants the slim-down refactor must preserve.

    Each test corresponds to a contract that earlier drafts of the
    helper accidentally broke. Together they cover: rid stamping on
    the cache-hit path, per-call option forwarding into the
    cache-refresh read, and lock acquisition during cache populate.
    """

    def test_cache_hit_path_still_stamps_rid_into_options(self):
        """Cache hit: the cached ``_rid`` ends up in the options dict sent to ``CreateItem``."""
        proxy, cc, _ = _make_proxy_with_mock_connection(rid="rid-hot")

        proxy.create_item({"id": "x", "pk": "a"})

        cc.CreateItem.assert_called_once()
        forwarded_options = cc.CreateItem.call_args.kwargs["options"]
        self.assertEqual(forwarded_options[Constants.ContainerRID], "rid-hot")

    def test_cache_miss_forwards_excluded_locations_into_cache_fetch(self):
        """Cache miss: ``excluded_locations`` from the call reaches the cache-refresh ``read``.

        A customer who passes ``excluded_locations=["West US"]`` to
        ``create_item`` expects that hint to be honoured everywhere,
        including the cache refresh that happens on a cold container.
        Dropping it here would silently route the refresh through a
        region the customer asked us to avoid.
        """
        proxy, _cc, cache = _make_proxy_with_mock_connection(precached=False)

        proxy.create_item(
            {"id": "x", "pk": "a"},
            excluded_locations=["West US"],
        )

        proxy.read.assert_called_once()
        read_kwargs = proxy.read.call_args.kwargs
        self.assertEqual(read_kwargs.get("excluded_locations"), ["West US"])
        # Sanity: the cache was actually populated by the fake read.
        self.assertIn("dbs/db/colls/c", cache)

    def test_cache_miss_forwards_timeout_kwargs_into_cache_fetch(self):
        """Cache miss: ``timeout`` and ``read_timeout`` reach the cache-refresh ``read``.

        Same contract as ``excluded_locations`` — a 5-second
        ``read_timeout`` on the customer's call must not silently
        become the default 60-second timeout during cache refresh.
        """
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
        """Cache populate runs under ``container_cache_lock`` (thread-safety invariant).

        The legacy ``_get_properties`` used double-checked locking
        under this lock. The slim-down must keep doing so or two
        threads racing on a cold container can corrupt the cache.
        We assert by wrapping the lock and watching ``__enter__``.
        """
        proxy, _cc, _cache = _make_proxy_with_mock_connection(precached=False)
        lock_use_recorder = MagicMock(wraps=proxy.container_cache_lock)
        with patch.object(proxy, "container_cache_lock", lock_use_recorder):
            proxy.create_item({"id": "x", "pk": "a"})
        lock_use_recorder.__enter__.assert_called()


if __name__ == "__main__":
    unittest.main()

