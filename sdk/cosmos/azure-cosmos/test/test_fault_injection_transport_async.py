# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import logging
import os
import sys
import time
import unittest
import uuid
from typing import Any, Callable

import pytest
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.rest import HttpRequest, AsyncHttpResponse

import test_config
from _fault_injection_transport import FaultInjectionTransport
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.aio._database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError

COLLECTION = "created_collection"
MGMT_TIMEOUT = 3.0 
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

host = test_config.TestConfig.host
master_key = test_config.TestConfig.masterKey
connection_policy = test_config.TestConfig.connectionPolicy
TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

@pytest.fixture()
def setup():
    return


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestFaultInjectionTransportAsync:
    @classmethod
    def setup_class(cls):
        logger.info("starting class: {} execution".format(cls.__name__))
        cls.host = test_config.TestConfig.host
        cls.master_key = test_config.TestConfig.masterKey

        if (cls.master_key == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        
        cls.connection_policy = test_config.TestConfig.connectionPolicy
        cls.database_id = test_config.TestConfig.TEST_DATABASE_ID
        cls.single_partition_container_name= os.path.basename(__file__) + str(uuid.uuid4())

        cls.mgmt_client = CosmosClient(host, master_key, consistency_level="Session",
                                      connection_policy=connection_policy, logger=logger)
        created_database: DatabaseProxy = cls.mgmt_client.get_database_client(cls.database_id)
        asyncio.run(asyncio.wait_for(
            created_database.create_container(
                cls.single_partition_container_name,
                partition_key=PartitionKey("/pk")),
            MGMT_TIMEOUT))
    
    @classmethod
    def teardown_class(cls):
        logger.info("tearing down class: {}".format(cls.__name__))
        created_database: DatabaseProxy = cls.mgmt_client.get_database_client(cls.database_id)
        try:
            asyncio.run(asyncio.wait_for(
                created_database.delete_container(cls.single_partition_container_name),
                MGMT_TIMEOUT))
        except Exception as containerDeleteError:    
            logger.warning("Exception trying to delete database {}. {}".format(created_database.id, containerDeleteError))
        finally:    
            try:
                asyncio.run(asyncio.wait_for(cls.mgmt_client.close(), MGMT_TIMEOUT))
            except Exception as closeError:    
                logger.warning("Exception trying to delete database {}. {}".format(created_database.id, closeError))

    def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport, **kwargs):
        client = CosmosClient(host, master_key, consistency_level="Session",
                              connection_policy=connection_policy, transport=custom_transport,
                              logger=logger, enable_diagnostics_logging=True, **kwargs)
        db: DatabaseProxy = client.get_database_client(TEST_DATABASE_ID)
        container: ContainerProxy = db.get_container_client(self.single_partition_container_name)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    def cleanup_method(initialized_objects: dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        try:
            asyncio.run(asyncio.wait_for(method_client.close(), MGMT_TIMEOUT))
        except Exception as close_error:
            logger.warning(f"Exception trying to close method client. {close_error}")

    async def test_throws_injected_error(self, setup):
        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        custom_transport =  FaultInjectionTransport()
        predicate : Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_req_for_document_with_id(r, id_value)
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransport.error_after_delay(
            500,
            CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error."))))

        initialized_objects = self.setup_method_with_custom_transport(custom_transport)
        try:
            container: ContainerProxy = initialized_objects["col"]
            await container.create_item(body=document_definition)
            pytest.fail("Expected exception not thrown")      
        except CosmosHttpResponseError as cosmosError:
            if cosmosError.status_code != 502:
                raise cosmosError
        finally:
            TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_swr_mrr_succeeds(self, setup):
        expected_read_region_uri: str = test_config.TestConfig.local_host
        expected_write_region_uri: str = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransport()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransport.predicate_is_write_operation(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransport.error_write_forbidden()))

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_region_sm_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], AsyncHttpResponse] = \
            lambda r, inner: FaultInjectionTransport.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                r=r,
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_region_sm_account_transformation)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["Read Region", "Write Region"])
        try:
            container: ContainerProxy = initialized_objects["col"]

            created_document = await container.create_item(body=document_definition)
            request: HttpRequest = created_document.get_response_headers()["_request"]
            # Validate the response comes from "South Central US" (the write region)
            assert request.url.startswith(expected_write_region_uri)
            start:float = time.perf_counter()

            while (time.perf_counter() - start) < 2:
                read_document = await container.read_item(id_value, partition_key=id_value)
                request: HttpRequest = read_document.get_response_headers()["_request"]
                # Validate the response comes from "East US" (the most preferred read-only region)
                assert request.url.startswith(expected_read_region_uri)

        finally:
            TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_mwr_succeeds(self, setup):
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransport()

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], AsyncHttpResponse] = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                r=r,
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"])
        try:
            container: ContainerProxy = initialized_objects["col"]

            created_document = await container.create_item(body=document_definition)
            request: HttpRequest = created_document.get_response_headers()["_request"]
            # Validate the response comes from "South Central US" (the write region)
            assert request.url.startswith(first_region_uri)
            start:float = time.perf_counter()

            while (time.perf_counter() - start) < 2:
                read_document = await container.read_item(id_value, partition_key=id_value)
                request: HttpRequest = read_document.get_response_headers()["_request"]
                # Validate the response comes from "East US" (the most preferred read-only region)
                assert request.url.startswith(first_region_uri)

        finally:
            TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

if __name__ == '__main__':
    unittest.main()
