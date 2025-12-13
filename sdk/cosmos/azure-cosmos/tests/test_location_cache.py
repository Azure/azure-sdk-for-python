# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest
import unittest.mock
from typing import Mapping, Any

import pytest
from azure.cosmos import documents
from azure.cosmos._service_request_retry_policy import ServiceRequestRetryPolicy

from azure.cosmos.documents import DatabaseAccount, _OperationType
from azure.cosmos.http_constants import ResourceType
from azure.cosmos._location_cache import LocationCache
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


def refresh_location_cache(preferred_locations, use_multiple_write_locations, connection_policy=documents.ConnectionPolicy()):
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

if __name__ == "__main__":
    unittest.main()
