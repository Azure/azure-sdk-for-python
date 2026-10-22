# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""LocationCache parity checks in async test classes.

Most tests in this module assert the same fallback and normalization
invariants as the sync suite while running under async unittest
classes. A small set of tests explicitly awaits async endpoint-manager
APIs to validate startup refresh/fetch behavior under coroutine
execution. All tests use mocks; no live account.
"""

import asyncio
import logging
import unittest
import unittest.mock

import pytest

from azure.cosmos import exceptions
from azure.cosmos import documents
from azure.cosmos.aio._global_endpoint_manager_async import _GlobalEndpointManager as _AsyncGlobalEndpointManager
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType
from azure.cosmos._location_cache import LocationCache, _normalize_region_name
from azure.cosmos._request_object import RequestObject
from azure.cosmos._service_request_retry_policy import ServiceRequestRetryPolicy


default_endpoint = "https://default.documents.azure.com"
location1_name = "location1"
location2_name = "location2"
location3_name = "location3"
location4_name = "location4"
location1_endpoint = "https://location1.documents.azure.com"
location2_endpoint = "https://location2.documents.azure.com"
location3_endpoint = "https://location3.documents.azure.com"
location4_endpoint = "https://location4.documents.azure.com"


# Canonical regions used by the normalization tests below. These mimic the
# region names the service returns so tests can pass spelling variants and
# confirm they still resolve to the canonical endpoint.
canonical_location1_name = "East US 2"
canonical_location2_name = "West US 3"
canonical_location3_name = "Central US"
canonical_location1_endpoint = "https://eastus2.documents.azure.com"
canonical_location2_endpoint = "https://westus3.documents.azure.com"
canonical_location3_endpoint = "https://centralus.documents.azure.com"


def _create_database_account_with_canonical_regions(enable_multiple_writable_locations, three_regions=False):
    """Builds a DatabaseAccount whose region names match real Azure regions.
    Set three_regions=True to include a third region (Central US)."""
    db_acc = documents.DatabaseAccount()
    regions = [
        {"name": canonical_location1_name, "databaseAccountEndpoint": canonical_location1_endpoint},
        {"name": canonical_location2_name, "databaseAccountEndpoint": canonical_location2_endpoint},
    ]
    if three_regions:
        regions.append(
            {"name": canonical_location3_name, "databaseAccountEndpoint": canonical_location3_endpoint},
        )
    db_acc._WritableLocations = list(regions)
    db_acc._ReadableLocations = list(regions)
    db_acc._EnableMultipleWritableLocations = enable_multiple_writable_locations
    return db_acc


def _refresh_location_cache_with_policy(preferred, excluded, use_multiple_write_locations=True):
    """Builds a LocationCache with the given preferred and excluded lists."""
    cp = documents.ConnectionPolicy()
    cp.PreferredLocations = list(preferred)
    if excluded is not None:
        cp.ExcludedLocations = list(excluded)
    cp.UseMultipleWriteLocations = use_multiple_write_locations
    return LocationCache(default_endpoint=default_endpoint, connection_policy=cp)


def _create_database_account(enable_multiple_writable_locations):
    """Builds a DatabaseAccount with three write regions and three
    read regions so tests can pick which one to mark unavailable."""
    db_acc = documents.DatabaseAccount()
    db_acc._WritableLocations = [
        {"name": location1_name, "databaseAccountEndpoint": location1_endpoint},
        {"name": location2_name, "databaseAccountEndpoint": location2_endpoint},
        {"name": location3_name, "databaseAccountEndpoint": location3_endpoint},
    ]
    db_acc._ReadableLocations = [
        {"name": location1_name, "databaseAccountEndpoint": location1_endpoint},
        {"name": location2_name, "databaseAccountEndpoint": location2_endpoint},
        {"name": location4_name, "databaseAccountEndpoint": location4_endpoint},
    ]
    db_acc._EnableMultipleWritableLocations = enable_multiple_writable_locations
    return db_acc


def _refresh_location_cache(preferred_locations, use_multiple_write_locations):
    """Builds a LocationCache with the given preferred regions."""
    cp = documents.ConnectionPolicy()
    cp.PreferredLocations = preferred_locations
    cp.UseMultipleWriteLocations = use_multiple_write_locations
    return LocationCache(default_endpoint=default_endpoint, connection_policy=cp)


@pytest.mark.cosmosEmulator
class TestLocationCacheAsync(unittest.IsolatedAsyncioTestCase):
    """Async-context tests for the unavailable-region fallback behavior."""

    async def test_unavailable_read_endpoint_remains_in_routing_list_async(self):
        """Read path: if the only healthy region is excluded by the
        caller, routing should still fall back to the unavailable
        preferred region instead of dropping to the global default."""
        preferred_locations = [location1_name, location2_name]
        lc = _refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        lc.perform_on_database_account_read(_create_database_account(True))

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(read_request)
        self.assertEqual(
            resolved, location1_endpoint,
            "Expected the unavailable preferred region to be used as a "
            "last-resort regional endpoint instead of the global default.",
        )

    async def test_unavailable_write_endpoint_remains_in_routing_list_async(self):
        """Write path version of the read test above."""
        preferred_locations = [location1_name, location2_name]
        lc = _refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        lc.perform_on_database_account_read(_create_database_account(True))

        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")

        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(write_request)
        self.assertEqual(
            resolved, location1_endpoint,
            "Expected the unavailable preferred region to be used as a "
            "last-resort regional endpoint instead of the global default.",
        )

    async def test_async_global_endpoint_manager_returns_unavailable_as_last_resort(self):
        """Drives the async endpoint-manager wrapper directly. The
        wrapper is a thin pass-through to the shared cache, so this
        test checks the wrapper does not lose or re-filter the
        unavailable-as-last-resort ordering."""
        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = [location1_name, location2_name]
        cp.UseMultipleWriteLocations = True
        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _AsyncGlobalEndpointManager(mock_client)
        gem.location_cache.perform_on_database_account_read(_create_database_account(True))

        # Mark location1 unavailable for both reads and writes.
        gem.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True, context="test")
        gem.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")

        # Read routing list should include both regions, unavailable one last.
        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_ctxs = gem.get_applicable_read_regional_routing_contexts(read_request)
        read_endpoints = [c.get_primary() for c in read_ctxs]
        self.assertEqual(
            read_endpoints, [location2_endpoint, location1_endpoint],
            "Unavailable read endpoint should appear at the tail of the list.",
        )

        # If the only healthy region is excluded, the unavailable
        # region should still be returned.
        read_request.excluded_locations = [location2_name]
        resolved = gem._resolve_service_endpoint(read_request)
        self.assertEqual(
            resolved, location1_endpoint,
            "Expected the unavailable preferred region when the only healthy "
            "region is excluded.",
        )

        # Same check for writes.
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_ctxs = gem.get_applicable_write_regional_routing_contexts(write_request)
        write_endpoints = [c.get_primary() for c in write_ctxs]
        self.assertEqual(
            write_endpoints, [location2_endpoint, location1_endpoint],
            "Unavailable write endpoint should appear at the tail of the list.",
        )

        write_request.excluded_locations = [location2_name]
        resolved_write = gem._resolve_service_endpoint(write_request)
        self.assertEqual(
            resolved_write, location1_endpoint,
            "Expected the unavailable preferred region when the only healthy "
            "region is excluded.",
        )

    async def test_async_endpoint_manager_get_database_account_uses_preferred_fallback_async(self):
        """_GetDatabaseAccount should await the default endpoint first, then
        await preferred-region fallback endpoints when default fails."""
        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = [location1_name]
        cp.UseMultipleWriteLocations = True
        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _AsyncGlobalEndpointManager(mock_client)
        account = _create_database_account(True)
        default_error = exceptions.CosmosHttpResponseError(
            status_code=503,
            message="Injected default-endpoint failure",
        )
        gem._GetDatabaseAccountStub = unittest.mock.AsyncMock(
            side_effect=[default_error, account],
        )

        resolved = await gem._GetDatabaseAccount()
        self.assertIs(resolved, account)

        locational_endpoint = LocationCache.GetLocationalEndpoint(
            default_endpoint, location1_name,
        )
        gem._GetDatabaseAccountStub.assert_has_awaits(
            [
                unittest.mock.call(default_endpoint),
                unittest.mock.call(locational_endpoint),
            ],
            any_order=False,
        )

    async def test_async_refresh_endpoint_list_concurrent_calls_fetch_once_async(self):
        """Concurrent refresh calls should serialize on the async lock and
        avoid duplicate account fetches when startup refresh is in flight."""
        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = [location1_name, location2_name]
        cp.UseMultipleWriteLocations = True
        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _AsyncGlobalEndpointManager(mock_client)
        gem.startup = True
        gem.refresh_needed = True
        gem._aenter_used = True

        call_counter = {"count": 0}
        account = _create_database_account(True)

        async def _get_account_once(**_kwargs):
            call_counter["count"] += 1
            await asyncio.sleep(0.01)
            return account

        gem._GetDatabaseAccount = unittest.mock.AsyncMock(side_effect=_get_account_once)
        gem._endpoints_health_check = unittest.mock.AsyncMock(return_value=None)

        await asyncio.gather(
            gem.refresh_endpoint_list(None),
            gem.refresh_endpoint_list(None),
        )

        if gem.refresh_task:
            await gem.refresh_task

        self.assertEqual(call_counter["count"], 1)
        self.assertFalse(gem.startup)
        self.assertGreater(len(gem.location_cache.get_ordered_read_locations()), 0)

    async def test_async_service_request_retry_policy_routes_through_unavailable_as_last_resort(self):  # pylint: disable=line-too-long
        """Drives the retry policy through the full retry-then-fallback
        sequence for a write. After both preferred regions are marked
        unavailable and the retry budget is exhausted, the final
        resolution must still surface a regional endpoint, not the
        global default."""
        preferred_locations = [location1_name, location2_name]
        lc = _refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        lc.perform_on_database_account_read(_create_database_account(True))

        mock_gem = unittest.mock.Mock()
        mock_gem.location_cache = lc
        mock_gem.resolve_service_endpoint_for_partition.side_effect = [location2_endpoint]
        mock_gem.mark_endpoint_unavailable_for_write = lc.mark_endpoint_unavailable_for_write

        mock_connection_policy = unittest.mock.Mock()
        mock_connection_policy.EnableEndpointDiscovery = True
        mock_pk_range_wrapper = unittest.mock.Mock()

        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        resolved_endpoint = lc.resolve_service_endpoint(write_request)
        self.assertEqual(resolved_endpoint, location1_endpoint)

        write_request.location_endpoint_to_route = location1_endpoint
        retry_policy = ServiceRequestRetryPolicy(
            mock_connection_policy, mock_gem, mock_pk_range_wrapper, write_request,
        )

        # First retry marks location1 unavailable and switches to location2.
        self.assertTrue(retry_policy.ShouldRetry())
        self.assertEqual(write_request.location_endpoint_to_route, location2_endpoint)
        self.assertTrue(lc.is_endpoint_unavailable(location1_endpoint, "Write"))

        # Second retry exhausts the budget.
        self.assertFalse(retry_policy.ShouldRetry())
        self.assertTrue(lc.is_endpoint_unavailable(location2_endpoint, "Write"))

        # Final fallback should surface the unavailable preferred region,
        # not the global default.
        write_request.clear_route_to_location()
        write_request.use_preferred_locations = False

        final_endpoint = lc.resolve_service_endpoint(write_request)
        self.assertEqual(
            final_endpoint, location1_endpoint,
            "Final fallback returned the global default instead of an "
            "unavailable preferred region.",
        )

    async def test_async_retry_policy_read_path_routes_through_unavailable_as_last_resort(self):  # pylint: disable=line-too-long
        """Read-path version of the retry-then-fallback test above."""
        preferred_locations = [location1_name, location2_name]
        lc = _refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        lc.perform_on_database_account_read(_create_database_account(True))

        mock_gem = unittest.mock.Mock()
        mock_gem.location_cache = lc
        mock_gem.resolve_service_endpoint_for_partition.side_effect = [location2_endpoint]
        mock_gem.mark_endpoint_unavailable_for_read = lc.mark_endpoint_unavailable_for_read

        mock_connection_policy = unittest.mock.Mock()
        mock_connection_policy.EnableEndpointDiscovery = True
        mock_pk_range_wrapper = unittest.mock.Mock()

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        resolved_endpoint = lc.resolve_service_endpoint(read_request)
        self.assertEqual(resolved_endpoint, location1_endpoint)

        read_request.location_endpoint_to_route = location1_endpoint
        retry_policy = ServiceRequestRetryPolicy(
            mock_connection_policy, mock_gem, mock_pk_range_wrapper, read_request,
        )

        self.assertTrue(retry_policy.ShouldRetry())
        self.assertEqual(read_request.location_endpoint_to_route, location2_endpoint)
        self.assertTrue(lc.is_endpoint_unavailable(location1_endpoint, "Read"))

        self.assertFalse(retry_policy.ShouldRetry())
        self.assertTrue(lc.is_endpoint_unavailable(location2_endpoint, "Read"))

        read_request.clear_route_to_location()
        read_request.use_preferred_locations = False
        final_endpoint = lc.resolve_service_endpoint(read_request)
        self.assertEqual(
            final_endpoint, location1_endpoint,
            "Final fallback returned the global default instead of an "
            "unavailable preferred region.",
        )

    # The tests below cover topologies and helpers that the existing
    # tests don't touch: single-write accounts, the no-duplicates
    # invariant, the health-check probe set, and the metadata routing
    # path. Each one runs inside an async coroutine to catch any
    # event-loop interaction with the shared cache.

    async def test_async_single_write_account_read_unavailable_and_excluded_async(self):
        """Single-write account read path. This is the common
        topology and the other tests only cover multi-write."""
        preferred_locations = [location1_name, location2_name]
        # use_multiple_write_locations=False on the policy plus
        # enable_multiple_writable_locations=False on the account = single-write.
        lc = _refresh_location_cache(preferred_locations, use_multiple_write_locations=False)
        lc.perform_on_database_account_read(_create_database_account(False))

        self.assertFalse(lc.can_use_multiple_write_locations(),
                         "Test setup must be a single-write account.")

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(read_request)
        self.assertEqual(
            resolved, location1_endpoint,
            "Single-write read path returned the global default instead of "
            "the unavailable preferred region.",
        )

    async def test_async_routing_list_has_no_duplicate_endpoints(self):
        """The routing list should never contain the same endpoint
        twice, regardless of which regions are marked unavailable."""
        endpoint_by_loc = {location1_name: location1_endpoint, location2_name: location2_endpoint}
        for unavailable in ([], [location1_name], [location1_name, location2_name]):
            with self.subTest(unavailable=unavailable):
                lc = _refresh_location_cache(
                    [location1_name, location2_name], use_multiple_write_locations=True,
                )
                lc.perform_on_database_account_read(_create_database_account(True))

                for loc in unavailable:
                    lc.mark_endpoint_unavailable_for_read(endpoint_by_loc[loc], refresh_cache=True)

                read_primaries = [c.get_primary() for c in lc.get_read_regional_routing_contexts()]
                self.assertEqual(
                    len(read_primaries), len(set(read_primaries)),
                    f"Read routing list has duplicates: {read_primaries}",
                )
                self.assertEqual(set(read_primaries), {location1_endpoint, location2_endpoint})

                # Read marks don't affect the write side, so mark again for writes.
                for loc in unavailable:
                    lc.mark_endpoint_unavailable_for_write(
                        endpoint_by_loc[loc], refresh_cache=True, context="test",
                    )
                write_primaries = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
                self.assertEqual(
                    len(write_primaries), len(set(write_primaries)),
                    f"Write routing list has duplicates: {write_primaries}",
                )
                self.assertEqual(set(write_primaries), {location1_endpoint, location2_endpoint})

    async def test_async_health_check_set_includes_unavailable_endpoints(self):
        """An endpoint marked unavailable should stay in the set the
        background health-check loop probes, so it can be re-marked
        available once it recovers."""
        lc = _refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(_create_database_account(True))
        lc.mark_endpoint_unavailable_for_write(
            location1_endpoint, refresh_cache=True, context="test"
        )
        self.assertEqual(
            lc.get_write_regional_routing_contexts()[0].get_primary(),
            location2_endpoint,
            "Test precondition failed: location1 must not be the primary write endpoint.",
        )

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)
        endpoints = lc.endpoints_to_health_check()
        self.assertIn(
            location1_endpoint, endpoints,
            "Health-check probe set is missing the unavailable read endpoint.",
        )
        self.assertIn(location2_endpoint, endpoints)


    async def test_async_master_resource_with_all_healthy_prefers_non_excluded(self):
        """With every region healthy, a metadata request should still
        prefer a healthy non-excluded region over a healthy excluded one."""
        lc = _refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(_create_database_account(True))

        # No mark_endpoint_unavailable calls; both regions stay healthy.

        master_request = RequestObject(ResourceType.Database, _OperationType.Read, None)
        master_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(master_request)
        self.assertEqual(
            resolved, location1_endpoint,
            f"Expected the healthy non-excluded region ({location1_endpoint}) "
            f"to come first, but got {resolved}.",
        )

    async def test_async_data_call_with_exclusion_and_unavailable_preserves_fallback(self):
        # For a data request, excluded_locations is a hard filter. With one
        # region unavailable and the other excluded, the SDK should still
        # return the unavailable non-excluded region before falling back to
        # the global default.
        lc = _refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(_create_database_account(True))

        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")

        data_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        data_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(data_request)
        self.assertEqual(
            resolved, location1_endpoint,
            f"Expected the unavailable non-excluded region ({location1_endpoint}) "
            f"as a last-resort regional endpoint, but got {resolved}.",
        )

    """
    Additional async coverage for keeping unavailable endpoints as
    fallback options. Recovery, account-topology refresh, and
    circuit-breaker read fallback are exercised here.
    """

    async def test_async_mark_endpoint_available_restores_head_position_async(self):
        # After recovery, a previously-unavailable preferred endpoint should
        # return to the head of the routing list, not stay at the tail.
        lc = _refresh_location_cache(
            [location1_name, location2_name, location3_name],
            use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(_create_database_account(True))

        self.assertEqual(
            lc.read_regional_routing_contexts[0].get_primary(), location1_endpoint
        )
        self.assertEqual(
            lc.write_regional_routing_contexts[0].get_primary(), location1_endpoint
        )

        # Mark location1 unavailable on both lanes; it should slide to the tail.
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")
        self.assertEqual(lc.read_regional_routing_contexts[-1].get_primary(), location1_endpoint)
        self.assertEqual(lc.write_regional_routing_contexts[-1].get_primary(), location1_endpoint)

        # Health-probe rehabilitates the endpoint.
        lc.mark_endpoint_available(location1_endpoint)
        lc.update_location_cache()

        self.assertFalse(lc.is_endpoint_unavailable(location1_endpoint, "Read"))
        self.assertFalse(lc.is_endpoint_unavailable(location1_endpoint, "Write"))
        self.assertEqual(
            lc.read_regional_routing_contexts[0].get_primary(), location1_endpoint,
            "Recovered endpoint should return to the head of the read routing list."
        )
        self.assertEqual(
            lc.write_regional_routing_contexts[0].get_primary(), location1_endpoint,
            "Recovered endpoint should return to the head of the write routing list."
        )

    async def test_account_topology_refresh_preserves_unavailability_tail_order_async(self):
        # A periodic account-topology refresh must not drop endpoints that
        # were marked unavailable, and the tail ordering must be preserved.
        lc = _refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True,
        )
        db_acc = _create_database_account(True)
        lc.perform_on_database_account_read(db_acc)

        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")
        write_primaries_before = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
        self.assertEqual(write_primaries_before, [location2_endpoint, location1_endpoint])

        # Simulate periodic background refresh — same topology comes back.
        lc.perform_on_database_account_read(db_acc)

        self.assertTrue(
            lc.is_endpoint_unavailable(location1_endpoint, "Write"),
            "Unavailability mark must survive an account-topology refresh.",
        )
        write_primaries_after = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
        self.assertEqual(
            write_primaries_after, write_primaries_before,
            "Account-topology refresh dropped the unavailable endpoint from the routing list.",
        )

    async def test_async_circuit_breaker_excluded_read_falls_back_before_global_default_async(self):
        # With the only healthy region user-excluded and the other region
        # circuit-breaker-excluded, reads should still resolve to the
        # circuit-breaker-excluded region instead of the global default.
        lc = _refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(_create_database_account(True))

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.excluded_locations = [location1_name]
        read_request.excluded_locations_circuit_breaker = [location2_name]

        resolved = lc.resolve_service_endpoint(read_request)
        self.assertEqual(
            resolved, location2_endpoint,
            "Read should fall back to the circuit-breaker-excluded region "
            "instead of dropping to the global default.",
        )


@pytest.mark.cosmosEmulator
class TestRegionNormalizationAsync(unittest.IsolatedAsyncioTestCase):
    """Async-context coverage for region-name normalization.

    Drives the same matching behavior the sync tests cover from inside
    coroutines so any event-loop interaction with the shared cache shows up.
    """

    async def test_preferred_locations_support_spelling_variants_async(self):
        # Each preferred entry uses a different spelling style. All three
        # should resolve to the canonical account endpoints in order.
        lc = _refresh_location_cache_with_policy(
            preferred=["east-us-2", " WEST_US_3 ", "Central US"],
            excluded=None,
        )
        lc.perform_on_database_account_read(
            _create_database_account_with_canonical_regions(True, three_regions=True),
        )

        write_endpoints = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
        read_endpoints = [c.get_primary() for c in lc.get_read_regional_routing_contexts()]
        expected = [
            canonical_location1_endpoint,
            canonical_location2_endpoint,
            canonical_location3_endpoint,
        ]
        self.assertEqual(write_endpoints, expected)
        self.assertEqual(read_endpoints, expected)

    async def test_excluded_locations_support_spelling_variants_async(self):
        # Client-level excluded list uses one spelling, per-request list uses
        # another. Both should filter the same region the canonical name does.
        lc = _refresh_location_cache_with_policy(
            preferred=[canonical_location1_name, canonical_location2_name],
            excluded=["east-us-2"],
        )
        lc.perform_on_database_account_read(_create_database_account_with_canonical_regions(True))

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.excluded_locations = ["WEST_US_3"]

        self.assertEqual(lc.resolve_service_endpoint(read_request), canonical_location2_endpoint)
        self.assertEqual(lc.resolve_service_endpoint(write_request), canonical_location1_endpoint)

    async def test_excluded_locations_ignore_none_and_empty_async(self):
        # None, empty, and whitespace-only entries must not block valid
        # exclusions and must not match real endpoints by accident.
        lc = _refresh_location_cache_with_policy(
            preferred=[canonical_location1_name, canonical_location2_name],
            excluded=[None, "", "  ", "east-us-2"],
        )
        lc.perform_on_database_account_read(_create_database_account_with_canonical_regions(True))

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.excluded_locations = [None, "", "west_us_3"]

        self.assertEqual(lc.resolve_service_endpoint(read_request), canonical_location2_endpoint)
        self.assertEqual(lc.resolve_service_endpoint(write_request), canonical_location1_endpoint)

    async def test_duplicate_normalized_entries_warn_once_async(self):
        # The same region listed three times in three spellings should still
        # filter correctly and should not produce a mismatch warning.
        lc = _refresh_location_cache_with_policy(
            preferred=[canonical_location1_name, canonical_location2_name],
            excluded=["East US 2", "east-us-2", "EAST_US_2"],
        )

        with self.assertLogs("azure.cosmos.LocationCache", level=logging.WARNING) as captured:
            lc.perform_on_database_account_read(_create_database_account_with_canonical_regions(True))
            read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
            resolved = lc.resolve_service_endpoint(read_request)
            # assertLogs requires at least one record, so emit a marker.
            logging.getLogger("azure.cosmos.LocationCache").warning("marker")

        self.assertEqual(resolved, canonical_location2_endpoint)
        mismatch_messages = [m for m in captured.output if "did not match" in m]
        self.assertEqual(mismatch_messages, [])

    async def test_resolve_endpoint_without_preferred_locations_supports_variants_async(self):
        # Per-request exclusions should still apply when the request opts out
        # of preferred-location routing.
        lc = _refresh_location_cache_with_policy(
            preferred=[],
            excluded=None,
        )
        lc.perform_on_database_account_read(_create_database_account_with_canonical_regions(True))

        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.use_preferred_locations = False
        write_request.excluded_locations = ["east-us-2"]
        self.assertEqual(lc.resolve_service_endpoint(write_request), canonical_location2_endpoint)

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.use_preferred_locations = False
        read_request.excluded_locations = ["west_us_3"]
        self.assertEqual(lc.resolve_service_endpoint(read_request), canonical_location1_endpoint)

    async def test_should_refresh_endpoints_handles_normalized_preferred_async(self):
        # When the most preferred region uses a non-canonical spelling and is
        # already the primary, no background refresh should be scheduled.
        lc = _refresh_location_cache_with_policy(preferred=["east-us-2"], excluded=None)
        lc.perform_on_database_account_read(_create_database_account_with_canonical_regions(True))
        self.assertFalse(lc.should_refresh_endpoints())

    async def test_should_refresh_endpoints_true_when_normalized_preferred_is_not_primary_async(self):
        # When the most preferred region is no longer the primary because its
        # endpoint was marked unavailable, a refresh should be scheduled.
        lc = _refresh_location_cache_with_policy(
            preferred=["east-us-2", "west-us-3"], excluded=None,
        )
        lc.perform_on_database_account_read(_create_database_account_with_canonical_regions(True))
        lc.mark_endpoint_unavailable_for_read(canonical_location1_endpoint, refresh_cache=True)

        self.assertEqual(
            lc.read_regional_routing_contexts[0].get_primary(), canonical_location2_endpoint,
        )
        self.assertTrue(lc.should_refresh_endpoints())

    async def test_get_locational_endpoint_normalizes_customer_region_async(self):
        # The static helper should produce the same regional URL for every
        # spelling variant of the same region.
        default_endpoint_url = "https://contoso.documents.azure.com:443/"
        expected = "https://contoso-eastus2.documents.azure.com:443/"
        for variant in ("East US 2", "east us 2", "eastus2", "east-us-2", "east_us_2",
                        " EastUs2 ", "EAST-US_2", "East  US  2"):
            self.assertEqual(LocationCache.GetLocationalEndpoint(default_endpoint_url, variant), expected)

    async def test_async_endpoint_manager_normalizes_preferred_locations_from_policy_async(self):
        # End-to-end check that messy region names set on ConnectionPolicy
        # flow through the async endpoint manager into the location cache.
        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = ["east-us-2", " WEST_US_3 "]
        cp.UseMultipleWriteLocations = True

        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _AsyncGlobalEndpointManager(mock_client)
        gem.location_cache.perform_on_database_account_read(
            _create_database_account_with_canonical_regions(True),
        )

        read_endpoints = [
            c.get_primary() for c in gem.location_cache.get_read_regional_routing_contexts()
        ]
        self.assertEqual(
            read_endpoints, [canonical_location1_endpoint, canonical_location2_endpoint],
        )


class TestNormalizeRegionNameAsync(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the helper, exercised inside coroutines for parity
    with the rest of the async suite."""

    async def test_does_not_collapse_prefix_sharing_regions_async(self):
        self.assertNotEqual(_normalize_region_name("East US"), _normalize_region_name("East US 2"))
        self.assertNotEqual(_normalize_region_name("West US"), _normalize_region_name("West US 2"))
        self.assertNotEqual(_normalize_region_name("Central US"), _normalize_region_name("North Central US"))
        self.assertNotEqual(_normalize_region_name("China East"), _normalize_region_name("China East 2"))

    async def test_collapses_case_and_whitespace_variants_async(self):
        canonical = _normalize_region_name("East US 2")
        for variant in ("east us 2", "EAST US 2", "  East US 2  ", "eastus2",
                        "east-us-2", "east_us_2", "East  US  2", "East-US_2"):
            self.assertEqual(_normalize_region_name(variant), canonical)

    async def test_handles_none_and_empty_async(self):
        self.assertEqual(_normalize_region_name(None), "")
        self.assertEqual(_normalize_region_name(""), "")
        self.assertEqual(_normalize_region_name("   "), "")

    async def test_is_idempotent_async(self):
        for raw in ("East US 2", "  East-US_2  ", "eastus2", "EAST US 2", ""):
            once = _normalize_region_name(raw)
            self.assertEqual(_normalize_region_name(once), once)


if __name__ == "__main__":
    unittest.main()
