# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import unittest
import os
from unittest import mock

import pytest

from azure.cosmos import _session, http_constants
from azure.cosmos._vector_session_token import VectorSessionToken
from azure.cosmos.exceptions import CosmosHttpResponseError


class _DummyCollectionRanges:
    def __init__(self):
        self._rangeById = {}


class _DummyRoutingMapProvider:
    def __init__(self, collection_link: str):
        self._collection_routing_map_by_item = {collection_link: _DummyCollectionRanges()}


class _DummySyncClient:
    def __init__(self, collection_link: str):
        self._routing_map_provider = _DummyRoutingMapProvider(collection_link)
        self.refresh_calls = 0

    def refresh_routing_map_provider(self):
        self.refresh_calls += 1


class _DummyAsyncClient:
    def __init__(self, collection_link: str):
        self._routing_map_provider = _DummyRoutingMapProvider(collection_link)
        self.refresh_calls = 0

    async def refresh_routing_map_provider(self):
        self.refresh_calls += 1


@pytest.mark.cosmosEmulator
class TestSessionRefreshCompatibilityUnitTest(unittest.IsolatedAsyncioTestCase):
    """Tests session refresh compatibility across sync and async client connections."""

    async def test_set_session_token_schedules_async_refresh(self):
        collection_link = "dbs/db1/colls/c1"
        session_container = _session.SessionContainer()
        async_client = _DummyAsyncClient(collection_link)

        response_result = {"id": "doc1"}
        response_headers = {
            http_constants.HttpHeaders.AlternateContentPath: collection_link,
            http_constants.HttpHeaders.PartitionKeyRangeID: "3",
        }

        session_container.set_session_token(async_client, response_result, response_headers)
        await asyncio.sleep(0)

        self.assertEqual(async_client.refresh_calls, 1)

    async def test_set_session_token_calls_sync_refresh_directly(self):
        collection_link = "dbs/db1/colls/c1"
        session_container = _session.SessionContainer()
        sync_client = _DummySyncClient(collection_link)

        response_result = {"id": "doc1"}
        response_headers = {
            http_constants.HttpHeaders.AlternateContentPath: collection_link,
            http_constants.HttpHeaders.PartitionKeyRangeID: "3",
        }

        session_container.set_session_token(sync_client, response_result, response_headers)

        self.assertEqual(sync_client.refresh_calls, 1)

    async def test_set_session_token_closes_coroutine_when_no_running_loop(self):
        collection_link = "dbs/db1/colls/c1"
        session_container = _session.SessionContainer()
        async_client = _DummyAsyncClient(collection_link)

        response_result = {"id": "doc1"}
        response_headers = {
            http_constants.HttpHeaders.AlternateContentPath: collection_link,
            http_constants.HttpHeaders.PartitionKeyRangeID: "3",
        }

        with mock.patch("azure.cosmos._session.asyncio.get_running_loop", side_effect=RuntimeError):
            session_container.set_session_token(async_client, response_result, response_headers)

        self.assertEqual(async_client.refresh_calls, 0)


