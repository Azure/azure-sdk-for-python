# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process tests for the container metadata provider -- no network.

The provider reads the two container facts the request prep needs -- the
container's resource id and its partition-key definition -- off one container
read. These tests cover:

1. The partition-key extractor (``_pk_extract``): single- and multi-hash,
   nested paths, and the undefined / system-key sentinels.
2. The sync provider: rid from a cache hit, rid after a cache-miss refresh,
   reading the partition key out of a body via the cached definition, the
   "partition key already supplied" short-circuit, and the ``_Empty`` fallback
   for a container with no partition-key definition.
3. The async provider: the same rid and extraction behaviour, awaited.
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from azure.cosmos._helpers._metadata_provider import ContainerMetadataProvider
from azure.cosmos._helpers._pk_extract import extract_partition_key_value
from azure.cosmos._backend.base import build_backend_response
from azure.cosmos.aio._helpers._metadata_provider import AsyncContainerMetadataProvider
from azure.cosmos.partition_key import _Empty, _Undefined

_LINK = "dbs/db/colls/c"
_HASH_DEF = {"kind": "Hash", "paths": ["/pk"], "version": 2}
_MULTI_DEF = {"kind": "MultiHash", "paths": ["/a", "/b"], "version": 2}


# ---------------------------------------------------------------------------
# Pure partition-key extractor
# ---------------------------------------------------------------------------

class TestPureExtractor(unittest.TestCase):
    def test_single_hash_reads_leaf_value(self):
        self.assertEqual(extract_partition_key_value(_HASH_DEF, {"pk": "customerA"}), "customerA")

    def test_single_hash_nested_path(self):
        definition = {"kind": "Hash", "paths": ["/address/city"]}
        self.assertEqual(
            extract_partition_key_value(definition, {"address": {"city": "Seattle"}}),
            "Seattle",
        )

    def test_single_hash_missing_path_is_undefined(self):
        value = extract_partition_key_value(_HASH_DEF, {"id": "x"})
        self.assertIsInstance(value, _Undefined)

    def test_single_hash_missing_path_system_key_is_empty(self):
        definition = {"kind": "Hash", "paths": ["/pk"], "systemKey": True}
        value = extract_partition_key_value(definition, {"id": "x"})
        self.assertIsInstance(value, _Empty)

    def test_multi_hash_reads_each_level(self):
        self.assertEqual(
            extract_partition_key_value(_MULTI_DEF, {"a": "x", "b": "y"}),
            ["x", "y"],
        )

    def test_multi_hash_missing_level_collapses_to_none(self):
        # A missing level in a hierarchical key becomes ``None`` in the list.
        self.assertEqual(extract_partition_key_value(_MULTI_DEF, {"a": "x"}), ["x", None])


# ---------------------------------------------------------------------------
# Sync provider
# ---------------------------------------------------------------------------

def _cc_with_props(props):
    cc = MagicMock()
    cc._container_properties_cache = {_LINK: props}
    return cc


