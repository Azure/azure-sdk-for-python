# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
import test_config
import pytest
from typing import Callable, List, Mapping, Any

from azure.core.rest import HttpRequest
from _fault_injection_transport import FaultInjectionTransport, ERROR_WITH_COUNTER
from azure.cosmos.container import ContainerProxy
from test_excluded_locations import (L1, L2,
                                     TestDataType, set_test_data_type,
                                     get_test_data_with_expected_output)
from test_fault_injection_transport import TestFaultInjectionTransport
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID
SINGLE_PARTITION_CONTAINER_ID = CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID
SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID = CONFIG.TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID
L1_URL = CONFIG.local_host
L2_URL = L1_URL.replace("localhost", "127.0.0.1")
URL_TO_LOCATIONS = {
    L1_URL: L1,
    L2_URL: L2
}

set_test_data_type(TestDataType.ALL_TESTS)

def delete_all_items_by_partition_key_test_data() -> List[str]:
    client_only_output_data = [
        L1,   #0
        L2,   #1
        L1,   #3
        L1    #4
    ]
    client_and_request_output_data = [
        L2,   #0
        L2,   #1
        L2,   #2
        L1,   #3
        L1,   #4
        L1,   #5
        L1,   #6
        L1,   #7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

# The output data is the number of retries that happened with different timeout region cases
# [timeout L1, timeout L2]
def metadata_read_with_excluded_locations_test_data() -> List[str]:
    client_only_output_data = [
        [1, 0],   #0
        [0, 1],   #1
        [1, 0],   #3
        [1, 0]    #4
    ]
    client_and_request_output_data = [
        [0, 1],   #0
        [0, 1],   #1
        [0, 1],   #2
        [1, 0],   #3
        [1, 0],   #4
        [1, 0],   #5
        [1, 0],   #6
        [1, 0],   #7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def get_location(
        initialized_objects: Mapping[str, Any],
        url_to_locations: Mapping[str, str] = URL_TO_LOCATIONS) -> str:
    # get Request URL
    header = initialized_objects['client'].client_connection.last_response_headers
    request_url = header["_request"].url

    # verify
    location = ""
    for url in url_to_locations:
        if request_url.startswith(url):
            location = url_to_locations[url]
            break
    return location

@pytest.mark.unittest
@pytest.mark.cosmosEmulator
class TestExcludedLocationsEmulator:
    @pytest.mark.parametrize('test_data', delete_all_items_by_partition_key_test_data())
    def test_delete_all_items_by_partition_key(self: "TestExcludedLocationsEmulator", test_data: List[List[str]]):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_location = test_data

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # with two read regions
        custom_transport = FaultInjectionTransport()
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name=L1,
                second_region_name=L2,
                inner=inner,
                first_region_url=L1_URL,
                second_region_url=L2_URL,
            )
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        for multiple_write_locations in [True, False]:
            # Create client
            initialized_objects = TestFaultInjectionTransport.setup_method_with_custom_transport(
                custom_transport,
                default_endpoint=HOST,
                key=KEY,
                database_id=DATABASE_ID,
                container_id=SINGLE_PARTITION_CONTAINER_ID,
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations,
                multiple_write_locations=multiple_write_locations,
            )
            container: ContainerProxy = initialized_objects["col"]

            # create an item
            id_value: str = str(uuid.uuid4())
            document_definition = {'id': id_value, 'pk': id_value}
            container.create_item(body=document_definition)

            # API call: delete_all_items_by_partition_key
            if request_excluded_locations is None:
                container.delete_all_items_by_partition_key(id_value)
            else:
                container.delete_all_items_by_partition_key(id_value, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            actual_location = get_location(initialized_objects)
            if multiple_write_locations:
                assert actual_location == expected_location
            else:
                assert actual_location == L1

    @pytest.mark.parametrize('test_data', metadata_read_with_excluded_locations_test_data())
    def test_metadata_read_with_excluded_locations(self: "TestExcludedLocationsEmulator", test_data: List[List[str]]):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_counts = test_data
        target_urls = [L1_URL, L2_URL]
        expected_locations = [L2, L1]
        for target_url, expected_location, expected_count in zip(target_urls, expected_locations, expected_counts):
            # Inject topology transformation that would make Emulator look like a multiple write region account
            # with two read regions
            custom_transport = FaultInjectionTransport()
            is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
                    r: FaultInjectionTransport.predicate_is_database_account_call(r)
            emulator_as_multi_write_region_account_transformation = \
                lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                    first_region_name=L1,
                    second_region_name=L2,
                    inner=inner,
                    first_region_url=L1_URL,
                    second_region_url=L2_URL,
                )
            custom_transport.add_response_transformation(
                is_get_account_predicate,
                emulator_as_multi_write_region_account_transformation)

            # Inject rule to simulate request timeout in target region
            is_request_to_target_region: Callable[[HttpRequest], bool] = lambda \
                    r: (FaultInjectionTransport.predicate_targets_region(r, target_url) and
                        FaultInjectionTransport.predicate_is_resource_type(r, ResourceType.Collection) and
                        not FaultInjectionTransport.predicate_is_write_operation(r, target_url))
            fault_factory = lambda r: custom_transport.error_with_counter(
                CosmosHttpResponseError(
                    status_code=408,
                    message="Request Time Out Error.")
            )
            custom_transport.add_fault(is_request_to_target_region, fault_factory)

            # Create client
            initialized_objects = TestFaultInjectionTransport.setup_method_with_custom_transport(
                custom_transport,
                default_endpoint=HOST,
                key=KEY,
                database_id=DATABASE_ID,
                container_id=SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID,
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations,
                multiple_write_locations=True,
            )
            container: ContainerProxy = initialized_objects["col"]

            custom_transport.reset_counters()
            if request_excluded_locations is None:
                container.read()
            else:
                container.read(excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            actual_location = get_location(initialized_objects)
            assert actual_location == expected_location
            actual_count = custom_transport.counters[ERROR_WITH_COUNTER]
            assert actual_count == expected_count


if __name__ == "__main__":
    unittest.main()
