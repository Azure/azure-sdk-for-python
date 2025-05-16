# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for the CosmosHttpLoggingPolicy."""
import logging
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey, ContainerProxy
import test_config
from _fault_injection_transport import FaultInjectionTransport
from test_fault_injection_transport import TestFaultInjectionTransport
from typing import List, Callable
from azure.core.rest import HttpRequest

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


class MockHandler(logging.Handler):

    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record)

class FilterStatusCode(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'status_code') and record.status_code >= 400:
            return True
        return False

CONFIG = test_config.TestConfig
L1 = "Location1"
L2 = "Location2"
L1_URL = test_config.TestConfig.local_host
L2_URL = L1_URL.replace("localhost", "127.0.0.1")
URL_TO_LOCATIONS = {
    L1_URL: L1,
    L2_URL: L2}


def create_logger(name: str, mock_handler: MockHandler, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addHandler(mock_handler)
    logger.setLevel(level)

    return logger

def get_locations_list(msg: str) -> List[str]:
    msg = msg.replace(' ', '')
    msg = msg.replace('\'', '')
    # Find the substring between the first '[' and the last ']'
    start = msg.find('[') + 1
    end = msg.rfind(']')
    # Extract the substring and convert it to a list using ast.literal_eval
    msg = msg[start:end]
    return msg.split(',')

@pytest.mark.cosmosEmulator
class TestCosmosHttpLogger(unittest.TestCase):
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
        cls.mock_handler_default = MockHandler()
        cls.mock_handler_diagnostic = MockHandler()
        cls.mock_handler_filtered_diagnostic = MockHandler()

        # Add filter to the filtered diagnostics handler

        cls.mock_handler_filtered_diagnostic.addFilter(FilterStatusCode())
        cls.logger_default = create_logger("testloggerdefault", cls.mock_handler_default)
        cls.logger_diagnostic = create_logger("testloggerdiagnostic", cls.mock_handler_diagnostic)
        cls.logger_filtered_diagnostic = create_logger("testloggerfiltereddiagnostic",
                                                       cls.mock_handler_filtered_diagnostic)
        cls.client_default = cosmos_client.CosmosClient(cls.host, cls.masterKey,
                                                        consistency_level="Session",
                                                        connection_policy=cls.connectionPolicy,
                                                        logger=cls.logger_default)
        cls.client_diagnostic = cosmos_client.CosmosClient(cls.host, cls.masterKey,
                                                           consistency_level="Session",
                                                           connection_policy=cls.connectionPolicy,
                                                           logger=cls.logger_diagnostic,
                                                           enable_diagnostics_logging=True)
        cls.client_filtered_diagnostic = cosmos_client.CosmosClient(cls.host, cls.masterKey,
                                                                    consistency_level="Session",
                                                                    connection_policy=cls.connectionPolicy,
                                                                    logger=cls.logger_filtered_diagnostic,
                                                                    enable_diagnostics_logging=True)

    def test_default_http_logging_policy(self):
        # Test if we can log into from creating a database
        database_id = "database_test-" + str(uuid.uuid4())
        self.client_default.create_database(id=database_id)
        assert all(m.levelname == 'INFO' for m in self.mock_handler_default.messages)
        messages_request = self.mock_handler_default.messages[0].message.split("\n")
        messages_response = self.mock_handler_default.messages[1].message.split("\n")
        assert messages_request[1] == "Request method: 'GET'"
        assert 'Request headers:' in messages_request[2]
        assert messages_request[14] == 'No body was attached to the request'
        assert messages_response[0] == 'Response status: 200'
        assert 'Response headers:' in messages_response[1]

        self.mock_handler_default.reset()

        # delete database
        self.client_default.delete_database(database_id)

    def test_cosmos_http_logging_policy(self):
        # Test if we can log info from reading a database
        database_id = "database_test-" + str(uuid.uuid4())
        self.client_diagnostic.create_database(id=database_id)
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
        # Verify we only have a total of 4 logged messages: 2 from databaseaccount read and 2 from create database
        assert len(self.mock_handler_diagnostic.messages) == 4
        # Test if we can log into from creating a database
        # The request to create database should follow the databaseaccount read request immediately
        messages_request = self.mock_handler_diagnostic.messages[2]
        messages_response = self.mock_handler_diagnostic.messages[3]
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
            self.client_diagnostic.create_database(id=database_id)
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
        self.client_diagnostic.delete_database(database_id)

        self.mock_handler_diagnostic.reset()

    def test_filtered_diagnostics_logging_policy(self):
        # Test if we can log errors with the filtered diagnostics logger
        database_id = "database_test_" + str(uuid.uuid4())
        container_id = "diagnostics_container_test_" + str(uuid.uuid4())
        self.client_filtered_diagnostic.create_database(id=database_id)
        database = self.client_filtered_diagnostic.get_database_client(database_id)
        database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))

        # Try to read an item that doesn't exist
        try:
            container = database.get_container_client(container_id)
            container.read_item(item="nonexistent_item", partition_key="nonexistent_pk")
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
            container.create_item(body={"FakeProperty": "item1", "NotPk": None})
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
        self.client_filtered_diagnostic.delete_database(database_id)
        self.mock_handler_filtered_diagnostic.reset()

    def test_client_settings(self):
        # Test data
        all_locations = [L1, L2]
        client_excluded_locations = [L1]
        multiple_write_locations = True

        # Client setup
        mock_handler = MockHandler()
        logger = create_logger("test_logger_client_settings", mock_handler)

        custom_transport = FaultInjectionTransport()
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name=L1,
                second_region_name=L2,
                inner=inner,
                first_region_url=L1_URL,
                second_region_url=L2_URL,
            )
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        initialized_objects = TestFaultInjectionTransport.setup_method_with_custom_transport(
            custom_transport,
            default_endpoint=CONFIG.host,
            key=CONFIG.masterKey,
            database_id=CONFIG.TEST_DATABASE_ID,
            container_id=CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID,
            preferred_locations=all_locations,
            excluded_locations=client_excluded_locations,
            multiple_write_locations=multiple_write_locations,
            custom_logger=logger
        )
        mock_handler.reset()

        # create an item
        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value, 'pk': id_value}
        container: ContainerProxy = initialized_objects["col"]
        container.create_item(body=document_definition)

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

if __name__ == "__main__":
    unittest.main()