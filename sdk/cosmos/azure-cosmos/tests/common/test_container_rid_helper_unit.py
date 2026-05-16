# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_container_rid.py`` — no network, no Cosmos emulator.

Every Cosmos container has an immutable internal id called the *rid*
(resource id). When a customer's deploy pipeline drops and recreates
a container with the same name (e.g. ``orders2026``), the new
container has a brand-new rid. If the SDK still has the old rid
cached and does not send it on the next request, the request lands
at the recreated (empty) container and the customer's freshly
written item appears to "vanish."

The fix is the ``x-ms-cosmos-intended-collection-rid`` header: when
the SDK sends the rid it currently believes a container has, the
service notices a mismatch, the SDK refreshes its caches, and the
request is retried against the right container.

``stamp_container_rid`` is the one helper that writes that rid into
the request-options dict. These tests cover its contract:

* Stamps the rid into options when missing.
* Skips when a rid is already present (defensive idempotency, so
  tests / replay scenarios can pre-set it).
* Calls the ``get_rid`` callback exactly when needed and at most
  once per call (the callback can be expensive — cache refresh).
* Leaves the options dict untouched if the callback raises.

Pure in-process; runs in milliseconds.
"""
import unittest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._container_rid import stamp_container_rid


class TestStampContainerRid(unittest.TestCase):
    """Direct behaviour of ``stamp_container_rid``.

    These tests cover the helper in isolation: stamping, idempotency,
    callback invocation count, exception propagation, and the
    "leaves other keys alone" contract.
    """

    def test_stamps_rid_into_empty_options(self):
        """Empty options + working callback → the looked-up rid appears under the constant key."""
        options = {}
        stamp_container_rid(
            options,
            "dbs/db/colls/orders",
            get_rid=lambda link: "rid-orders-1",
        )
        self.assertEqual(options, {Constants.ContainerRID: "rid-orders-1"})

    def test_skips_when_rid_already_present(self):
        """A pre-existing rid is preserved; the callback is not invoked at all."""
        options = {Constants.ContainerRID: "rid-pre-existing"}
        stamp_container_rid(
            options,
            "dbs/db/colls/orders",
            get_rid=lambda link: self.fail("get_rid should not be called"),
        )
        self.assertEqual(options, {Constants.ContainerRID: "rid-pre-existing"})

    def test_get_rid_callback_receives_container_link(self):
        """The ``container_link`` argument is passed straight through to the callback, unchanged."""
        seen = {}

        def capture(link):
            seen["link"] = link
            return "rid-x"

        stamp_container_rid({}, "dbs/db/colls/orders2026", get_rid=capture)
        self.assertEqual(seen["link"], "dbs/db/colls/orders2026")

    def test_get_rid_callback_called_only_once_when_needed(self):
        """The callback is invoked exactly once per stamp call (real callbacks may hit the network)."""
        call_count = {"n": 0}

        def counting_get_rid(_link):
            call_count["n"] += 1
            return "rid"

        stamp_container_rid({}, "dbs/db/colls/c", get_rid=counting_get_rid)
        self.assertEqual(call_count["n"], 1)

    def test_get_rid_callback_not_called_when_rid_already_set(self):
        """A pre-set rid means we must not even invoke the (potentially expensive) callback."""
        call_count = {"n": 0}

        def counting_get_rid(_link):
            call_count["n"] += 1
            return "rid"

        options = {Constants.ContainerRID: "preset"}
        stamp_container_rid(options, "dbs/db/colls/c", get_rid=counting_get_rid)
        self.assertEqual(call_count["n"], 0)

    def test_options_untouched_when_callback_raises(self):
        """If the callback raises, the exception propagates and the options dict is left as-is.

        No sentinel value, no half-stamped state — a clean failure is
        preferable to a request going out with a placeholder rid.
        """
        options = {"existing": "value"}

        def failing_get_rid(_link):
            raise RuntimeError("rid lookup failed")

        with self.assertRaises(RuntimeError):
            stamp_container_rid(options, "dbs/db/colls/c", get_rid=failing_get_rid)
        self.assertEqual(options, {"existing": "value"})

    def test_stamping_does_not_disturb_other_options(self):
        """Other keys in the options dict are preserved alongside the new rid."""
        options = {"preTriggerInclude": "validateOrder", "priorityLevel": "High"}
        stamp_container_rid(
            options,
            "dbs/db/colls/c",
            get_rid=lambda _link: "rid-z",
        )
        self.assertEqual(
            options,
            {
                "preTriggerInclude": "validateOrder",
                "priorityLevel": "High",
                Constants.ContainerRID: "rid-z",
            },
        )

    def test_returns_none(self):
        """The helper mutates in place and returns ``None`` (no chaining on the return value)."""
        result = stamp_container_rid(
            {},
            "dbs/db/colls/c",
            get_rid=lambda _link: "rid-q",
        )
        self.assertIsNone(result)


class TestParityWithLegacyEnsureContainerRid(unittest.TestCase):
    """Cross-check ``stamp_container_rid`` against the legacy ``scripts._ensure_container_rid``.

    The legacy method does the same job but with the cache + refresh
    plumbing inlined (no callback inversion). Reproducing the legacy
    shape inline as a callback composition proves the new helper is
    a clean refactor and produces identical options-dict mutations
    for the cache-hit and cache-miss-then-refresh paths.
    """

    @staticmethod
    def _legacy_ensure(options, container_link, *, cache, on_cache_miss):
        """Inline reproduction of ``scripts._ensure_container_rid``."""
        if Constants.ContainerRID in options:
            return
        if container_link not in cache:
            on_cache_miss(container_link)
        options[Constants.ContainerRID] = cache[container_link]["_rid"]

    def test_helper_matches_legacy_for_cache_hit(self):
        """Cache hit: legacy and helper produce the same options-dict mutation."""
        cache = {"dbs/db/colls/c": {"_rid": "rid-cached"}}

        legacy_options = {}
        self._legacy_ensure(
            legacy_options,
            "dbs/db/colls/c",
            cache=cache,
            on_cache_miss=lambda _link: self.fail("no miss expected"),
        )

        helper_options = {}
        stamp_container_rid(
            helper_options,
            "dbs/db/colls/c",
            get_rid=lambda link: cache[link]["_rid"],
        )

        self.assertEqual(legacy_options, helper_options)

    def test_helper_matches_legacy_for_cache_miss_then_refresh(self):
        """Cache miss + refresh: legacy and helper both end with the refreshed rid stamped."""
        cache = {}

        def refresh(link):
            cache[link] = {"_rid": "rid-refreshed"}

        legacy_options = {}
        self._legacy_ensure(
            legacy_options,
            "dbs/db/colls/c",
            cache=cache,
            on_cache_miss=refresh,
        )

        helper_options = {}

        def helper_get_rid(link):
            if link not in cache:
                refresh(link)
            return cache[link]["_rid"]

        stamp_container_rid(
            helper_options,
            "dbs/db/colls/c",
            get_rid=helper_get_rid,
        )

        self.assertEqual(legacy_options, helper_options)
        self.assertEqual(legacy_options, {Constants.ContainerRID: "rid-refreshed"})


if __name__ == "__main__":
    unittest.main()
