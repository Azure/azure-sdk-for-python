# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest
import unittest.mock
import logging
from typing import Mapping, Any

import pytest
from azure.cosmos import documents
from azure.cosmos._global_endpoint_manager import _GlobalEndpointManager
from azure.cosmos._service_request_retry_policy import ServiceRequestRetryPolicy

from azure.cosmos.documents import DatabaseAccount, _OperationType
from azure.cosmos.http_constants import ResourceType
from azure.cosmos._location_cache import LocationCache, _normalize_region_name
from azure.cosmos._request_object import RequestObject

default_endpoint = "https://default.documents.azure.com"
location1_name = "location1"
location2_name = "location2"
location3_name = "location3"
location4_name = "location4"
location1_endpoint = "https://location1.documents.azure.com"
location2_endpoint = "https://location2.documents.azure.com"
location3_endpoint = "https://location3.documents.azure.com"
location4_endpoint = "https://location4.documents.azure.com"
refresh_time_interval_in_ms = 1000


def create_database_account(enable_multiple_writable_locations):
    db_acc = DatabaseAccount()
    db_acc._WritableLocations = [{"name": location1_name, "databaseAccountEndpoint": location1_endpoint},
                                 {"name": location2_name, "databaseAccountEndpoint": location2_endpoint},
                                 {"name": location3_name, "databaseAccountEndpoint": location3_endpoint}]
    db_acc._ReadableLocations = [{"name": location1_name, "databaseAccountEndpoint": location1_endpoint},
                                 {"name": location2_name, "databaseAccountEndpoint": location2_endpoint},
                                 {"name": location4_name, "databaseAccountEndpoint": location4_endpoint}]
    db_acc._EnableMultipleWritableLocations = enable_multiple_writable_locations
    return db_acc


canonical_location1_name = "East US 2"
canonical_location2_name = "West US 3"
canonical_location3_name = "Central US"
canonical_location1_endpoint = "https://eastus2.documents.azure.com"
canonical_location2_endpoint = "https://westus3.documents.azure.com"
canonical_location3_endpoint = "https://centralus.documents.azure.com"


def create_database_account_with_canonical_regions(enable_multiple_writable_locations):
    db_acc = DatabaseAccount()
    db_acc._WritableLocations = [
        {"name": canonical_location1_name, "databaseAccountEndpoint": canonical_location1_endpoint},
        {"name": canonical_location2_name, "databaseAccountEndpoint": canonical_location2_endpoint},
    ]
    db_acc._ReadableLocations = [
        {"name": canonical_location1_name, "databaseAccountEndpoint": canonical_location1_endpoint},
        {"name": canonical_location2_name, "databaseAccountEndpoint": canonical_location2_endpoint},
    ]
    db_acc._EnableMultipleWritableLocations = enable_multiple_writable_locations
    return db_acc


def create_database_account_with_three_canonical_regions(enable_multiple_writable_locations):
    # Builds a three-region account for tests that need a longer preferred list.
    db_acc = DatabaseAccount()
    regions = [
        {"name": canonical_location1_name, "databaseAccountEndpoint": canonical_location1_endpoint},
        {"name": canonical_location2_name, "databaseAccountEndpoint": canonical_location2_endpoint},
        {"name": canonical_location3_name, "databaseAccountEndpoint": canonical_location3_endpoint},
    ]
    db_acc._WritableLocations = list(regions)
    db_acc._ReadableLocations = list(regions)
    db_acc._EnableMultipleWritableLocations = enable_multiple_writable_locations
    return db_acc


def refresh_location_cache(preferred_locations, use_multiple_write_locations, connection_policy=None):
    if connection_policy is None:
        connection_policy = documents.ConnectionPolicy()
    connection_policy.PreferredLocations = preferred_locations
    connection_policy.UseMultipleWriteLocations = use_multiple_write_locations
    lc = LocationCache(default_endpoint=default_endpoint,
                       connection_policy=connection_policy)
    return lc

