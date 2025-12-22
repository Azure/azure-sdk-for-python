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
from azure.cosmos.exceptions import CosmosHttpResponseError
import test_config
from _fault_injection_transport import FaultInjectionTransport
from test_fault_injection_transport import TestFaultInjectionTransport
from typing import List, Callable
from azure.core.rest import HttpRequest

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


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


def create_logger(name: str, mock_handler: test_config.MockHandler, level: int = logging.INFO) -> logging.Logger:
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
        cls.mock_handler_default = test_config.MockHandler()
        cls.mock_handler_diagnostic = test_config.MockHandler()
        cls.mock_handler_filtered_diagnostic = test_config.MockHandler()

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

        # Create a root logger with a mock handler and a filter for status codes above 400
        cls.root_mock_handler = test_config.MockHandler()
        cls.root_mock_handler.addFilter(FilterStatusCode())
        cls.root_logger = create_logger("rootLogger", cls.root_mock_handler)

        # Create child loggers
        cls.root_logger_child = logging.getLogger("rootLogger.child")
        cls.root_logger_grandchild = logging.getLogger("rootLogger.child.grandchild")

        # Use the grandchild logger for the Cosmos client
        cls.client_grandchild_logger = cosmos_client.CosmosClient(
            cls.host,
            cls.masterKey,
            consistency_level="Session",
            connection_policy=cls.connectionPolicy,
            logger=cls.root_logger_grandchild,
            enable_diagnostics_logging=True
        )

    def test_default_http_logging_policy(self):
        # Test if we can log into from creating a database
        database_id = "database_test-" + str(uuid.uuid4())
        self.client_default.create_database(id=database_id)
        assert all(m.levelname == 'INFO' for m in self.mock_handler_default.messages)
        messages_request = self.mock_handler_default.messages[0].message.split("\n")
        messages_response = self.mock_handler_default.messages[1].message.split("\n")
        assert messages_request[1] == "Request method: 'GET'"
        assert 'Request headers:' in messages_request[2]
        assert messages_request[-1] == 'No body was attached to the request'
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
        # Verify we only have a total of 6 logged messages: 2 from databaseaccount read, 2 from health check, and 2 from create database
        assert len(self.mock_handler_diagnostic.messages) == 6
        # Test if we can log into from creating a database
        # The request to create database should follow the health check request immediately
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
        mock_handler = test_config.MockHandler()
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

    def test_activity_id_logging_policy(self):
        # Create a mock handler and logger for the new client
        self.mock_handler_activity_id = test_config.MockHandler()
        self.logger_activity_id = create_logger("test_logger_activity_id", self.mock_handler_activity_id)

        # Create a new client with the logger and enable diagnostics logging
        self.client_activity_id = cosmos_client.CosmosClient(
            self.host,
            self.masterKey,
            consistency_level="Session",
            connection_policy=self.connectionPolicy,
            logger=self.logger_activity_id,
            enable_diagnostics_logging=True
        )

        # Generate a custom activity ID
        custom_activity_id = str(uuid.uuid4())

        # Create a database and container for the test
        database_id = "database_test_activity_id_" + str(uuid.uuid4())
        container_id = "container_test_activity_id_" + str(uuid.uuid4())
        database = self.client_activity_id.create_database(id=database_id)
        container = database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
        # Reset the mock handler to clear previous messages
        self.mock_handler_activity_id.reset()

        # Upsert an item and verify the request and response activity IDs match
        item_id = str(uuid.uuid4())
        item_body = {"id": item_id, "pk": item_id}
        container.upsert_item(body=item_body)

        # Verify that the request activity ID matches the response activity ID
        # Having the Request Activity confirms we generated one from SDK
        # Having it match the response means it was passed successfully
        log_record_request = self.mock_handler_activity_id.messages[0]
        log_record_response = self.mock_handler_activity_id.messages[1]
        assert log_record_request.activity_id == log_record_response.activity_id

        # Upsert another item with the custom activity ID in the initial headers
        headers = {"x-ms-activity-id": custom_activity_id}
        item_id_2 = str(uuid.uuid4())
        item_body_2 = {"id": item_id_2, "pk": item_id_2}
        container.upsert_item(body=item_body_2, initial_headers=headers)

        # Verify that the custom activity ID does not match the request activity ID from the log record
        # Users should not be able to pass in their own activity ID.
        log_record_request_2 = self.mock_handler_activity_id.messages[2]
        assert log_record_request_2.activity_id != custom_activity_id

        # Clean up by deleting the database
        self.client_activity_id.delete_database(database_id)
        self.mock_handler_activity_id.reset()

    def test_logging_exceptions_with_no_response(self):
        # Create a mock handler and logger for capturing logs
        mock_handler = test_config.MockHandler()
        logger = create_logger("test_logger_fault_injection", mock_handler)

        # Set up FaultInjectionTransport to inject a 502 error
        id_value = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}
        custom_transport = FaultInjectionTransport()
        predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_req_for_document_with_id(
            r, id_value)
        custom_transport.add_fault(predicate, lambda r: FaultInjectionTransport.error_after_delay(
            1000,
            CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error.")))


        # Initialize the client with the custom transport and logger
        initialized_objects = TestFaultInjectionTransport.setup_method_with_custom_transport(
            custom_transport,
            default_endpoint=CONFIG.host,
            key=CONFIG.masterKey,
            database_id=CONFIG.TEST_DATABASE_ID,
            container_id=CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID,
            preferred_locations=[L1, L2],
            excluded_locations=[],
            multiple_write_locations=True,
            custom_logger=logger
        )
        mock_handler.reset()

        # Attempt to create an item, which should trigger the injected 502 error
        container: ContainerProxy = initialized_objects["col"]
        try:
            container.create_item(body=document_definition)
            pytest.fail("Expected exception not thrown")
        except CosmosHttpResponseError as cosmosError:
            # Verify that the logger captured the 502 error and was called from on_exception
            assert any(m.status_code == 502 and "on_exception" in m.funcName for m in mock_handler.messages)

    def test_hierarchical_logger_with_filter(self):
        # Reset the mock handler before the test
        self.root_mock_handler.reset()

        # Attempt to read a nonexistent item
        database_id = "database_test_hierarchical_logger_" + str(uuid.uuid4())
        container_id = "container_test_hierarchical_logger_" + str(uuid.uuid4())
        database = self.client_grandchild_logger.create_database(id=database_id)
        container = database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))

        try:
            container.read_item(item="nonexistent_item", partition_key="nonexistent_pk")
        except:
            pass

        # Verify that the error was logged by the root logger's mock handler
        assert len(self.root_mock_handler.messages) == 2
        log_record = self.root_mock_handler.messages[0]
        assert hasattr(log_record, "status_code")
        assert log_record.status_code == 404
        assert log_record.name == "rootLogger.child.grandchild"
        assert not bool(self.root_logger_grandchild.filters)
        assert not bool(self.root_logger_child.filters)
        assert bool(self.root_mock_handler.filters)

        # Clean up
        self.client_grandchild_logger.delete_database(database_id)
        self.root_mock_handler.reset()

if __name__ == "__main__":
    unittest.main()
