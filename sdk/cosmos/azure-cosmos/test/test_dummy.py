# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from collections.abc import MutableMapping
import logging
import time
from tokenize import String
from typing import Any, Callable
import unittest
import uuid

import pytest
import pytest_asyncio

from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.aio._database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.core.rest import HttpRequest, AsyncHttpResponse
import asyncio
import aiohttp
import sys
from azure.core.pipeline.transport import AioHttpTransport

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

        custom_transport = FaulInjectionTransport(logger)
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
        custom_transport = FaulInjectionTransport(logger)
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


class FaulInjectionTransport(AioHttpTransport):
    def __init__(self, logger: logging.Logger, *, session: aiohttp.ClientSession | None = None, loop=None, session_owner: bool = True, **config):
        self.logger = logger
        self.faults = []
        self.requestTransformations = []
        self.responseTransformations = []
        super().__init__(session=session, loop=loop, session_owner=session_owner, **config)

    def addFault(self, predicate: Callable[[HttpRequest], bool], faultFactory: Callable[[HttpRequest], asyncio.Task[Exception]]):
        self.faults.append({"predicate": predicate, "apply": faultFactory})

    def addRequestTransformation(self, predicate: Callable[[HttpRequest], bool], requestTransformation: Callable[[HttpRequest], asyncio.Task[HttpRequest]]):
        self.requestTransformations.append({"predicate": predicate, "apply": requestTransformation})

    def addResponseTransformation(self, predicate: Callable[[HttpRequest], bool], responseTransformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], AsyncHttpResponse]):
        self.responseTransformations.append({
            "predicate": predicate, 
            "apply": responseTransformation})    

    def firstItem(self, iterable, condition=lambda x: True):
        """
        Returns the first item in the `iterable` that satisfies the `condition`.
        
        If no item satisfies the condition, it returns None.
        """
        return next((x for x in iterable if condition(x)), None)

    async def send(self, request: HttpRequest, *, stream: bool = False, proxies: MutableMapping[str, str] | None = None, **config):
        # find the first fault Factory with matching predicate if any
        firstFaultFactory = self.firstItem(iter(self.faults), lambda f: f["predicate"](request))
        if (firstFaultFactory != None):
            injectedError = await firstFaultFactory["apply"]()
            self.logger.info("Found to-be-injected error {}".format(injectedError))
            raise injectedError

        # apply the chain of request transformations with matching predicates if any
        matchingRequestTransformations = filter(lambda f: f["predicate"](f["predicate"]), iter(self.requestTransformations))
        for currentTransformation in matchingRequestTransformations:
            request = await currentTransformation["apply"](request)

        firstResonseTransformation = self.firstItem(iter(self.responseTransformations), lambda f: f["predicate"](request))
        
        getResponseTask = super().send(request, stream=stream, proxies=proxies, **config)
        
        if (firstResonseTransformation != None):
            self.logger.info(f"Invoking response transformation")
            response = await firstResonseTransformation["apply"](request, lambda: getResponseTask)        
            self.logger.info(f"Received response transformation result with status code {response.status_code}")
            return response
        else:
            self.logger.info(f"Sending request to {request.url}")
            response = await getResponseTask
            self.logger.info(f"Received response with status code {response.status_code}")
            return response

if __name__ == '__main__':
    unittest.main()
