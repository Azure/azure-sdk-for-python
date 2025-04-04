# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid
from typing import Dict, Any

import pytest
import pytest_asyncio
from azure.core.pipeline.transport._aiohttp import AioHttpTransport

from azure.cosmos import PartitionKey
from azure.cosmos._partition_health_tracker import HEALTH_STATUS, UNHEALTHY, UNHEALTHY_TENTATIVE
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from tests import test_config
from tests._fault_injection_transport_async import FaultInjectionTransportAsync

COLLECTION = "created_collection"
@pytest_asyncio.fixture(scope='class')
async def setup():
    if (TestPPCBSmMrrAsync.master_key == '[YOUR_KEY_HERE]' or
            TestPPCBSmMrrAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
    client = CosmosClient(TestPPCBSmMrrAsync.host, TestPPCBSmMrrAsync.master_key, consistency_level="Session")
    created_database = client.get_database_client(TestPPCBSmMrrAsync.TEST_DATABASE_ID)
    created_collection = await created_database.create_container(TestPPCBSmMrrAsync.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                 partition_key=PartitionKey("/pk"), throughput=10000)
    yield {
        COLLECTION: created_collection
    }

    await created_database.delete_container(TestPPCBSmMrrAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    await client.close()
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"




def error_codes():

    return [408, 500, 502, 503]


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestPPCBSmMrrAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = os.path.basename(__file__) + str(uuid.uuid4())

    async def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    async def create_custom_transport_sm_mrr(self):
        custom_transport =  FaultInjectionTransportAsync()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate = lambda \
                r: FaultInjectionTransportAsync.predicate_is_write_operation(r, self.host)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_write_forbidden()))

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_region_sm_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_region_sm_account_transformation)
        return custom_transport



    @pytest.mark.parametrize("error_code", error_codes())
    async def test_consecutive_failure_threshold_async(self, setup, error_code):
        custom_transport = await self.create_custom_transport_sm_mrr()
        id_value = 'failoverDoc-' + str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': 'pk1',
                               'name': 'sample document',
                               'key': 'value'}
        predicate = lambda r: FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, id_value)
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected fault.")))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        container = custom_setup['col']

        # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
        for i in range(6):
            with pytest.raises(CosmosHttpResponseError):
                await container.create_item(body=document_definition)

        TestPPCBSmMrrAsync.validate_unhealthy_partitions(container.client_connection._global_endpoint_manager, 0)



        # create item with client without fault injection
        await setup[COLLECTION].create_item(body=document_definition)

        # reads should failover and only the relevant partition should be marked as unavailable
        await container.read_item(item=document_definition['id'], partition_key=document_definition['pk'])
        # partition should not have been marked unavailable after one error
        TestPPCBSmMrrAsync.validate_unhealthy_partitions(container.client_connection._global_endpoint_manager, 0)

        for i in range(10):
            await container.read_item(item=document_definition['id'], partition_key=document_definition['pk'])

       # the partition should have been marked as unavailable
        TestPPCBSmMrrAsync.validate_unhealthy_partitions(container.client_connection._global_endpoint_manager, 1)


    @staticmethod
    def validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions):
        health_info_map = global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.pkrange_wrapper_to_health_info
        unhealthy_partitions = 0
        for pk_range_wrapper, location_to_health_info in health_info_map.items():
            for location, health_info in location_to_health_info:
                if health_info[HEALTH_STATUS] == UNHEALTHY_TENTATIVE or health_info[HEALTH_STATUS] == UNHEALTHY:
                    unhealthy_partitions += 1
        assert len(health_info_map) == expected_unhealthy_partitions
        assert unhealthy_partitions == expected_unhealthy_partitions






    # test_failure_rate_threshold


if __name__ == '__main__':
    unittest.main()