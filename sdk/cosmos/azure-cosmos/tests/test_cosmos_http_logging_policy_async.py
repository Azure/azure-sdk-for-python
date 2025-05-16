# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for the CosmosHttpLoggingPolicy."""
import unittest
import uuid
import logging

import pytest

import azure.cosmos.aio._cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import test_config
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_fault_injection_transport_async import TestFaultInjectionTransportAsync

from test_cosmos_http_logging_policy import create_logger, L1, L2, CONFIG, \
    get_locations_list, FilterStatusCode, MockHandler

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

@pytest.mark.cosmosEmulator
class TestCosmosHttpLoggerAsync(unittest.IsolatedAsyncioTestCase):
    mock_handler_diagnostic = None
    mock_handler_default = None
    logger_diagnostic = None
    logger_default = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.mock_handler_default = MockHandler()
        self.mock_handler_diagnostic = MockHandler()
        self.mock_handler_filtered_diagnostic = MockHandler()
        # Add filter to the filtered diagnostics handler

        self.mock_handler_filtered_diagnostic.addFilter(FilterStatusCode())

        self.logger = logging.getLogger("azure.cosmos")
        self.logger.setLevel(logging.INFO)

        self.client_default = None
        self.client_diagnostic = None
        self.client_filtered_diagnostic = None

    async def asyncTearDown(self):
        if self.client_default:
            await self.client_default.close()
        if self.client_diagnostic:
            await self.client_diagnostic.close()
        if self.client_filtered_diagnostic:
            await self.client_filtered_diagnostic.close()

    async def test_default_http_logging_policy_async(self):
        self.logger.addHandler(self.mock_handler_default)
        # Create a client with the default logging policy
        self.client_default = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                         consistency_level="Session", logger=self.logger)
        await self.client_default.__aenter__()
        # Test if we can log info from creating a database
        database_id = "database_test-" + str(uuid.uuid4())
        await self.client_default.create_database(id=database_id)

        assert all(m.levelname == 'INFO' for m in self.mock_handler_default.messages)
        messages_request = self.mock_handler_default.messages[0].message.split("\n")
        messages_response = self.mock_handler_default.messages[1].message.split("\n")
        assert messages_request[1] == "Request method: 'GET'"
        assert 'Request headers:' in messages_request[2]
        assert messages_request[15] == 'No body was attached to the request'
        assert messages_response[0] == 'Response status: 200'
        assert 'Response headers:' in messages_response[1]

        self.mock_handler_default.reset()
        self.logger.removeHandler(self.mock_handler_default)

        # delete database
        await self.client_default.delete_database(database_id)

    async def test_cosmos_http_logging_policy_async(self):
        self.logger.addHandler(self.mock_handler_diagnostic)
        # Create a client with the diagnostic logging policy
        self.client_diagnostic = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                            consistency_level="Session", logger=self.logger,
                                                            enable_diagnostics_logging=True)
        # Test if we can log into from reading a database
        database_id = "database_test-" + str(uuid.uuid4())
        await self.client_diagnostic.create_database(id=database_id)
        assert all(m.levelname == 'INFO' for m in self.mock_handler_diagnostic.messages)
        # Check that we made a databaseaccount read request only once and that we only logged it once
        messages_request = self.mock_handler_diagnostic.messages[0]
        messages_response = self.mock_handler_diagnostic.messages[1]
        elapsed_time = messages_response.duration
        assert "databaseaccount" == messages_request.resource_type
        assert messages_request.verb == "GET"
        assert 200 == messages_response.status_code
        assert "Read" == messages_request.operation_type
        assert elapsed_time is not None
        assert "Response headers" in messages_response.message
        # Verify we only have a total of 6 logged messages: 4 from databaseaccount read and 2 from create database
        assert len(self.mock_handler_diagnostic.messages) == 6
        # Test if we can log into from creating a database
        # The request to create database should follow the databaseaccount read request immediately
        messages_request = self.mock_handler_diagnostic.messages[4]
        messages_response = self.mock_handler_diagnostic.messages[5]
        elapsed_time = messages_response.duration
        assert "dbs" == messages_request.resource_type
        assert messages_request.verb == "POST"
        assert 201 == messages_response.status_code
        assert messages_request.operation_type == "Create"
        assert elapsed_time is not None
        assert "Response headers" in messages_response.message

        self.mock_handler_diagnostic.reset()
        # now test in case of an error
        try:
            await self.client_diagnostic.create_database(id=database_id)
        except:
            pass
        assert all(m.levelname == 'INFO' for m in self.mock_handler_diagnostic.messages)
        messages_request = self.mock_handler_diagnostic.messages[0]
        messages_response = self.mock_handler_diagnostic.messages[1]
        elapsed_time = messages_response.duration
        assert "dbs" == messages_request.resource_type
        assert messages_request.operation_type == "Create"
        assert 'Request headers:' in messages_request.msg
        assert 'A body is sent with the request' in messages_request.msg
        assert messages_response.status_code == 409
        assert elapsed_time is not None
        assert "Response headers" in messages_response.msg

        # delete database
        await self.client_diagnostic.delete_database(database_id)

        self.mock_handler_diagnostic.reset()
        self.logger.removeHandler(self.mock_handler_diagnostic)

    async def test_filtered_diagnostics_logging_policy_async(self):
        self.logger.addHandler(self.mock_handler_filtered_diagnostic)
        # Create a client with the filtered diagnostics logging policy
        self.client_filtered_diagnostic = cosmos_client.CosmosClient(self.host, self.masterKey,
                                                                     consistency_level="Session",
                                                                     logger=self.logger,
                                                                     enable_diagnostics_logging=True)
        # Test if we can log errors with the filtered diagnostics logger
        database_id = "database_test_" + str(uuid.uuid4())
        container_id = "diagnostics_container_test_" + str(uuid.uuid4())
        await self.client_filtered_diagnostic.create_database(id=database_id)
        database = self.client_filtered_diagnostic.get_database_client(database_id)
        await database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))

        # Try to read an item that doesn't exist
        try:
            container = database.get_container_client(container_id)
            await container.read_item(item="nonexistent_item", partition_key="nonexistent_pk")
        except:
            pass

        # Assert that the filtered logger only captured the error
        request_log = self.mock_handler_filtered_diagnostic.messages[0]
        response_log = self.mock_handler_filtered_diagnostic.messages[1]
        assert response_log.status_code == 404
        assert request_log.resource_type == "docs"
        assert request_log.operation_type == "Read"
        assert len(self.mock_handler_filtered_diagnostic.messages) == 2

        self.mock_handler_filtered_diagnostic.reset()

        # Try to create an item with an invalid partition key
        try:
            await container.create_item(body={"FakeProperty": "item1", "NotPk": None})
        except:
            pass

        # Assert that the filtered logger captured the error
        request_log = self.mock_handler_filtered_diagnostic.messages[0]
        response_log = self.mock_handler_filtered_diagnostic.messages[1]
        assert response_log.status_code == 400
        assert request_log.resource_type == "docs"
        assert request_log.operation_type == "Create"
        assert len(self.mock_handler_filtered_diagnostic.messages) == 2

        # Clean up
        await self.client_filtered_diagnostic.delete_database(database_id)
        self.mock_handler_filtered_diagnostic.reset()
        self.logger.removeHandler(self.mock_handler_filtered_diagnostic)

    async def test_client_settings_async(self):
        # Test data
        all_locations = [L1, L2]
        client_excluded_locations = [L1]
        multiple_write_locations = True

        # Client setup
        mock_handler = MockHandler()
        logger = create_logger("test_logger_client_settings", mock_handler)

        custom_transport = FaultInjectionTransportAsync()
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name=L1,
                second_region_name=L2,
                inner=inner,
            )
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            default_endpoint=CONFIG.host,
            key=CONFIG.masterKey,
            database_id=CONFIG.TEST_DATABASE_ID,
            container_id=CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID,
            custom_logger=logger,
            preferred_locations=all_locations,
            excluded_locations=client_excluded_locations,
            multiple_write_locations=multiple_write_locations
        )
        mock_handler.reset()

        # create an item
        id_value = str(uuid.uuid4())
        document_definition = {'id': id_value, 'pk': id_value}
        container = initialized_objects["col"]
        await container.create_item(body=document_definition)

        # Verify endpoint locations
        messages_split = mock_handler.messages[1].message.split("\n")
        for message in messages_split:
            if "Preferred Regions:" in message:
                locations = get_locations_list(message)
                assert all_locations == locations
            elif "Excluded Regions:" in message:
                locations = get_locations_list(message)
                assert client_excluded_locations == locations
            elif "Account Read Regions:" in message:
                locations = get_locations_list(message)
                assert all_locations == locations
            elif "Account Write Regions:" in message:
                locations = get_locations_list(message)
                assert all_locations == locations
        await initialized_objects["client"].close()


if __name__ == "__main__":
    unittest.main()