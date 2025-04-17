# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
import test_config
import pytest
from typing import Callable, List, Mapping, Any

from azure.core.pipeline.transport import AioHttpTransport
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos.aio._container import ContainerProxy
from test_excluded_locations import L1, L2, CLIENT_ONLY_TEST_DATA, CLIENT_AND_REQUEST_TEST_DATA
from test_excluded_locations_emulator import L1_URL, L2_URL, get_location
from test_fault_injection_transport_async import TestFaultInjectionTransportAsync

CONFIG = test_config.TestConfig()

ALL_INPUT_TEST_DATA = CLIENT_ONLY_TEST_DATA + CLIENT_AND_REQUEST_TEST_DATA

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
    all_output_test_data = client_only_output_data + client_and_request_output_data

    all_test_data = [input_data + [output_data] for input_data, output_data in zip(ALL_INPUT_TEST_DATA, all_output_test_data)]
    return all_test_data

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestExcludedLocationsEmulatorAsync:
    @pytest.mark.parametrize('test_data', delete_all_items_by_partition_key_test_data())
    async def test_delete_all_items_by_partition_key(self: "TestExcludedLocationsEmulatorAsync", test_data: List[List[str]]):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_location = test_data

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # with two read regions
        custom_transport = FaultInjectionTransportAsync()
        is_get_account_predicate: Callable[[AioHttpTransport], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name=L1,
                first_region_url=L1_URL,
                inner=inner,
                second_region_name=L2,
                second_region_url=L2_URL)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        for multiple_write_locations in [True, False]:
            # Create client
            initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
                custom_transport,
                default_endpoint=CONFIG.host,
                key=CONFIG.masterKey,
                database_id=CONFIG.TEST_DATABASE_ID,
                container_id=CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID,
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations,
                multiple_write_locations=multiple_write_locations,
            )
            container: ContainerProxy = initialized_objects["col"]

            # create an item
            id_value: str = str(uuid.uuid4())
            document_definition = {'id': id_value, 'pk': id_value}
            await container.create_item(body=document_definition)

            # API call: delete_all_items_by_partition_key
            if request_excluded_locations is None:
                await container.delete_all_items_by_partition_key(id_value)
            else:
                await container.delete_all_items_by_partition_key(id_value, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            actual_location = get_location(initialized_objects)
            if multiple_write_locations:
                assert actual_location == expected_location
            else:
                assert actual_location == L1

if __name__ == "__main__":
    unittest.main()
