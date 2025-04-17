# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest
from typing import Mapping, Any

import pytest
from azure.cosmos import documents

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
        assert lc.is_endpoint_unavailable_internal(location1_endpoint, "Read") is False
        assert lc.is_endpoint_unavailable_internal(location1_endpoint, "None") is False
        assert lc.is_endpoint_unavailable_internal(location1_endpoint, "Write") is False
        lc.mark_endpoint_unavailable_for_read(location1_endpoint, False)
        assert lc.is_endpoint_unavailable_internal(location1_endpoint, "Read")
        assert lc.is_endpoint_unavailable_internal(location1_endpoint, "None") is False
        assert lc.is_endpoint_unavailable_internal(location1_endpoint, "Write") is False
        lc.mark_endpoint_unavailable_for_write(location2_endpoint, False)
        assert lc.is_endpoint_unavailable_internal(location2_endpoint, "Read") is False
        assert lc.is_endpoint_unavailable_internal(location2_endpoint, "None") is False
        assert lc.is_endpoint_unavailable_internal(location2_endpoint, "Write")
        location1_info = lc.location_unavailability_info_by_endpoint[location1_endpoint]
        lc.location_unavailability_info_by_endpoint[location1_endpoint] = location1_info

    def test_get_locations(self):
        lc = refresh_location_cache([], False)
        db_acc = create_database_account(False)
        lc.perform_on_database_account_read(db_acc)

        # check read endpoints without preferred locations
        read_regions = lc.get_read_regional_routing_contexts()
        assert len(read_regions) == 1
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
                if endpoint in (region.get_primary(), region.get_alternate()):
                    found_endpoint = True
            assert found_endpoint

        # check write endpoints
        write_regions = lc.get_write_regional_routing_contexts()
        assert len(write_regions) == len(db_acc.WritableLocations)
        for write_region in db_acc.WritableLocations:
            found_endpoint = False
            endpoint = write_region['databaseAccountEndpoint']
            for region in write_regions:
                if endpoint in (region.get_primary(), region.get_alternate()):
                    found_endpoint = True
            assert found_endpoint

    def test_resolve_request_endpoint_preferred_regions(self):
        lc = refresh_location_cache([location1_name, location3_name, location4_name], True)
        db_acc = create_database_account(True)
        lc.perform_on_database_account_read(db_acc)
        write_doc_request = RequestObject(ResourceType.Document, _OperationType.Create)
        read_doc_request = RequestObject(ResourceType.Document, _OperationType.Read)

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
        assert read_resolved == write_resolved
        assert read_resolved == default_endpoint

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
            write_doc_request = RequestObject(ResourceType.Document, _OperationType.Create)
            write_doc_request.excluded_locations = excluded_locations_on_requests
            read_doc_request = RequestObject(ResourceType.Document, _OperationType.Read)
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
        read_doc_request = RequestObject(ResourceType.Document, _OperationType.Create)
        read_doc_request.set_excluded_location_from_options(options)
        actual_excluded_locations = read_doc_request.excluded_locations
        assert actual_excluded_locations == expected_excluded_locations

        expected_read_endpoints = [location2_endpoint]
        read_regional_routing_contexts = location_cache._get_applicable_read_regional_routing_contexts(read_doc_request)
        read_doc_endpoint = [regional_routing_contexts.get_primary() for regional_routing_contexts in read_regional_routing_contexts]
        assert read_doc_endpoint == expected_read_endpoints


        # Test setting excluded locations with invalid resource types
        expected_excluded_locations = None
        for resource_type in [ResourceType.Offer, ResourceType.Conflict]:
            options: Mapping[str, Any] = {"excludedLocations": [location1_name]}
            read_doc_request = RequestObject(resource_type, _OperationType.Create)
            read_doc_request.set_excluded_location_from_options(options)
            actual_excluded_locations = read_doc_request.excluded_locations
            assert actual_excluded_locations == expected_excluded_locations

            expected_read_endpoints = [location1_endpoint]
            read_regional_routing_contexts = location_cache._get_applicable_read_regional_routing_contexts(read_doc_request)
            read_doc_endpoint = [regional_routing_contexts.get_primary() for regional_routing_contexts in read_regional_routing_contexts]
            assert read_doc_endpoint == expected_read_endpoints



        # Test setting excluded locations with None value
        expected_error_message = ("Excluded locations cannot be None. "
                                  "If you want to remove all excluded locations, try passing an empty list.")
        with pytest.raises(ValueError) as e:
            options: Mapping[str, Any] = {"excludedLocations": None}
            doc_request = RequestObject(ResourceType.Document, _OperationType.Create)
            doc_request.set_excluded_location_from_options(options)
        assert str(
            e.value) == expected_error_message


if __name__ == "__main__":
    unittest.main()
