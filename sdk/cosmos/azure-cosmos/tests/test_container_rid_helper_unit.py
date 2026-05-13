# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_container_rid.py`` â—” no network, no Cosmos emulator.

The helper is small but the failure mode it prevents is severe (items
silently land in the wrong container after a recreate). These tests
pin the contract by which the future item helper invokes it:

* Stamps the rid into options when missing.
* Skips when already present (defensive idempotency).
* Calls the ``get_rid`` callback exactly when needed.
* Leaves options untouched if the callback raises.
"""
import unittest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._container_rid import stamp_container_rid


class TestStampContainerRid(unittest.TestCase):
    """Behaviour of ``stamp_container_rid``."""

    def test_stamps_rid_into_empty_options(self):
        # The common case: no prior rid in options. Helper looks it up
        # via the callback and writes it under the constant key the
        # rest of the SDK reads.
        options = {}
        stamp_container_rid(
            options,
            "dbs/db/colls/orders",
            get_rid=lambda link: "rid-orders-1",
        )
        self.assertEqual(options, {Constants.ContainerRID: "rid-orders-1"})

    def test_skips_when_rid_already_present(self):
        # A caller (test fixture, replay scenario) has already set the
        # rid. We do not overwrite â—” the legacy
        # ``scripts._ensure_container_rid`` form is the right one.
        options = {Constants.ContainerRID: "rid-pre-existing"}
        stamp_container_rid(
            options,
            "dbs/db/colls/orders",
            get_rid=lambda link: self.fail("get_rid should not be called"),
        )
        self.assertEqual(options, {Constants.ContainerRID: "rid-pre-existing"})

    def test_get_rid_callback_receives_container_link(self):
        # The container_link argument is passed straight through. The
        # helper does not interpret or normalise it.
        seen = {}

        def capture(link):
            seen["link"] = link
            return "rid-x"

        stamp_container_rid({}, "dbs/db/colls/orders2026", get_rid=capture)
        self.assertEqual(seen["link"], "dbs/db/colls/orders2026")

    def test_get_rid_callback_called_only_once_when_needed(self):
        # Helpful invariant: the callback runs at most once per call.
        # Some real callbacks trigger a network refresh, so calling
        # them more than necessary would inflate latency.
        call_count = {"n": 0}

        def counting_get_rid(_link):
            call_count["n"] += 1
            return "rid"

        stamp_container_rid({}, "dbs/db/colls/c", get_rid=counting_get_rid)
        self.assertEqual(call_count["n"], 1)

    def test_get_rid_callback_not_called_when_rid_already_set(self):
        # The skip path is the whole point of the idempotency contract:
        # a pre-set rid means we must not even invoke the callback,
        # because the callback may be expensive (cache refresh).
        call_count = {"n": 0}

        def counting_get_rid(_link):
            call_count["n"] += 1
            return "rid"

        options = {Constants.ContainerRID: "preset"}
        stamp_container_rid(options, "dbs/db/colls/c", get_rid=counting_get_rid)
        self.assertEqual(call_count["n"], 0)

    def test_options_untouched_when_callback_raises(self):
        # If the callback raises (cache miss + refresh failure), we
        # propagate the exception and leave options exactly as it was.
        # No sentinel value, no half-stamped state.
        options = {"existing": "value"}

        def failing_get_rid(_link):
            raise RuntimeError("rid lookup failed")

        with self.assertRaises(RuntimeError):
            stamp_container_rid(options, "dbs/db/colls/c", get_rid=failing_get_rid)
        # The options dict is unchanged.
        self.assertEqual(options, {"existing": "value"})

    def test_stamping_does_not_disturb_other_options(self):
        # Other keys in the options dict are preserved.
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
        # The helper mutates in place and returns nothing. Make the
        # contract explicit so a caller cannot accidentally chain on
        # the return value.
        result = stamp_container_rid(
            {},
            "dbs/db/colls/c",
            get_rid=lambda _link: "rid-q",
        )
        self.assertIsNone(result)


class TestParityWithLegacyEnsureContainerRid(unittest.TestCase):
    """Cross-check against ``scripts._ensure_container_rid``.

    The legacy method does the same job but with the cache + refresh
    plumbing inlined. Reproducing it here as a callback composition
    proves the helper is a clean refactor of the legacy shape.
    """

    @staticmethod
    def _legacy_ensure(options, container_link, *, cache, on_cache_miss):
        # Replicates scripts._ensure_container_rid in the test so the
        # comparison is self-contained.
        if Constants.ContainerRID in options:
            return
        if container_link not in cache:
            on_cache_miss(container_link)
        options[Constants.ContainerRID] = cache[container_link]["_rid"]

    def test_helper_matches_legacy_for_cache_hit(self):
        # Cache already populated. Legacy and helper produce the same
        # options-dict mutation.
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
        # Cache empty initially; refresh callback populates it. Both
        # legacy and helper end with the rid stamped.
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
