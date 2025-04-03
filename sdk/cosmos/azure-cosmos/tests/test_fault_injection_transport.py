import logging
import os
import sys
import time
import uuid
from typing import Callable

import pytest
from azure.core.pipeline.transport._requests_basic import RequestsTransport
from azure.core.rest import HttpRequest

import test_config
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos import PartitionKey
from azure.cosmos import CosmosClient
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError

logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

host = test_config.TestConfig.host
master_key = test_config.TestConfig.masterKey
TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
SINGLE_PARTITION_CONTAINER_NAME = os.path.basename(__file__) + str(uuid.uuid4())

@pytest.mark.unittest
@pytest.mark.cosmosEmulator
class TestFaultInjectionTransport:

    @classmethod
    async def setup_class(cls):
        logger.info("starting class: {} execution".format(cls.__name__))
        cls.host = host
        cls.master_key = master_key

        if (cls.master_key == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.database_id = TEST_DATABASE_ID
        cls.single_partition_container_name = SINGLE_PARTITION_CONTAINER_NAME

        cls.mgmt_client = CosmosClient(cls.host, cls.master_key, consistency_level="Session", logger=logger)
        created_database = cls.mgmt_client.get_database_client(cls.database_id)
        created_database.create_container(
            cls.single_partition_container_name,
            partition_key=PartitionKey("/pk"))


    @classmethod
    async def teardown_class(cls):
        logger.info("tearing down class: {}".format(cls.__name__))
        created_database = cls.mgmt_client.get_database_client(cls.database_id)
        try:
            created_database.delete_container(cls.single_partition_container_name),
        except Exception as containerDeleteError:
            logger.warning("Exception trying to delete database {}. {}".format(created_database.id, containerDeleteError))

    @staticmethod
    def setup_method_with_custom_transport(custom_transport: RequestsTransport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, master_key, consistency_level="Session",
                              transport=custom_transport, logger=logger, enable_diagnostics_logging=True, **kwargs)
        db: DatabaseProxy = client.get_database_client(TEST_DATABASE_ID)
        container: ContainerProxy = db.get_container_client(SINGLE_PARTITION_CONTAINER_NAME)
        return {"client": client, "db": db, "col": container}


    def test_throws_injected_error_async(self: "TestFaultInjectionTransport"):
        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        custom_transport =  FaultInjectionTransportAsync()
        predicate : Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, id_value)
        custom_transport.add_fault(predicate, lambda r: FaultInjectionTransportAsync.error_after_delay(
            10000,
            CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error.")))

        initialized_objects = TestFaultInjectionTransport.setup_method_with_custom_transport(custom_transport)
        start: float = time.perf_counter()
        try:
            container: ContainerProxy = initialized_objects["col"]
            container.create_item(body=document_definition)
            pytest.fail("Expected exception not thrown")
        except CosmosHttpResponseError as cosmosError:
            end = time.perf_counter() - start
            # validate response took more than 10 seconds
            assert end > 10
            if cosmosError.status_code != 502:
                raise cosmosError