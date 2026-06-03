# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async-context tests for the LocationCache fallback behavior when a
preferred region is marked unavailable. Drives the same invariants the
sync tests cover, but from inside coroutines so any event-loop
interaction with the shared cache shows up. Also drives the async
endpoint manager wrapper and the retry policy through the full
retry-then-fallback sequence. All tests use mocks; no live account."""

import unittest
import unittest.mock

import pytest

from azure.cosmos import documents
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType
from azure.cosmos._location_cache import LocationCache
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
        from azure.cosmos.aio._global_endpoint_manager_async import _GlobalEndpointManager

        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = [location1_name, location2_name]
        cp.UseMultipleWriteLocations = True
        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _GlobalEndpointManager(mock_client)
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

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)
        endpoints = lc.endpoints_to_health_check()
        self.assertIn(
            location1_endpoint, endpoints,
            "Health-check probe set is missing the unavailable read endpoint.",
        )
        self.assertIn(location2_endpoint, endpoints)

    async def test_async_master_resource_prefers_healthy_excluded_over_unavailable(self):
        """For a metadata (master-resource) request, a healthy region
        that is user-excluded should still be preferred over an
        unavailable non-excluded one. excluded_locations is a soft
        preference for metadata, not a hard filter."""
        lc = _refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(_create_database_account(True))

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)

        master_request = RequestObject(ResourceType.Database, _OperationType.Read, None)
        master_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(master_request)
        self.assertEqual(
            resolved, location2_endpoint,
            f"Expected {location2_endpoint} (healthy, user-excluded) but got "
            f"{resolved}.",
        )

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

    async def test_async_data_call_with_exclusion_and_unavailable_preserves_pr45200(self):
        """For a data request, excluded_locations is a hard filter.
        With one region unavailable and the other excluded, the SDK
        should still return the unavailable non-excluded region before
        falling back to the global default."""
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


if __name__ == "__main__":
    unittest.main()

