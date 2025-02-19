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
masterKey = test_config.TestConfig.masterKey
connectionPolicy = test_config.TestConfig.connectionPolicy
TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

@pytest.fixture()
def setup():
    return


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestDummyAsync:
    @classmethod
    def setup_class(cls):
        logger.info("starting class: {} execution".format(cls.__name__))
        cls.host = test_config.TestConfig.host
        cls.masterKey = test_config.TestConfig.masterKey

        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        
        cls.connectionPolicy = test_config.TestConfig.connectionPolicy
        cls.database_id = test_config.TestConfig.TEST_DATABASE_ID
        cls.single_partition_container_name= os.path.basename(__file__) + str(uuid.uuid4())

        cls.mgmtClient = CosmosClient(host, masterKey, consistency_level="Session",
                            connection_policy=connectionPolicy, logger=logger)
        created_database: DatabaseProxy = cls.mgmtClient.get_database_client(cls.database_id)
        asyncio.run(asyncio.wait_for(
            created_database.create_container(
                cls.single_partition_container_name,
                partition_key=PartitionKey("/pk")),
            MGMT_TIMEOUT))
    
    @classmethod
    def teardown_class(cls):
        logger.info("tearing down class: {}".format(cls.__name__))
        created_database: DatabaseProxy = cls.mgmtClient.get_database_client(cls.database_id)
        try:
            asyncio.run(asyncio.wait_for(
                created_database.delete_container(cls.single_partition_container_name),
                MGMT_TIMEOUT))
        except Exception as containerDeleteError:    
            logger.warn("Exception trying to delete database {}. {}".format(created_database.id, containerDeleteError))
        finally:    
            try:
                asyncio.run(asyncio.wait_for(cls.mgmtClient.close(), MGMT_TIMEOUT))
            except Exception as closeError:    
                logger.warn("Exception trying to delete database {}. {}".format(created_database.id, closeError))

    def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport):
        client = CosmosClient(host, masterKey, consistency_level="Session",
                            connection_policy=connectionPolicy, transport=custom_transport,
                            logger=logger, enable_diagnostics_logging=True)
        db: DatabaseProxy = client.get_database_client(TEST_DATABASE_ID)
        container: ContainerProxy = db.get_container_client(self.single_partition_container_name)
        return {"client": client, "db": db, "col": container}

    def cleanup_method(self, initializedObjects: dict[str, Any]):
        method_client: CosmosClient = initializedObjects["client"]
        try:
            asyncio.run(asyncio.wait_for(method_client.close(), MGMT_TIMEOUT))
        except Exception as closeError:    
            logger.warning("Exception trying to close method client.")

    async def test_throws_injected_error(self, setup):
        idValue: str = str(uuid.uuid4())
        document_definition = {'id': idValue,
                               'pk': idValue,
                               'name': 'sample document',
                               'key': 'value'}

        custom_transport =  FaultInjectionTransport()
        predicate : Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_req_for_document_with_id(r, idValue)
        custom_transport.addFault(predicate, lambda: FaultInjectionTransport.throw_after_delay(
            500,
            CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error.")))

        initializedObjects = self.setup_method_with_custom_transport(custom_transport)
        try:
            container: ContainerProxy = initializedObjects["col"]
            await container.create_item(body=document_definition)
            pytest.fail("Expected exception not thrown")      
        except CosmosHttpResponseError as cosmosError:
            if (cosmosError.status_code != 502):
                raise cosmosError
        finally:
            cleanupOp = self.cleanup_method(initializedObjects)
            if (cleanupOp != None):
                await cleanupOp

    async def test_succeeds_with_multiple_endpoints(self, setup):
        custom_transport = FaultInjectionTransport()
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        is_write_operation_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransport.predicate_is_write_operation(r, "https://localhost")
        emulator_as_multi_region_sm_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], AsyncHttpResponse] = \
            lambda r, inner: FaultInjectionTransport.transform_convert_emulator_to_single_master_read_multi_region_account(r, inner)

        custom_transport.addFault(is_write_operation_predicate, lambda: FaultInjectionTransport.throw_write_forbidden())
        custom_transport.add_response_transformation(is_get_account_predicate, emulator_as_multi_region_sm_account_transformation)

        idValue: str = str(uuid.uuid4())
        document_definition = {'id': idValue,
                               'pk': idValue,
                               'name': 'sample document',
                               'key': 'value'}

        initializedObjects = self.setup_method_with_custom_transport(custom_transport)
        try:
            container: ContainerProxy = initializedObjects["col"]

            created_document = await container.create_item(body=document_definition)
            start = time.perf_counter()


            #while ((time.perf_counter() - start) < 2):
            #    await container.read_item(idValue, partition_key=idValue)
            #    await asyncio.sleep(0.2)

        finally:
            self.cleanup_method(initializedObjects)

if __name__ == '__main__':
    unittest.main()