class TestSyncProvider(unittest.TestCase):
    def test_rust_metadata_response_bypasses_legacy_container_cache(self):
        cc = MagicMock()
        cc._container_properties_cache = {}
        resolver = MagicMock(
            return_value=build_backend_response(
                200,
                0,
                {},
                b'{"_rid":"rust-rid","partitionKey":{"paths":["/pk"],"kind":"Hash","version":2}}',
            )
        )
        provider = ContainerMetadataProvider(cc, resolve_through_backend=resolver)
        options = {}

        self.assertEqual(provider.container_rid(_LINK, options), "rust-rid")
        self.assertEqual(provider.extract_partition_key(_LINK, {"pk": "value"}, options), "value")

        resolver.assert_called_once_with(_LINK)
        cc._refresh_container_properties_cache.assert_not_called()

    def test_container_rid_from_cache_hit(self):
        provider = ContainerMetadataProvider(_cc_with_props({"_rid": "R", "partitionKey": _HASH_DEF}))
        self.assertEqual(provider.container_rid(_LINK, {}), "R")

    def test_container_rid_none_when_absent(self):
        provider = ContainerMetadataProvider(_cc_with_props({"partitionKey": _HASH_DEF}))
        self.assertIsNone(provider.container_rid(_LINK, {}))

    def test_container_rid_cache_miss_triggers_one_refresh(self):
        cc = MagicMock()
        cache = {}
        cc._container_properties_cache = cache
        cc._refresh_container_properties_cache = MagicMock(
            side_effect=lambda link: cache.__setitem__(link, {"_rid": "R2"})
        )
        provider = ContainerMetadataProvider(cc)
        self.assertEqual(provider.container_rid(_LINK, {}), "R2")
        cc._refresh_container_properties_cache.assert_called_once_with(_LINK)

    def test_extract_partition_key_from_body(self):
        provider = ContainerMetadataProvider(_cc_with_props({"_rid": "R", "partitionKey": _HASH_DEF}))
        options = {}
        value = provider.extract_partition_key(_LINK, {"pk": "v"}, options)
        self.assertEqual(value, "v")
        # The extracted value is written back into the options (legacy parity).
        self.assertEqual(options["partitionKey"], "v")

    def test_extract_partition_key_short_circuits_on_caller_value(self):
        # When the caller already set the partition key, no read happens.
        cc = MagicMock()
        cc._container_properties_cache = {}
        provider = ContainerMetadataProvider(cc)
        value = provider.extract_partition_key(_LINK, {"pk": "ignored"}, {"partitionKey": "given"})
        self.assertEqual(value, "given")
        cc._refresh_container_properties_cache.assert_not_called()

    def test_extract_partition_key_empty_when_no_definition(self):
        provider = ContainerMetadataProvider(_cc_with_props({"_rid": "R"}))
        value = provider.extract_partition_key(_LINK, {"pk": "v"}, {})
        self.assertIsInstance(value, _Empty)


# ---------------------------------------------------------------------------
# Async provider
# ---------------------------------------------------------------------------

class TestAsyncProvider(unittest.TestCase):
    def test_async_rust_metadata_response_bypasses_legacy_container_cache(self):
        cc = MagicMock()
        cc._container_properties_cache = {}
        resolver = AsyncMock(
            return_value=build_backend_response(
                200,
                0,
                {},
                b'{"_rid":"rust-rid","partitionKey":{"paths":["/a","/b"],"kind":"MultiHash","version":2}}',
            )
        )
        provider = AsyncContainerMetadataProvider(cc, resolve_through_backend=resolver)

        async def run():
            options = {}
            rid = await provider.container_rid(_LINK, options)
            value = await provider.extract_partition_key(
                _LINK, {"a": "x", "b": "y"}, options
            )
            return rid, value

        rid, value = asyncio.run(run())
        self.assertEqual(rid, "rust-rid")
        self.assertEqual(value, ["x", "y"])
        resolver.assert_awaited_once_with(_LINK)
        cc._refresh_container_properties_cache.assert_not_called()

    def test_async_container_rid_cache_miss_awaits_refresh(self):
        cc = MagicMock()
        cache = {}
        cc._container_properties_cache = cache

        async def refresh(link):
            cache[link] = {"_rid": "R-async"}

        cc._refresh_container_properties_cache = AsyncMock(side_effect=refresh)
        provider = AsyncContainerMetadataProvider(cc)

        rid = asyncio.run(provider.container_rid(_LINK, {}))
        self.assertEqual(rid, "R-async")
        cc._refresh_container_properties_cache.assert_awaited_once_with(_LINK)

    def test_async_extract_partition_key_from_body(self):
        cc = MagicMock()
        cc._container_properties_cache = {_LINK: {"_rid": "R", "partitionKey": _MULTI_DEF}}
        provider = AsyncContainerMetadataProvider(cc)
        options = {}
        value = asyncio.run(provider.extract_partition_key(_LINK, {"a": "x", "b": "y"}, options))
        self.assertEqual(value, ["x", "y"])
        self.assertEqual(options["partitionKey"], ["x", "y"])


if __name__ == "__main__":
    unittest.main()
