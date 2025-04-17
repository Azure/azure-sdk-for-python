# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import logging
import os
import sys
import time
import unittest
import uuid
from typing import Any, Callable, Awaitable, Dict
from unittest import IsolatedAsyncioTestCase

import pytest
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.pipeline.transport._aiohttp import AioHttpTransportResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse

import test_config
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.aio._database import DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.core.exceptions import ServiceRequestError

MGMT_TIMEOUT = 5.0
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

host = test_config.TestConfig.host
master_key = test_config.TestConfig.masterKey
TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
SINGLE_PARTITION_CONTAINER_NAME = os.path.basename(__file__) + str(uuid.uuid4())

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestFaultInjectionTransportAsync(IsolatedAsyncioTestCase):
    @classmethod
    async def asyncSetUp(cls):
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
        await asyncio.wait_for(
            created_database.create_container(
                cls.single_partition_container_name,
                partition_key=PartitionKey("/pk")),
            MGMT_TIMEOUT)
    
    @classmethod
    async def asyncTearDown(cls):
        logger.info("tearing down class: {}".format(cls.__name__))
        created_database = cls.mgmt_client.get_database_client(cls.database_id)
        try:
            await asyncio.wait_for(
                created_database.delete_container(cls.single_partition_container_name),
                MGMT_TIMEOUT)
        except Exception as containerDeleteError:    
            logger.warning("Exception trying to delete database {}. {}".format(created_database.id, containerDeleteError))
        finally:    
            try:
                await asyncio.wait_for(cls.mgmt_client.close(), MGMT_TIMEOUT)
            except Exception as closeError:    
                logger.warning("Exception trying to close client {}. {}".format(created_database.id, closeError))

    @staticmethod
    async def setup_method_with_custom_transport(
            custom_transport: AioHttpTransport,
            default_endpoint: str = host,
            key: str = master_key,
            database_id: str = TEST_DATABASE_ID,
            container_id: str = SINGLE_PARTITION_CONTAINER_NAME,
            **kwargs):
        client = CosmosClient(default_endpoint, key, consistency_level="Session",
                              transport=custom_transport, logger=logger, enable_diagnostics_logging=True, **kwargs)
        db: DatabaseProxy = client.get_database_client(database_id)
        container: ContainerProxy = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        try:
            await asyncio.wait_for(method_client.close(), MGMT_TIMEOUT)
        except Exception as close_error:
            logger.warning(f"Exception trying to close method client. {close_error}")

    async def test_throws_injected_error_async(self: "TestFaultInjectionTransportAsync"):
        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        custom_transport =  FaultInjectionTransportAsync()
        predicate : Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, id_value)
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            10000,
            CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error."))))

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(custom_transport)
        start: float = time.perf_counter()
        try:
            container: ContainerProxy = initialized_objects["col"]
            await container.create_item(body=document_definition)
            pytest.fail("Expected exception not thrown")      
        except CosmosHttpResponseError as cosmosError:
            end = time.perf_counter() - start
            # validate response took more than 10 seconds
            assert end > 10
            if cosmosError.status_code != 502:
                raise cosmosError
        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_swr_mrr_succeeds_async(self: "TestFaultInjectionTransportAsync"):
        expected_read_region_uri: str = test_config.TestConfig.local_host
        expected_write_region_uri: str = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransportAsync()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_write_operation(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_write_forbidden()))

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_region_sm_account_transformation: Callable[[HttpRequest, Callable[[], AsyncHttpResponse]], AioHttpTransportResponse] = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_region_sm_account_transformation)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["Read Region", "Write Region"])
        try:
            container: ContainerProxy = initialized_objects["col"]

            created_document = await container.create_item(body=document_definition)
            request: HttpRequest = created_document.get_response_headers()["_request"]
            # Validate the response comes from "Write Region" (the write region)
            assert request.url.startswith(expected_write_region_uri)
            start: float = time.perf_counter()

            while (time.perf_counter() - start) < 2:
                read_document = await container.read_item(id_value, partition_key=id_value)
                request = read_document.get_response_headers()["_request"]
                # Validate the response comes from "Read Region" (the most preferred read-only region)
                assert request.url.startswith(expected_read_region_uri)

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_swr_mrr_region_down_read_succeeds_async(self: "TestFaultInjectionTransportAsync"):
        expected_read_region_uri: str = test_config.TestConfig.local_host
        expected_write_region_uri: str = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransportAsync()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_write_operation(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_write_forbidden()))

        # Inject rule to simulate regional outage in "Read Region"
        is_request_to_read_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_request_to_read_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_region_sm_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], AsyncHttpResponse]], AioHttpTransportResponse] = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_region_sm_account_transformation)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            default_endpoint=expected_write_region_uri,
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
                request = read_document.get_response_headers()["_request"]
                # Validate the response comes from "Write Region" ("Read Region" the most preferred read-only region is down)
                assert request.url.startswith(expected_write_region_uri)

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_swr_mrr_region_down_envoy_read_succeeds_async(self: "TestFaultInjectionTransportAsync"):
        expected_read_region_uri: str = test_config.TestConfig.local_host
        expected_write_region_uri: str = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransportAsync()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_write_operation(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_write_forbidden()))

        # Inject rule to simulate regional outage in "Read Region"
        is_request_to_read_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, expected_read_region_uri) and \
                    FaultInjectionTransportAsync.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_read_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                500,
                CosmosHttpResponseError(
                    status_code=502,
                    message="Some random reverse proxy error."))))

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_region_sm_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], Awaitable[AsyncHttpResponse]]], AioHttpTransportResponse] = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_region_sm_account_transformation)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            default_endpoint=expected_write_region_uri,
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
                request = read_document.get_response_headers()["_request"]
                # Validate the response comes from "Write Region" ("Read Region" the most preferred read-only region is down)
                assert request.url.startswith(expected_write_region_uri)

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)


    async def test_mwr_succeeds_async(self: "TestFaultInjectionTransportAsync"):
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransportAsync()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation: Callable[[HttpRequest, Callable[[HttpRequest], Awaitable[AsyncHttpResponse]]], AioHttpTransportResponse] = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
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
                request = read_document.get_response_headers()["_request"]
                # Validate the response comes from "East US" (the most preferred read-only region)
                assert request.url.startswith(first_region_uri)

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_mwr_region_down_succeeds_async(self: "TestFaultInjectionTransportAsync"):
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransportAsync()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransportAsync.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"])
        try:
            container: ContainerProxy = initialized_objects["col"]

            start:float = time.perf_counter()
            while (time.perf_counter() - start) < 2:
                # reads and writes should failover to second region
                upsert_document = await container.upsert_item(body=document_definition)
                request = upsert_document.get_response_headers()["_request"]
                assert request.url.startswith(second_region_uri)
                read_document = await container.read_item(id_value, partition_key=id_value)
                request = read_document.get_response_headers()["_request"]
                # Validate the response comes from "East US" (the most preferred read-only region)
                assert request.url.startswith(second_region_uri)

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_swr_mrr_all_regions_down_for_read_async(self: "TestFaultInjectionTransportAsync"):
        expected_read_region_uri: str = test_config.TestConfig.local_host
        expected_write_region_uri: str = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransportAsync()

        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_is_write_operation(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_write_forbidden()))

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: (FaultInjectionTransportAsync.predicate_targets_region(r, expected_write_region_uri) and
                   FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                    not FaultInjectionTransportAsync.predicate_is_write_operation(r, expected_write_region_uri))


        # Inject rule to simulate regional outage in "Second Region"
        is_request_to_second_region: Callable[[HttpRequest], bool] = lambda \
                r: (FaultInjectionTransportAsync.predicate_targets_region(r, expected_read_region_uri) and
                   FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                    not FaultInjectionTransportAsync.predicate_is_write_operation(r, expected_write_region_uri))

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))
        custom_transport.add_fault(
            is_request_to_second_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"])
        try:
            container: ContainerProxy = initialized_objects["col"]
            await container.upsert_item(body=document_definition)
            with pytest.raises(ServiceRequestError):
                await container.read_item(id_value, partition_key=id_value)
        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    async def test_mwr_all_regions_down_async(self: "TestFaultInjectionTransportAsync"):

        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransportAsync()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransportAsync.predicate_is_document_operation(r)

        # Inject rule to simulate regional outage in "Second Region"
        is_request_to_second_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, second_region_uri) and \
                   FaultInjectionTransportAsync.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))
        custom_transport.add_fault(
            is_request_to_second_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"])
        try:
            container: ContainerProxy = initialized_objects["col"]
            with pytest.raises(ServiceRequestError):
                await container.upsert_item(body=document_definition)
        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

if __name__ == '__main__':
    unittest.main()