@pytest.mark.cosmosEmulator
class TestLocationCache:

    def test_mark_endpoint_unavailable(self):
        lc = refresh_location_cache([], False)
        # mark unavailable for read
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, True)
        location1_info = lc.location_unavailability_info_by_endpoint[location1_endpoint]
        assert location1_info['operationType'] == {'Read'}

        # mark unavailable for write
        time.sleep(1)
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, False)
        location1_info = lc.location_unavailability_info_by_endpoint[location1_endpoint]
        assert location1_info['operationType'] == {'Read', 'Write'}

    def test_is_endpoint_unavailable(self):
        lc = refresh_location_cache([], False)
        assert lc.is_endpoint_unavailable(location1_endpoint, "Read") is False
        assert lc.is_endpoint_unavailable(location1_endpoint, "None") is False
        assert lc.is_endpoint_unavailable(location1_endpoint, "Write") is False
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, False)
        assert lc.is_endpoint_unavailable(location1_endpoint, "Read")
        assert lc.is_endpoint_unavailable(location1_endpoint, "None") is False
        assert lc.is_endpoint_unavailable(location1_endpoint, "Write") is False
        lc.mark_endpoint_unavailable_for_write(location2_endpoint, False)
        assert lc.is_endpoint_unavailable(location2_endpoint, "Read") is False
        assert lc.is_endpoint_unavailable(location2_endpoint, "None") is False
        assert lc.is_endpoint_unavailable(location2_endpoint, "Write")
        location1_info = lc.location_unavailability_info_by_endpoint[location1_endpoint]
        lc.location_unavailability_info_by_endpoint[location1_endpoint] = location1_info

    def test_endpoints_to_health_check(self):
        lc = refresh_location_cache([location4_name], False)
        db_acc = create_database_account(False)
        lc.perform_on_database_account_read(db_acc)

        # check endpoints to health check
        endpoints = lc.endpoints_to_health_check()
        assert len(endpoints) == 2
        assert location1_endpoint in endpoints
        assert location4_endpoint in endpoints

    def test_get_locations(self):
        lc = refresh_location_cache([], False)
        db_acc = create_database_account(False)
        lc.perform_on_database_account_read(db_acc)

        # check read endpoints without preferred locations
        read_regions = lc.get_read_regional_routing_contexts()
        assert len(read_regions) == 3
        assert read_regions[0].get_primary() == location1_endpoint

        # check read endpoints with preferred locations
        lc = refresh_location_cache([location1_name, location2_name, location4_name], False)
        lc.perform_on_database_account_read(db_acc)
        read_regions = lc.get_read_regional_routing_contexts()
        assert len(read_regions) == len(db_acc.ReadableLocations)
        for read_region in db_acc.ReadableLocations:
            found_endpoint = False
            endpoint = read_region['databaseAccountEndpoint']
            for region in read_regions:
                if endpoint == region.get_primary():
                    found_endpoint = True
            assert found_endpoint

        # check write endpoints
        write_regions = lc.get_write_regional_routing_contexts()
        assert len(write_regions) == len(db_acc.WritableLocations)
        for write_region in db_acc.WritableLocations:
            found_endpoint = False
            endpoint = write_region['databaseAccountEndpoint']
            for region in write_regions:
                if endpoint == region.get_primary():
                    found_endpoint = True
            assert found_endpoint

    def test_resolve_request_endpoint_preferred_regions(self):
        lc = refresh_location_cache([location1_name, location3_name, location4_name], True)
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)
        write_doc_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        read_doc_request = RequestObject(ResourceType.Document, _OperationType.Read, None)

        # resolve both document requests with all regions available
        write_doc_resolved = lc.resolve_service_endpoint(write_doc_request)
        read_doc_resolved = lc.resolve_service_endpoint(read_doc_request)
        assert write_doc_resolved == read_doc_resolved

        # mark main region unavailable and try again
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, True)
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, True)
        read_doc_resolved = lc.resolve_service_endpoint(read_doc_request)
        write_doc_resolved = lc.resolve_service_endpoint(write_doc_request)
        assert read_doc_resolved == location4_endpoint
        assert write_doc_resolved == location3_endpoint

        # mark next preferred region as unavailable - no preferred endpoints left
        lc.mark_endpoint_unavailable_for_read(location4_endpoint, True)
        lc.mark_endpoint_unavailable_for_write(location3_endpoint, True)
        read_resolved = lc.resolve_service_endpoint(read_doc_request)
        write_resolved = lc.resolve_service_endpoint(write_doc_request)
        # With the updated logic, we should retry the unavailable preferred locations
        # instead of falling back to the default endpoint.
        assert read_resolved == location1_endpoint
        assert write_resolved == location1_endpoint

    @pytest.mark.parametrize("test_type",["OnClient", "OnRequest", "OnBoth"])
    def test_get_applicable_regional_endpoints_excluded_regions(self, test_type):
        # Init test data
        if test_type == "OnClient":
            excluded_locations_on_client_list = [
                [location1_name],
                [location1_name, location2_name],
                [location1_name, location2_name, location3_name],
                [location4_name],
                [],
            ]
            excluded_locations_on_requests_list = [None] * 5
        elif test_type == "OnRequest":
            excluded_locations_on_client_list = [[]] * 5
            excluded_locations_on_requests_list = [
                [location1_name],
                [location1_name, location2_name],
                [location1_name, location2_name, location3_name],
                [location4_name],
                [],
            ]
        else:
            excluded_locations_on_client_list = [
                [location1_name],
                [location1_name, location2_name, location3_name],
                [location1_name, location2_name],
                [location2_name],
                [location1_name, location2_name, location3_name],
            ]
            excluded_locations_on_requests_list = [
                [location1_name],
                [location1_name, location2_name],
                [location1_name, location2_name, location3_name],
                [location4_name],
                [],
            ]

        expected_read_endpoints_list = [
            [location2_endpoint],
            [location1_endpoint],
            [location1_endpoint],
            [location1_endpoint, location2_endpoint],
            [location1_endpoint, location2_endpoint],
        ]
        expected_write_endpoints_list = [
            [location2_endpoint, location3_endpoint],
            [location3_endpoint],
            [default_endpoint],
            [location1_endpoint, location2_endpoint, location3_endpoint],
            [location1_endpoint, location2_endpoint, location3_endpoint],
        ]

        # Loop over each test cases
        for excluded_locations_on_client, excluded_locations_on_requests, expected_read_endpoints, expected_write_endpoints in zip(excluded_locations_on_client_list, excluded_locations_on_requests_list, expected_read_endpoints_list, expected_write_endpoints_list):
            # Init excluded_locations in ConnectionPolicy
            connection_policy = documents.ConnectionPolicy()
            connection_policy.ExcludedLocations = excluded_locations_on_client

            # Init location_cache
            location_cache = refresh_location_cache([location1_name, location2_name, location3_name], True,
                                                    connection_policy)
            database_account = create_database_account(True)
            location_cache.perform_on_database_account_read(database_account)

            # Init requests and set excluded regions on requests
            write_doc_request = RequestObject(ResourceType.Document, _OperationType.Create, {})
            write_doc_request.excluded_locations = excluded_locations_on_requests
            read_doc_request = RequestObject(ResourceType.Document, _OperationType.Read, {})
            read_doc_request.excluded_locations = excluded_locations_on_requests

            # Test if read endpoints were correctly filtered on client level
            read_regional_routing_contexts = location_cache._get_applicable_read_regional_routing_contexts(read_doc_request)
            read_doc_endpoint = [regional_routing_contexts.get_primary() for regional_routing_contexts in read_regional_routing_contexts]
            assert read_doc_endpoint == expected_read_endpoints

            # Test if write endpoints were correctly filtered on client level
            write_regional_routing_contexts = location_cache._get_applicable_write_regional_routing_contexts(write_doc_request)
            write_doc_endpoint = [regional_routing_contexts.get_primary() for regional_routing_contexts in write_regional_routing_contexts]
            assert write_doc_endpoint == expected_write_endpoints

    def test_set_excluded_locations_for_requests(self):
        # Init excluded_locations in ConnectionPolicy
        excluded_locations_on_client = [location1_name, location2_name]
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = excluded_locations_on_client

        # Init location_cache
        location_cache = refresh_location_cache([location1_name, location2_name, location3_name], True,
                                                connection_policy)
        database_account = create_database_account(True)
        location_cache.perform_on_database_account_read(database_account)

        # Test setting excluded locations
        excluded_locations = [location1_name]
        options: Mapping[str, Any] = {"excludedLocations": excluded_locations}

        expected_excluded_locations = excluded_locations
        read_doc_request = RequestObject(ResourceType.Document, _OperationType.Create, {})
        read_doc_request.set_excluded_location_from_options(options)
        actual_excluded_locations = read_doc_request.excluded_locations
        assert actual_excluded_locations == expected_excluded_locations

        expected_read_endpoints = [location2_endpoint]
        read_regional_routing_contexts = location_cache._get_applicable_read_regional_routing_contexts(read_doc_request)
        read_doc_endpoint = [regional_routing_contexts.get_primary() for regional_routing_contexts in read_regional_routing_contexts]
        assert read_doc_endpoint == expected_read_endpoints

        # Test setting excluded locations with None value
        expected_error_message = ("Excluded locations cannot be None. "
                                  "If you want to remove all excluded locations, try passing an empty list.")
        with pytest.raises(ValueError) as e:
            options: Mapping[str, Any] = {"excludedLocations": None}
            doc_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
            doc_request.set_excluded_location_from_options(options)
        assert str(
            e.value) == expected_error_message

    def test_resolve_endpoint_unavailable_and_excluded_preferred_regions(self):
        # Scenario: All preferred read locations are unavailable AND in the excluded list.
        # Expected: Fallback to the primary write region.
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = [location1_name, location4_name]
        lc = refresh_location_cache([location1_name, location4_name], True, connection_policy)
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)

        # Mark all preferred read locations as unavailable
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, True)
        lc.mark_endpoint_unavailable_for_read(location4_endpoint, True)

        # Create a read request
        read_doc_request = RequestObject(ResourceType.Document, _OperationType.Read, None)

        # Resolve the endpoint for the read request
        read_doc_resolved = lc.resolve_service_endpoint(read_doc_request)

        # All preferred read locations ([loc1, loc4]) are excluded.
        # The fallback for read is the primary write region, which is loc1.
        assert read_doc_resolved == location1_endpoint

        # Scenario: All preferred write locations are unavailable AND in the excluded list.
        # Expected: Fallback to the default endpoint.
        connection_policy.ExcludedLocations = [location1_name, location2_name]
        lc = refresh_location_cache([location1_name, location2_name], True, connection_policy)
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)

        # Mark preferred write locations as unavailable
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, True)
        lc.mark_endpoint_unavailable_for_write(location2_endpoint, True)

        # Create a write request
        write_doc_request = RequestObject(ResourceType.Document, _OperationType.Create, None)

        # Resolve the endpoint for the write request
        write_doc_resolved = lc.resolve_service_endpoint(write_doc_request)

        # All preferred write locations ([loc1, loc2]) are excluded.
        # The fallback for write is the default_endpoint.
        assert write_doc_resolved == default_endpoint

    def test_resolve_endpoint_unavailable_and_excluded_on_request(self):
        # Scenario: All preferred read locations are unavailable AND in the excluded list on the request.
        # Expected: Fallback to the primary write region.
        lc = refresh_location_cache([location1_name, location4_name], True)
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)

        # Mark all preferred read locations as unavailable
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, True)
        lc.mark_endpoint_unavailable_for_read(location4_endpoint, True)

        # Create a read request and set excluded locations
        read_doc_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_doc_request.excluded_locations = [location1_name, location4_name]

        # Resolve the endpoint for the read request
        read_doc_resolved = lc.resolve_service_endpoint(read_doc_request)

        # All preferred read locations ([loc1, loc4]) are excluded.
        # The fallback for read is the primary write region, which is loc1.
        assert read_doc_resolved == location1_endpoint

        # Scenario: All preferred write locations are unavailable AND in the excluded list on the request.
        # Expected: Fallback to the default endpoint.
        lc = refresh_location_cache([location1_name, location2_name], True)
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)

        # Mark preferred write locations as unavailable
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, True)
        lc.mark_endpoint_unavailable_for_write(location2_endpoint, True)

        # Create a write request and set excluded locations
        write_doc_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_doc_request.excluded_locations = [location1_name, location2_name]

        # Resolve the endpoint for the write request
        write_doc_resolved = lc.resolve_service_endpoint(write_doc_request)

        # All preferred write locations ([loc1, loc2]) are excluded.
        # The fallback for write is the default_endpoint.
        assert write_doc_resolved == default_endpoint

    def test_resolve_endpoint_respects_excluded_regions_when_use_preferred_locations_is_false(self):

        # 1. Setup: LocationCache with multiple locations enabled.
        lc = refresh_location_cache(preferred_locations=[], use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # 2. Create a write request.
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)

        # 3. Set use_preferred_locations to False and exclude the first write location.
        write_request.use_preferred_locations = False
        write_request.excluded_locations = [location1_name]

        # 4. Resolve the endpoint.
        # With the fix, the excluded_locations list is respected.
        # It should resolve to the next available write location, which is location2.
        resolved_endpoint = lc.resolve_service_endpoint(write_request)

        # 5. Assert the correct behavior for the write request.
        assert resolved_endpoint == location2_endpoint

        # 6. Repeat for a read request.
        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.use_preferred_locations = False
        read_request.excluded_locations = [location1_name]

        # It should resolve to the next available read location, which is location2.
        resolved_endpoint = lc.resolve_service_endpoint(read_request)

        # Assert the correct behavior.
        assert resolved_endpoint == location2_endpoint

    def test_regional_fallback_when_primary_is_excluded(self):
        # This test simulates a scenario where the primary preferred region is excluded
        # by the user, and the secondary is excluded by the circuit breaker.
        # The expected behavior is to fall back to the circuit-breaker-excluded region
        # as a last resort, instead of the global endpoint.

        # 1. Setup: LocationCache with two preferred write locations.
        preferred_locations = [location1_name, location2_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # 2. Create a write request.
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)

        # 3. Exclude the primary region by user and the secondary by circuit breaker.
        write_request.excluded_locations = [location1_name]
        write_request.excluded_locations_circuit_breaker = [location2_name]

        # 4. Resolve the endpoint.
        # the user-excluded location should be filtered out, and the
        # circuit-breaker-excluded location moved to the end of the list.
        # Since it's the only one left, it should be selected.
        resolved_endpoint = lc.resolve_service_endpoint(write_request)

        # 5. Assert that the resolved endpoint is the circuit-breaker-excluded one, not the global default.
        assert resolved_endpoint == location2_endpoint

    def test_write_fallback_to_global_after_regional_retries_exhausted(self):
        # This test simulates the client pipeline retrying preferred locations for writes
        # after all of them have been tried and marked as unavailable.

        # 1. Setup: LocationCache with two preferred write locations.
        preferred_locations = [location1_name, location2_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # Mock the GlobalEndpointManager to use our LocationCache and forward calls.
        mock_gem = unittest.mock.Mock()
        mock_gem.location_cache = lc
        # Simulate resolving to the next preferred location on the first retry.
        mock_gem.resolve_service_endpoint_for_partition.side_effect = [location2_endpoint]
        mock_gem.mark_endpoint_unavailable_for_write = lc.mark_endpoint_unavailable_for_write

        # Mock ConnectionPolicy and pk_range_wrapper
        mock_connection_policy = unittest.mock.Mock()
        mock_connection_policy.EnableEndpointDiscovery = True
        mock_pk_range_wrapper = unittest.mock.Mock()

        # 2. Initial Request: The client resolves the first endpoint.
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        resolved_endpoint = lc.resolve_service_endpoint(write_request)
        assert resolved_endpoint == location1_endpoint

        # 3. First Failure and Retry: The request to location1 fails. The retry policy is invoked.
        write_request.location_endpoint_to_route = location1_endpoint  # Simulate request was sent here
        retry_policy = ServiceRequestRetryPolicy(mock_connection_policy, mock_gem, mock_pk_range_wrapper, write_request)

        # The policy should decide to retry and route to the next endpoint (location2).
        should_retry = retry_policy.ShouldRetry()
        assert should_retry is True
        assert write_request.location_endpoint_to_route == location2_endpoint
        assert lc.is_endpoint_unavailable(location1_endpoint, "Write") is True

        # 4. Second Failure and Exhaustion: The request to location2 also fails.
        should_retry_again = retry_policy.ShouldRetry()

        # The policy has now exhausted all regional retries and should return False.
        assert should_retry_again is False
        assert lc.is_endpoint_unavailable(location2_endpoint, "Write") is True

        # 5. Fallback to Global: After the retry policy gives up, the client clears the regional
        # routing preference to make a final attempt at the global endpoint.
        write_request.clear_route_to_location()
        write_request.use_preferred_locations = False

        # A final call to resolve the endpoint should now return the first preferred location,
        # even though it's marked as unavailable, as a last resort.
        final_endpoint = lc.resolve_service_endpoint(write_request)
        assert final_endpoint == location1_endpoint

    def test_unavailable_endpoints_not_dropped_from_routing_list(self):
        """
        Unavailable endpoints should be appended to the end of the routing list,
        not dropped entirely.

        Scenario:
        - Customer has preferred_locations = ["East US", "West US 2"]
        - East US is marked unavailable for writes
        - Customer makes a request with excluded_locations = ["West US 2"]
        - Expected: East US should still be available as fallback (unavailable but in the list)
        """
        # Setup: Two preferred locations, multi-write enabled
        preferred_locations = [location1_name, location2_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # Verify initial state: Both locations are in write_regional_routing_contexts
        write_contexts = lc.get_write_regional_routing_contexts()
        assert len(write_contexts) == 2
        assert write_contexts[0].get_primary() == location1_endpoint
        assert write_contexts[1].get_primary() == location2_endpoint

        # Mark location1 (East US) as unavailable for writes
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")

        # After marking unavailable, the routing list should still contain
        # both endpoints - healthy ones first, unavailable ones at the end
        write_contexts_after = lc.get_write_regional_routing_contexts()
        assert len(write_contexts_after) == 2, \
            f"Expected 2 endpoints in routing list, got {len(write_contexts_after)}. " \
            "Unavailable endpoint was incorrectly dropped!"
        # location2 (healthy) should be first
        assert write_contexts_after[0].get_primary() == location2_endpoint
        # location1 (unavailable) should be at the end as fallback
        assert write_contexts_after[1].get_primary() == location1_endpoint

        # Now simulate the customer request with excluded_locations = ["location2"]
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.excluded_locations = [location2_name]

        # Resolve endpoint - should get location1 (unavailable) as the only remaining option
        # NOT the global default endpoint!
        resolved_endpoint = lc.resolve_service_endpoint(write_request)

        # Should fall back to location1 (unavailable regional endpoint)
        # NOT the global endpoint
        assert resolved_endpoint == location1_endpoint, \
            f"Expected {location1_endpoint} but got {resolved_endpoint}. " \
            f"Bug: Unavailable endpoint was dropped and SDK fell back to global endpoint!"

    def test_unavailable_endpoints_ordering_in_routing_list(self):
        """
        Test that healthy endpoints come before unavailable endpoints in the routing list.
        This ensures the SDK tries healthy regions first, but has unavailable ones as fallback.
        """
        # Setup: Three preferred locations
        preferred_locations = [location1_name, location2_name, location3_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # Mark location1 as unavailable
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")

        # Check ordering: location2, location3 (healthy) should come before location1 (unavailable)
        write_contexts = lc.get_write_regional_routing_contexts()
        assert len(write_contexts) == 3
        assert write_contexts[0].get_primary() == location2_endpoint  # First healthy
        assert write_contexts[1].get_primary() == location3_endpoint  # Second healthy
        assert write_contexts[2].get_primary() == location1_endpoint  # Unavailable at end

        # Mark location2 as unavailable too
        lc.mark_endpoint_unavailable_for_write(location2_endpoint, refresh_cache=True, context="test")

        # Check ordering: location3 (healthy) should come before location1, location2 (unavailable)
        write_contexts = lc.get_write_regional_routing_contexts()
        assert len(write_contexts) == 3
        assert write_contexts[0].get_primary() == location3_endpoint  # Only healthy
        # Unavailable ones at end, in original preferred order
        assert write_contexts[1].get_primary() == location1_endpoint
        assert write_contexts[2].get_primary() == location2_endpoint

    def test_update_location_cache_recalculates_from_account_data(self):
        """
        Verify that update_location_cache() recalculates routing contexts from the
        underlying account data (account_*_regional_routing_contexts_by_location),
        not from stale direct mutations to read/write_regional_routing_contexts.

        This documents the invariant that caused the retry test CI failures:
        if you mutate read_regional_routing_contexts directly without updating
        the source-of-truth attributes, a subsequent update_location_cache() call
        will overwrite your mutations.
        """
        preferred_locations = [location1_name, location2_name, location4_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=False)
        db_acc = create_database_account(enable_multiple_writable_locations=False)
        lc.perform_on_database_account_read(db_acc)

        # Capture the correctly-derived state
        original_read_contexts = list(lc.read_regional_routing_contexts)
        assert len(original_read_contexts) == 3  # location1, location2, location4

        # Simulate what the old tests did: directly mutate the derived list
        from azure.cosmos._location_cache import RegionalRoutingContext
        lc.read_regional_routing_contexts = [
            RegionalRoutingContext("https://fake1.documents.azure.com"),
            RegionalRoutingContext("https://fake2.documents.azure.com"),
            RegionalRoutingContext("https://fake3.documents.azure.com"),
        ]

        # Now call update_location_cache() with no new data (simulates health check completion)
        lc.update_location_cache()

        # The direct mutation should be overwritten — routing contexts recalculated from account data
        recalculated = lc.read_regional_routing_contexts
        assert len(recalculated) == len(original_read_contexts)
        for orig, context in zip(original_read_contexts, recalculated):
            assert orig.get_primary() == context.get_primary(), \
                "update_location_cache() should recalculate from account data, overwriting direct mutations"

    def test_update_location_cache_preserves_unavailability_marks(self):
        """
        Verify that mark_endpoint_unavailable() state survives subsequent
        update_location_cache() calls. Unavailable endpoints should be moved
        to the end of the routing list, not removed.
        """
        preferred_locations = [location1_name, location2_name, location3_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # Mark location1 as unavailable for reads
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=False)

        # Verify the unavailability is recorded
        assert lc.is_endpoint_unavailable(location1_endpoint, "Read")

        # Call update_location_cache() — simulates background health check completing
        lc.update_location_cache()

        # Unavailability info should persist (it lives in location_unavailability_info_by_endpoint)
        assert lc.is_endpoint_unavailable(location1_endpoint, "Read"), \
            "Unavailability marks should survive update_location_cache() calls"

        # The unavailable endpoint should be moved to the end of the read routing list
        read_contexts = lc.get_read_regional_routing_contexts()
        read_endpoints = [ctx.get_primary() for ctx in read_contexts]
        assert location1_endpoint in read_endpoints, "Unavailable endpoint should still be in routing list"
        assert read_endpoints[-1] == location1_endpoint, \
            "Unavailable endpoint should be at the end of routing list"
        assert read_endpoints[0] == location2_endpoint, \
            "First healthy preferred endpoint should be first"

    def test_location_cache_derived_state_consistency(self):
        """
        Verify that update_location_cache() is idempotent and that the derived
        state (read/write_regional_routing_contexts) matches what
        get_preferred_regional_routing_contexts() would return independently.
        """
        preferred_locations = [location1_name, location2_name, location4_name]
        lc = refresh_location_cache(preferred_locations, use_multiple_write_locations=True)
        db_acc = create_database_account(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # Snapshot after first update
        read_after_first = [ctx.get_primary() for ctx in lc.read_regional_routing_contexts]
        write_after_first = [ctx.get_primary() for ctx in lc.write_regional_routing_contexts]

        # Call update_location_cache() again with no new data — should be idempotent
        lc.update_location_cache()

        read_after_second = [ctx.get_primary() for ctx in lc.read_regional_routing_contexts]
        write_after_second = [ctx.get_primary() for ctx in lc.write_regional_routing_contexts]

        assert read_after_first == read_after_second, \
            "update_location_cache() should be idempotent for read routing contexts"
        assert write_after_first == write_after_second, \
            "update_location_cache() should be idempotent for write routing contexts"

        # Verify derived state matches what get_preferred_regional_routing_contexts returns directly
        from azure.cosmos._location_cache import EndpointOperationType
        expected_read = lc.get_preferred_regional_routing_contexts(
            lc.account_read_regional_routing_contexts_by_location,
            lc.account_read_locations,
            EndpointOperationType.ReadType,
            lc.write_regional_routing_contexts[0]
        )
        expected_write = lc.get_preferred_regional_routing_contexts(
            lc.account_write_regional_routing_contexts_by_location,
            lc.account_write_locations,
            EndpointOperationType.WriteType,
            lc.default_regional_routing_context
        )

        assert read_after_second == [ctx.get_primary() for ctx in expected_read]
        assert write_after_second == [ctx.get_primary() for ctx in expected_write]

    def test_resolve_endpoint_without_preferred_locations_supports_normalized_exclusions(self):
        # This specifically exercises _resolve_endpoint_without_preferred_locations by
        # setting use_preferred_locations=False.
        lc = refresh_location_cache(
            preferred_locations=[],
            use_multiple_write_locations=True,
        )
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.use_preferred_locations = False
        write_request.excluded_locations = ["east-us-2"]

        assert lc.resolve_service_endpoint(write_request) == canonical_location2_endpoint

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.use_preferred_locations = False
        read_request.excluded_locations = ["west_us_3"]

        assert lc.resolve_service_endpoint(read_request) == canonical_location1_endpoint

    def test_preferred_locations_support_normalized_region_names(self, caplog):
        # Preferred locations should match account region names even when the
        # caller uses different case, spacing, hyphens, or underscores. No
        # mismatch warning should appear when every entry matches a real region.
        with caplog.at_level(logging.WARNING):
            lc = refresh_location_cache(["east-us-2", " west_us_3 "], True)
            db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
            lc.perform_on_database_account_read(db_acc)

        assert not [r for r in caplog.records if "did not match" in r.getMessage()]

        write_contexts = lc.get_write_regional_routing_contexts()
        read_contexts = lc.get_read_regional_routing_contexts()

        assert write_contexts[0].get_primary() == canonical_location1_endpoint
        assert write_contexts[1].get_primary() == canonical_location2_endpoint
        assert read_contexts[0].get_primary() == canonical_location1_endpoint
        assert read_contexts[1].get_primary() == canonical_location2_endpoint

    def test_excluded_locations_support_normalized_region_names(self, caplog):
        # Excluded locations should filter regions even when the caller spells
        # them with different case, spacing, hyphens, or underscores. No
        # mismatch warning should appear when every entry matches a real region.
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = ["east-us-2"]

        with caplog.at_level(logging.WARNING):
            lc = refresh_location_cache([canonical_location1_name, canonical_location2_name], True, connection_policy)
            db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
            lc.perform_on_database_account_read(db_acc)

        assert not [r for r in caplog.records if "did not match" in r.getMessage()]

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.excluded_locations = ["west_us_3"]

        assert lc.resolve_service_endpoint(read_request) == canonical_location2_endpoint
        assert lc.resolve_service_endpoint(write_request) == canonical_location1_endpoint

    def test_should_refresh_endpoints_handles_normalized_preferred_region(self):
        # should_refresh_endpoints must match canonical region keys even when the
        # customer's preferred location uses non-canonical spelling.
        lc = refresh_location_cache(["east-us-2"], True)
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        # Most-preferred is already the primary; no background refresh should be triggered.
        assert lc.should_refresh_endpoints() is False

    def test_should_refresh_endpoints_returns_true_for_normalized_non_primary(self):
        # When the caller's most preferred region (spelled with a hyphen here)
        # is no longer the primary because its endpoint was marked unavailable,
        # should_refresh_endpoints must return True so a refresh runs.
        lc = refresh_location_cache(["east-us-2", "west-us-3"], True)
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)
        lc.mark_endpoint_unavailable_for_read(canonical_location1_endpoint, refresh_cache=True)

        # Sanity: primary is now West US 3, but most-preferred still normalizes to East US 2.
        assert lc.read_regional_routing_contexts[0].get_primary() == canonical_location2_endpoint
        assert lc.should_refresh_endpoints() is True

    def test_get_locational_endpoint_normalizes_customer_region_string(self):
        # The static helper builds a region-specific URL from the account host.
        # Any spelling variant of the same region should produce the same URL.
        default_endpoint_url = "https://contoso.documents.azure.com:443/"
        expected_endpoint = "https://contoso-eastus2.documents.azure.com:443/"

        for region_input in ("East US 2", "east us 2", "eastus2", "east-us-2", "east_us_2", " EastUs2 "):
            assert LocationCache.GetLocationalEndpoint(default_endpoint_url, region_input) == expected_endpoint

    def test_unmatched_excluded_locations_warning_is_deduped(self, caplog):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = ["unknown-region"]
        lc = refresh_location_cache([canonical_location1_name], True, connection_policy)
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        with caplog.at_level("WARNING", logger="azure.cosmos.LocationCache"):
            lc.perform_on_database_account_read(db_acc)
            request = RequestObject(ResourceType.Document, _OperationType.Read, None)
            lc.resolve_service_endpoint(request)
            lc.resolve_service_endpoint(request)
            # Simulate a periodic refresh with unchanged topology and config.
            lc.perform_on_database_account_read(db_acc)

        unmatched_logs = [
            record for record in caplog.records
            if "Ignoring excluded_locations entries" in record.getMessage()
        ]
        assert len(unmatched_logs) == 1

    def test_unmatched_preferred_locations_warning_is_deduped(self, caplog):
        with caplog.at_level("WARNING", logger="azure.cosmos.LocationCache"):
            lc = refresh_location_cache(["unknown-region"], True)
            db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
            lc.perform_on_database_account_read(db_acc)
            # Simulate a periodic refresh with unchanged topology and config.
            lc.perform_on_database_account_read(db_acc)

        unmatched_logs = [
            record for record in caplog.records
            if "Ignoring preferred_locations entries" in record.getMessage()
        ]
        assert len(unmatched_logs) == 1

    def test_excluded_locations_ignore_none_and_empty_entries(self):
        # None, empty, and whitespace-only entries in excluded_locations should
        # be ignored. They must not accidentally match real endpoints and they
        # must not block the valid entries from filtering correctly.
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = [None, "", "  ", "east-us-2"]  # type: ignore[list-item]

        lc = refresh_location_cache(
            [canonical_location1_name, canonical_location2_name], True, connection_policy
        )
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        # Mixed garbage on the request-level excluded list too.
        write_request.excluded_locations = [None, "", "west_us_3"]  # type: ignore[list-item]

        # East US 2 is excluded by the client list → reads route to the other region.
        assert lc.resolve_service_endpoint(read_request) == canonical_location2_endpoint
        # West US 3 is excluded on the request → writes route to East US 2.
        assert lc.resolve_service_endpoint(write_request) == canonical_location1_endpoint

    def test_preferred_locations_handle_uppercase_and_pascalcase_variants(self):
        # The caller may spell preferred regions in all caps or PascalCase.
        # Both should resolve to the same canonical endpoints.
        lc = refresh_location_cache(["EAST US 2", "WestUs3"], True)
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        write_contexts = lc.get_write_regional_routing_contexts()
        read_contexts = lc.get_read_regional_routing_contexts()
        assert write_contexts[0].get_primary() == canonical_location1_endpoint
        assert write_contexts[1].get_primary() == canonical_location2_endpoint
        assert read_contexts[0].get_primary() == canonical_location1_endpoint
        assert read_contexts[1].get_primary() == canonical_location2_endpoint

    def test_excluded_locations_handle_uppercase_and_mixed_punctuation(self):
        # Client-level and per-request excluded entries that mix uppercase and
        # different separators should still filter the right regions.
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = ["EAST-US_2"]
        lc = refresh_location_cache(
            [canonical_location1_name, canonical_location2_name], True, connection_policy,
        )
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_request.excluded_locations = ["WEST-US_3"]

        assert lc.resolve_service_endpoint(read_request) == canonical_location2_endpoint
        assert lc.resolve_service_endpoint(write_request) == canonical_location1_endpoint

    def test_duplicate_normalized_entries_in_excluded_list_warn_once(self, caplog):
        # When the same region is listed twice in different spellings, the
        # filter should still work and no duplicate mismatch warning should fire.
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ExcludedLocations = ["East US 2", "east-us-2", "EAST_US_2"]
        lc = refresh_location_cache(
            [canonical_location1_name, canonical_location2_name], True, connection_policy,
        )
        db_acc = create_database_account_with_canonical_regions(enable_multiple_writable_locations=True)

        with caplog.at_level("WARNING", logger="azure.cosmos.LocationCache"):
            lc.perform_on_database_account_read(db_acc)
            read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
            resolved = lc.resolve_service_endpoint(read_request)

        assert resolved == canonical_location2_endpoint
        mismatch_warnings = [
            r for r in caplog.records if "did not match" in r.getMessage()
        ]
        assert mismatch_warnings == []

    def test_preferred_locations_mix_normalized_and_canonical_forms(self):
        # A three-region preferred list that mixes canonical and messy spellings
        # should map every entry to the right account region in the right order.
        lc = refresh_location_cache(
            ["east-us-2", "WestUs3", "  central us  "], True,
        )
        db_acc = create_database_account_with_three_canonical_regions(enable_multiple_writable_locations=True)
        lc.perform_on_database_account_read(db_acc)

        write_endpoints = [ctx.get_primary() for ctx in lc.get_write_regional_routing_contexts()]
        read_endpoints = [ctx.get_primary() for ctx in lc.get_read_regional_routing_contexts()]
        expected = [
            canonical_location1_endpoint,
            canonical_location2_endpoint,
            canonical_location3_endpoint,
        ]
        assert write_endpoints == expected
        assert read_endpoints == expected

    def test_global_endpoint_manager_normalizes_preferred_locations_from_policy(self):
        # End-to-end check that messy region names set on ConnectionPolicy flow
        # through the endpoint manager into the location cache and resolve correctly.
        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = ["east-us-2", " WEST_US_3 "]
        cp.UseMultipleWriteLocations = True

        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _GlobalEndpointManager(mock_client)
        gem.location_cache.perform_on_database_account_read(
            create_database_account_with_canonical_regions(enable_multiple_writable_locations=True),
        )

        read_endpoints = [
            ctx.get_primary() for ctx in gem.location_cache.get_read_regional_routing_contexts()
        ]
        assert read_endpoints == [canonical_location1_endpoint, canonical_location2_endpoint]

    """
    Additional sync coverage for keeping unavailable endpoints as
    fallback options. Covers the global-endpoint-manager wrapper,
    single-write accounts, the health-check probe set, ordering,
    circuit-breaker fallback, recovery, and account-refresh preservation.
    """

    def test_sync_global_endpoint_manager_returns_unavailable_as_last_resort(self):
        # Sync wrapper around LocationCache should also keep an unavailable
        # endpoint at the tail of the routing list so it can be used as fallback.
        cp = documents.ConnectionPolicy()
        cp.PreferredLocations = [location1_name, location2_name]
        cp.UseMultipleWriteLocations = True
        mock_client = unittest.mock.Mock()
        mock_client.connection_policy = cp
        mock_client.url_connection = default_endpoint

        gem = _GlobalEndpointManager(mock_client)
        gem.location_cache.perform_on_database_account_read(create_database_account(True))

        # Mark location1 unavailable for both reads and writes.
        gem.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True, context="test")
        gem.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_ctxs = gem.get_applicable_read_regional_routing_contexts(read_request)
        assert [c.get_primary() for c in read_ctxs] == [location2_endpoint, location1_endpoint], \
            "Sync GEM should keep unavailable read endpoint at the tail, not drop it."

        # If the only healthy region is excluded, the unavailable region
        # should still be returned by the sync wrapper, not the global default.
        read_request.excluded_locations = [location2_name]
        assert gem._resolve_service_endpoint(read_request) == location1_endpoint

        write_request = RequestObject(ResourceType.Document, _OperationType.Create, None)
        write_ctxs = gem.get_applicable_write_regional_routing_contexts(write_request)
        assert [c.get_primary() for c in write_ctxs] == [location2_endpoint, location1_endpoint]

        write_request.excluded_locations = [location2_name]
        assert gem._resolve_service_endpoint(write_request) == location1_endpoint

    def test_sync_single_write_account_read_unavailable_and_excluded(self):
        # On a single-write account, an excluded healthy region should still
        # fall back to the unavailable preferred region rather than the global default.
        lc = refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=False
        )
        lc.perform_on_database_account_read(create_database_account(False))
        assert lc.can_use_multiple_write_locations() is False, \
            "Test setup must be a single-write account."

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.excluded_locations = [location2_name]

        resolved = lc.resolve_service_endpoint(read_request)
        assert resolved == location1_endpoint, \
            "Single-write read path returned the global default instead of " \
            "the unavailable preferred region."

    def test_sync_health_check_set_includes_unavailable_endpoints(self):
        # Unavailable read endpoints must remain in the health-check probe set so
        # they can be re-marked available once the prober finds them healthy.
        # First mark location1 write-unavailable so it is no longer the primary
        # write probe endpoint; this isolates the read-unavailable assertion from
        # write-endpoint inclusion.
        lc = refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True
        )
        lc.perform_on_database_account_read(create_database_account(True))
        lc.mark_endpoint_unavailable_for_write(
            location1_endpoint, refresh_cache=True, context="test"
        )
        assert lc.get_write_regional_routing_contexts()[0].get_primary() == location2_endpoint, \
            "Test precondition failed: location1 must not be the primary write endpoint."

        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)
        endpoints = lc.endpoints_to_health_check()
        assert location1_endpoint in endpoints, \
            "Health-check probe set is missing the unavailable read endpoint."
        assert location2_endpoint in endpoints

    @pytest.mark.parametrize("unavailable", [[], [location1_name], [location1_name, location2_name]])
    def test_sync_routing_list_has_no_duplicate_endpoints(self, unavailable):
        # The routing list should never contain the same endpoint twice,
        # regardless of how many regions are marked unavailable.
        endpoint_by_loc = {location1_name: location1_endpoint, location2_name: location2_endpoint}
        lc = refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True
        )
        lc.perform_on_database_account_read(create_database_account(True))

        for loc in unavailable:
            lc.mark_endpoint_unavailable_for_read(endpoint_by_loc[loc], refresh_cache=True)
        read_primaries = [c.get_primary() for c in lc.get_read_regional_routing_contexts()]
        assert len(read_primaries) == len(set(read_primaries)), \
            f"Read routing list has duplicates: {read_primaries}"
        assert set(read_primaries) == {location1_endpoint, location2_endpoint}

        for loc in unavailable:
            lc.mark_endpoint_unavailable_for_write(
                endpoint_by_loc[loc], refresh_cache=True, context="test"
            )
        write_primaries = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
        assert len(write_primaries) == len(set(write_primaries)), \
            f"Write routing list has duplicates: {write_primaries}"
        assert set(write_primaries) == {location1_endpoint, location2_endpoint}

    def test_mark_endpoint_available_restores_head_position(self):
        # After recovery, a previously-unavailable preferred endpoint should
        # return to the head of the routing list, not stay at the tail.
        lc = refresh_location_cache(
            [location1_name, location2_name, location3_name],
            use_multiple_write_locations=True,
        )
        lc.perform_on_database_account_read(create_database_account(True))

        # Initial state: most-preferred is location1.
        assert lc.read_regional_routing_contexts[0].get_primary() == location1_endpoint
        assert lc.write_regional_routing_contexts[0].get_primary() == location1_endpoint

        # Mark location1 unavailable for both lanes — it should slide to the tail.
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, refresh_cache=True)
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")
        assert lc.read_regional_routing_contexts[-1].get_primary() == location1_endpoint
        assert lc.write_regional_routing_contexts[-1].get_primary() == location1_endpoint

        # Simulate the health-probe rehabilitating the endpoint.
        lc.mark_endpoint_available(location1_endpoint)
        lc.update_location_cache()

        assert lc.is_endpoint_unavailable(location1_endpoint, "Read") is False
        assert lc.is_endpoint_unavailable(location1_endpoint, "Write") is False
        assert lc.read_regional_routing_contexts[0].get_primary() == location1_endpoint, \
            "Recovered endpoint should return to the head of the read routing list."
        assert lc.write_regional_routing_contexts[0].get_primary() == location1_endpoint, \
            "Recovered endpoint should return to the head of the write routing list."

    def test_account_topology_refresh_preserves_unavailability_tail_order(self):
        # A periodic account-topology refresh must not drop endpoints that
        # were marked unavailable, and the tail ordering must be preserved.
        lc = refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True
        )
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)

        # Mark location1 unavailable for writes — it should move to the tail.
        lc.mark_endpoint_unavailable_for_write(location1_endpoint, refresh_cache=True, context="test")
        write_primaries_before = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
        assert write_primaries_before == [location2_endpoint, location1_endpoint]

        # Simulate a periodic background refresh — the same topology comes back.
        lc.perform_on_database_account_read(db_acc)

        # The unavailability mark must survive, AND the routing list must
        # still contain location1 (as the tail), not drop it.
        assert lc.is_endpoint_unavailable(location1_endpoint, "Write"), \
            "Unavailability mark must survive an account-topology refresh."
        write_primaries_after = [c.get_primary() for c in lc.get_write_regional_routing_contexts()]
        assert write_primaries_after == write_primaries_before, \
            "Account-topology refresh dropped the unavailable endpoint from the routing list."

    def test_circuit_breaker_excluded_read_falls_back_before_global_default(self):
        # With the only healthy region user-excluded and the other region
        # circuit-breaker-excluded, reads should still resolve to the
        # circuit-breaker-excluded region instead of the global default.
        lc = refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True
        )
        lc.perform_on_database_account_read(create_database_account(True))

        read_request = RequestObject(ResourceType.Document, _OperationType.Read, None)
        read_request.excluded_locations = [location1_name]
        read_request.excluded_locations_circuit_breaker = [location2_name]

        resolved = lc.resolve_service_endpoint(read_request)
        assert resolved == location2_endpoint, \
            "Read should fall back to the circuit-breaker-excluded region " \
            "instead of dropping to the global default."

    def test_master_resource_appends_user_excluded_to_tail(self):
        # For master/metadata requests, user-excluded locations should be
        # appended to the tail so the request still has a chance to succeed.
        lc = refresh_location_cache(
            [location1_name, location2_name], use_multiple_write_locations=True
        )
        lc.perform_on_database_account_read(create_database_account(True))

        # Both regions healthy and both user-excluded — for a metadata request,
        # the SDK must still try them as a last resort.
        master_request = RequestObject(ResourceType.Database, _OperationType.Read, None)
        master_request.excluded_locations = [location1_name, location2_name]

        applicable = lc._get_applicable_read_regional_routing_contexts(master_request)
        primaries = [c.get_primary() for c in applicable]
        # The fix preserves user-excluded regions as a tail fallback for
        # master requests; both location1 and location2 should appear.
        assert location1_endpoint in primaries
        assert location2_endpoint in primaries
        # And neither should be the global default.
        assert default_endpoint not in primaries