@pytest.mark.cosmosEmulator
class TestSessionTokenUnitTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    def test_validate_successful_session_token_parsing(self):
        # valid session token
        session_token = "1#100#1=20#2=5#3=30"
        self.assertEqual(VectorSessionToken.create(session_token).convert_to_string(), "1#100#1=20#2=5#3=30")

    def test_validate_session_token_parsing_with_invalid_version(self):
        session_token = "foo#100#1=20#2=5#3=30"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_with_invalid_global_lsn(self):
        session_token = "1#foo#1=20#2=5#3=30"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_with_invalid_region_progress(self):
        session_token = "1#100#1=20#2=x#3=30"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_with_invalid_format(self):
        session_token = "1;100#1=20#2=40"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_from_empty_string(self):
        session_token = ""
        self.assertIsNone(VectorSessionToken.create(session_token))

    def _different_merge_scenarios(self):
        # valid session token
        session_token1 = VectorSessionToken.create("1#100#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("2#105#4=10#2=5#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        self.assertFalse(session_token1.equals(session_token2))
        self.assertFalse(session_token2.equals(session_token1))

        session_token_merged = VectorSessionToken.create("2#105#2=5#3=30#4=10")
        self.assertIsNotNone(session_token_merged)
        self.assertTrue(session_token1.merge(session_token2).equals(session_token_merged))

        session_token1 = VectorSessionToken.create("1#100#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#100#1=10#2=8#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        self.assertFalse(session_token1.equals(session_token2))
        self.assertFalse(session_token2.equals(session_token1))

        session_token_merged = VectorSessionToken.create("1#100#1=20#2=8#3=30")
        self.assertIsNotNone(session_token_merged)
        self.assertTrue(session_token_merged.equals(session_token1.merge(session_token2)))

        session_token1 = VectorSessionToken.create("1#100#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#102#1=100#2=8#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token1)
        self.assertFalse(session_token1.equals(session_token2))
        self.assertFalse(session_token2.equals(session_token1))

        session_token_merged = VectorSessionToken.create("1#102#2=8#3=30#1=100")
        self.assertIsNotNone(session_token_merged)
        self.assertTrue(session_token_merged.equals(session_token1.merge(session_token2)))

        # same vector clock version with global lsn increase (no failover)
        session_token1 = VectorSessionToken.create("1#100#1=20#2=5")
        session_token2 = VectorSessionToken.create("1#197#1=20#2=5")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)

        self.assertTrue(session_token1.merge(session_token2).equals(
            VectorSessionToken.create("1#197#1=20#2=5")))

        # same vector clock version with global lsn increase and local lsn increase
        session_token1 = VectorSessionToken.create("1#100#1=20#2=5")
        session_token2 = VectorSessionToken.create("1#197#1=23#2=15")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)

        self.assertTrue(session_token1.merge(session_token2).equals(
            VectorSessionToken.create("1#197#1=23#2=15")))

        # different number of regions with same region should throw error
        session_token1 = VectorSessionToken.create("1#101#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#100#1=20#2=5#3=30#4=40")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        try:
            session_token1.merge(session_token2)
            self.fail("Region progress can not be different when version is same")
        except CosmosHttpResponseError as e:
            self.assertEqual(str(e),
                             "Status code: 500\nCompared session tokens '1#101#1=20#2=5#3=30' "
                             "and '1#100#1=20#2=5#3=30#4=40' have unexpected regions.")

        # same version with different region progress should throw error
        session_token1 = VectorSessionToken.create("1#101#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#100#4=20#2=5#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)

        try:
            session_token1.merge(session_token2)
            self.fail("Region progress can not be different when version is same")
        except CosmosHttpResponseError as e:
            self.assertEqual(str(e),
                             "Status code: 500\nCompared session tokens '1#101#1=20#2=5#3=30' "
                             "and '1#100#4=20#2=5#3=30' have unexpected regions.")

    def test_validate_session_token_comparison(self):
        self._different_merge_scenarios()
        os.environ["AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE"] = "false"
        self._different_merge_scenarios()
        del os.environ["AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE"]

    def test_session_token_false_progress_merge(self):
        for false_progress_enabled in [True, False]:
            self.validate_different_session_token_false_progress_merge_scenarios(false_progress_enabled)

    def validate_different_session_token_false_progress_merge_scenarios(self, false_progress_enabled: bool):
        # Test that false progress merge is enabled by default and that global lsn is used from higher version token
        # when enabled
        os.environ["AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE"] = str(false_progress_enabled)
        session_token1 = VectorSessionToken.create("1#200#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("2#100#1=10#2=8#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        if false_progress_enabled:
            expected_session_token = "2#100#1=20#2=8#3=30"
        else:
            expected_session_token = "2#200#1=20#2=8#3=30"
        self.assertTrue(session_token1.merge(session_token2).equals(
            VectorSessionToken.create(expected_session_token)))

        # vector clock version increase with removed region progress should merge
        session_token1 = VectorSessionToken.create("1#200#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("2#100#1=10#2=5")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)

        if false_progress_enabled:
            expected_session_token = "2#100#1=20#2=5"
        else:
            expected_session_token = "2#200#1=20#2=5"
        self.assertTrue(session_token1.merge(session_token2).equals(
            VectorSessionToken.create(expected_session_token)))

        # vector clock version increase with new region progress should merge
        session_token1 = VectorSessionToken.create("1#200#1=20#2=5")
        session_token2 = VectorSessionToken.create("2#100#1=10#2=5#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        if false_progress_enabled:
            expected_session_token = "2#100#1=20#2=5#3=30"
        else:
            expected_session_token = "2#200#1=20#2=5#3=30"
        self.assertTrue(session_token1.merge(session_token2).equals(
            VectorSessionToken.create(expected_session_token)))

if __name__ == '__main__':
    unittest.main()



class TestResolvePartitionLocalSessionTokenRegression(unittest.TestCase):
    """Regression tests for ``_resolve_partition_local_session_token``.

    Companion-fix for the PKRange migration at ``_session.py:386``:
    ``parents = list(pk_range[0].get('parents') or ())``. Previously this was
    ``pk_range[0]['parents'].copy()`` which crashed (a) on PKRange namedtuples
    because tuples have no ``.copy()`` and (b) when ``parents`` was ``None``.
    """

    def _container(self):
        return _session.SessionContainer()

    def test_pkrange_tuple_with_parents(self):
        """PKRange (namedtuple) input does not crash and parents are walked."""
        from azure.cosmos._routing.routing_range import PKRange
        pkr = PKRange(id="child", minInclusive="80", maxExclusive="FF",
                      parents=("parentA", "parentB"))
        # No tokens — function must not crash on the parents iteration.
        result = self._container()._resolve_partition_local_session_token(
            (pkr,), token_dict={})
        self.assertIsNone(result)

    def test_dict_with_none_parents_does_not_crash(self):
        """Old code did ``parents.copy()`` which raised AttributeError on None."""
        pkr = {"id": "0", "minInclusive": "", "maxExclusive": "FF", "parents": None}
        result = self._container()._resolve_partition_local_session_token(
            (pkr,), token_dict={})
        self.assertIsNone(result)

    def test_dict_with_empty_parents(self):
        pkr = {"id": "0", "minInclusive": "", "maxExclusive": "FF", "parents": []}
        result = self._container()._resolve_partition_local_session_token(
            (pkr,), token_dict={})
        self.assertIsNone(result)

    def test_dict_with_tuple_parents(self):
        pkr = {"id": "child", "parents": ("parentA",)}
        result = self._container()._resolve_partition_local_session_token(
            (pkr,), token_dict={})
        self.assertIsNone(result)

    def test_pkrange_walks_parents_then_self(self):
        """The iteration appends ``pk_range[0]['id']`` after parents, so an id
        token alone (no parent tokens) still resolves."""
        from azure.cosmos._routing.routing_range import PKRange
        from azure.cosmos._vector_session_token import VectorSessionToken
        pkr = PKRange(id="child", minInclusive="80", maxExclusive="FF", parents=())
        # Build a token for the child id only.
        # VectorSessionToken.create accepts the standard "version#globalLsn" form;
        # use a minimal valid token so .session_token round-trips.
        token = VectorSessionToken.create("1#1")
        # The session container holds dict[id] -> SessionToken-like object
        # whose ``session_token`` attribute is the string form. Wrap accordingly.
        class _Wrap:
            def __init__(self, t):
                self.session_token = t.session_token
        result = self._container()._resolve_partition_local_session_token(
            (pkr,), token_dict={"child": _Wrap(token)})
        self.assertEqual(result, token.session_token)

