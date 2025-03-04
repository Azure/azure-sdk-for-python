# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest

import pytest

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


def refresh_location_cache(preferred_locations, use_multiple_write_locations):
    lc = LocationCache(preferred_locations=preferred_locations,
                       default_endpoint=default_endpoint,
                       enable_endpoint_discovery=True,
                       use_multiple_write_locations=use_multiple_write_locations)
    return lc

@pytest.mark.cosmosEmulator
class TestLocationCache(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