class TestNormalizeRegionName:
    """Unit tests for the _normalize_region_name helper.

    The helper must accept cosmetic differences (case, spacing, hyphens,
    underscores) but never collapse two genuinely different regions like
    "East US" and "East US 2".
    """

    # Distinct regions must stay distinct after normalization.
    def test_does_not_collapse_prefix_sharing_regions(self):
        assert _normalize_region_name("East US") != _normalize_region_name("East US 2")
        assert _normalize_region_name("West US") != _normalize_region_name("West US 2")
        assert _normalize_region_name("West US") != _normalize_region_name("West US 3")
        assert _normalize_region_name("Central US") != _normalize_region_name("North Central US")
        assert _normalize_region_name("Central US") != _normalize_region_name("South Central US")
        assert _normalize_region_name("China East") != _normalize_region_name("China East 2")

    # Cosmetic differences should collapse to the same canonical form.
    def test_collapses_case_and_whitespace_variants(self):
        canonical = _normalize_region_name("East US 2")
        assert _normalize_region_name("east us 2") == canonical
        assert _normalize_region_name("EAST US 2") == canonical
        assert _normalize_region_name("  East US 2  ") == canonical
        assert _normalize_region_name("eastus2") == canonical
        assert _normalize_region_name("east-us-2") == canonical
        assert _normalize_region_name("east_us_2") == canonical
        # Extra internal whitespace and mixed punctuation should also collapse.
        assert _normalize_region_name("East  US  2") == canonical
        assert _normalize_region_name("East-US_2") == canonical
        assert _normalize_region_name("east -_ us -_ 2") == canonical

    def test_handles_none_and_empty(self):
        assert _normalize_region_name(None) == ""
        assert _normalize_region_name("") == ""
        assert _normalize_region_name("   ") == ""

    # Calling the helper on its own output should be a no-op.
    def test_is_idempotent(self):
        for raw in ("East US 2", "  East-US_2  ", "eastus2", "EAST US 2", ""):
            once = _normalize_region_name(raw)
            assert _normalize_region_name(once) == once


if __name__ == "__main__":
    unittest.main()
