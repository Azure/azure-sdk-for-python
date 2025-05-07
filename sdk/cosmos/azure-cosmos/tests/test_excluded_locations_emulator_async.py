# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import unittest
import uuid

from azure.cosmos.aio import CosmosClient

import test_config
import pytest
from typing import Callable, List

from azure.core.rest import HttpRequest
from azure.core.pipeline.transport import AioHttpTransport
from _fault_injection_transport_async import FaultInjectionTransportAsync, ERROR_WITH_COUNTER
from azure.cosmos.aio._container import ContainerProxy
from test_excluded_locations import (L1, L2,
                                     TestDataType, set_test_data_type)
from test_excluded_locations_emulator import (L1_URL, L2_URL,
                                              get_location,
                                              delete_all_items_by_partition_key_test_data,
                                              metadata_read_with_excluded_locations_test_data)
from test_fault_injection_transport_async import TestFaultInjectionTransportAsync
from azure.cosmos.exceptions import CosmosHttpResponseError

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID
SINGLE_PARTITION_CONTAINER_ID = CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID
SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID = CONFIG.TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID

set_test_data_type(TestDataType.ALL_TESTS)

async def init_container(client, db_id, container_id):
    db = client.get_database_client(db_id)
    container = db.get_container_client(container_id)

    return db, container

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

    @pytest.mark.parametrize('test_data', metadata_read_with_excluded_locations_test_data())
    async def test_metadata_read_with_excluded_locations(self: "TestExcludedLocationsEmulatorAsync", test_data: List[List[str]]):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_counts = test_data
        target_urls = [L1_URL, L2_URL]
        expected_locations = [L2, L1]
        for target_url, expected_location, expected_count in zip(target_urls, expected_locations, expected_counts):
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

            # Inject rule to simulate request timeout in target region
            is_request_to_target_region: Callable[[HttpRequest], bool] = lambda \
                    r: (FaultInjectionTransportAsync.predicate_targets_region(r, target_url) and
                        FaultInjectionTransportAsync.predicate_is_collection_operation(r) and
                        not FaultInjectionTransportAsync.predicate_is_write_operation(r, target_url))
            fault_factory = lambda r: asyncio.create_task(custom_transport.error_with_counter(
                CosmosHttpResponseError(
                    status_code=408,
                    message="Request Time Out Error.")
            ))
            custom_transport.add_fault(is_request_to_target_region, fault_factory)


            # Create client
            async with CosmosClient(HOST, KEY,
                                    consistency_level="Session",
                                    transport=custom_transport,
                                    # logger=logger, enable_diagnostics_logging=True,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=True) as client:
                db, container = await init_container(client, DATABASE_ID, SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID)

                await custom_transport.reset_counters()
                if request_excluded_locations is None:
                    await container.read()
                else:
                    await container.read(excluded_locations=request_excluded_locations)

                # Verify endpoint locations
                actual_location = get_location({"client": client})
                assert actual_location == expected_location
                actual_count = custom_transport.counters[ERROR_WITH_COUNTER]
                assert actual_count == expected_count

if __name__ == "__main__":
    unittest.main()
