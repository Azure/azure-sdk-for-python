# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import logging
import time
import unittest
import uuid

import pytest

from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.aio._database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.core.rest import HttpRequest
import asyncio
import sys
from azure.core.pipeline.transport import AioHttpTransport
from typing import Any, Callable
import _fault_injection_transport

COLLECTION = "created_collection"
logger = logging.getLogger('azure.cosmos')
logger.setLevel("INFO")
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

    async def cleanup(self, initializedObjects: dict[str, Any]):
        created_database: DatabaseProxy = initializedObjects["db"]
        try:
            await created_database.delete_container(initializedObjects["col"])
        except Exception as containerDeleteError:    
            logger.warn("Exception trying to delete database {}. {}".format(created_database.id, containerDeleteError))
        finally:    
            client: CosmosClient = initializedObjects["client"]
            try:
                await client.close()
            except Exception as closeError:    
                logger.warn("Exception trying to delete database {}. {}".format(created_database.id, closeError))

    async def setup(self, custom_transport: AioHttpTransport):

        host = test_config.TestConfig.host
        masterKey = test_config.TestConfig.masterKey
        connectionPolicy = test_config.TestConfig.connectionPolicy
        TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
        TEST_CONTAINER_SINGLE_PARTITION_ID = "test-timeout-retry-policy-container-" + str(uuid.uuid4())

        if (masterKey == '[YOUR_KEY_HERE]' or
                host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        client = CosmosClient(host, masterKey, consistency_level="Session",
                            connection_policy=connectionPolicy, transport=custom_transport,
                            logger=logger)
        created_database: DatabaseProxy = client.get_database_client(TEST_DATABASE_ID)
        created_collection = await created_database.create_container(TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                    partition_key=PartitionKey("/pk"))
        return {"client": client, "db": created_database, "col": created_collection}

    def predicate_url_contains_id(self, r: HttpRequest, id: str):
        logger.info("FaultPredicate for request {} {}".format(r.method, r.url));
        return  id in r.url;   

    def predicate_req_payload_contains_id(self, r: HttpRequest, id: str):
        logger.info("FaultPredicate for request {} {} - request payload {}".format(
            r.method, 
            r.url,
            "NONE" if r.body is None else r.body));
        
        if (r.body == None):
            return False
        
        
        return  '"id":"{}"'.format(id) in r.body;       

    async def throw_after_delay(self, delayInMs: int, error: Exception):
        await asyncio.sleep(delayInMs/1000.0)
        raise error

    async def test_throws_injected_error(self, setup):
        idValue: str = str(uuid.uuid4())
        document_definition = {'id': idValue,
                               'pk': idValue,
                               'name': 'sample document',
                               'key': 'value'}

        custom_transport =  _fault_injection_transport.FaulInjectionTransport(logger)
        predicate : Callable[[HttpRequest], bool] = lambda r: self.predicate_req_payload_contains_id(r, idValue) 
        custom_transport.addFault(predicate, lambda: self.throw_after_delay(
            500,
            CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error.")))

        initializedObjects = await self.setup(custom_transport)
        try:
            container: ContainerProxy = initializedObjects["col"]
            await container.create_item(body=document_definition)
            pytest.fail("Expected exception not thrown")      
        except CosmosHttpResponseError as cosmosError:
            if (cosmosError.status_code != 502):
                raise cosmosError
        finally:
            await self.cleanup(initializedObjects)

    async def test_succeeds_with_multiple_endpoints(self, setup):
        custom_transport = _fault_injection_transport.FaulInjectionTransport(logger)
        idValue: str = str(uuid.uuid4())
        document_definition = {'id': idValue,
                               'pk': idValue,
                               'name': 'sample document',
                               'key': 'value'}

        initializedObjects = await self.setup(custom_transport)
        try:
            container: ContainerProxy = initializedObjects["col"]
            
            created_document = await container.create_item(body=document_definition)
            start = time.perf_counter()
            
            while ((time.perf_counter() - start) < 2):
                await container.read_item(idValue, partition_key=idValue)
                await asyncio.sleep(0.2)

        finally:
            await self.cleanup(initializedObjects)        

if __name__ == '__main__':
    unittest.main()
