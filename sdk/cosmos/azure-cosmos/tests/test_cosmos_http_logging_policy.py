# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for the CosmosHttpLoggingPolicy."""
import logging
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config

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
        cls.logger_default = logging.getLogger("testloggerdefault")
        cls.logger_default.addHandler(cls.mock_handler_default)
        cls.logger_default.setLevel(logging.DEBUG)
        cls.logger_diagnostic = logging.getLogger("testloggerdiagnostic")
        cls.logger_diagnostic.addHandler(cls.mock_handler_diagnostic)
        cls.logger_diagnostic.setLevel(logging.DEBUG)
        cls.client_default = cosmos_client.CosmosClient(cls.host, cls.masterKey,
                                                        consistency_level="Session",
                                                        connection_policy=cls.connectionPolicy,
                                                        logger=cls.logger_default)
        cls.client_diagnostic = cosmos_client.CosmosClient(cls.host, cls.masterKey,
                                                           consistency_level="Session",
                                                           connection_policy=cls.connectionPolicy,
                                                           logger=cls.logger_diagnostic,
                                                           enable_diagnostics_logging=True)

    def test_default_http_logging_policy(self):
        # Test if we can log into from creating a database
        database_id = "database_test-" + str(uuid.uuid4())
        self.client_default.create_database(id=database_id)
        assert all(m.levelname == 'INFO' for m in self.mock_handler_default.messages)
        messages_request = self.mock_handler_default.messages[3].message.split("\n")
        messages_response = self.mock_handler_default.messages[4].message.split("\n")
        assert messages_request[1] == "Request method: 'GET'"
        assert 'Request headers:' in messages_request[2]
        assert messages_request[14] == 'No body was attached to the request'
        assert messages_response[0] == 'Response status: 200'
        assert 'Response headers:' in messages_response[1]

        self.mock_handler_default.reset()

        # delete database
        self.client_default.delete_database(database_id)

    def test_cosmos_http_logging_policy(self):
        # Test if we can log into from creating a database
        database_id = "database_test-" + str(uuid.uuid4())
        self.client_diagnostic.create_database(id=database_id)
        assert all(m.levelname == 'INFO' for m in self.mock_handler_diagnostic.messages)
        messages_request = self.mock_handler_diagnostic.messages[13].message.split("\n")
        messages_response = self.mock_handler_diagnostic.messages[14].message.split("\n")
        elapsed_time = self.mock_handler_diagnostic.messages[5].message.split("\n")
        assert "/dbs" in messages_request[0]
        assert messages_request[1] == "Request method: 'POST'"
        assert 'Request headers:' in messages_request[2]
        assert messages_request[15] == 'A body is sent with the request'
        assert messages_response[0] == 'Response status: 201'
        assert "Elapsed time in seconds:" in elapsed_time[0]
        assert "Response headers" in messages_response[1]

        self.mock_handler_diagnostic.reset()
        # now test in case of an error
        try:
            self.client_diagnostic.create_database(id=database_id)
        except:
            pass
        assert all(m.levelname == 'INFO' for m in self.mock_handler_diagnostic.messages)
        messages_request = self.mock_handler_diagnostic.messages[7].message.split("\n")
        messages_response = self.mock_handler_diagnostic.messages[8].message.split("\n")
        elapsed_time = self.mock_handler_diagnostic.messages[9].message.split("\n")
        assert "/dbs" in messages_request[0]
        assert messages_request[1] == "Request method: 'POST'"
        assert 'Request headers:' in messages_request[2]
        assert messages_request[15] == 'A body is sent with the request'
        assert messages_response[0] == 'Response status: 409'
        assert "Elapsed time in seconds:" in elapsed_time[0]
        assert "Response headers" in messages_response[1]

        # delete database
        self.client_diagnostic.delete_database(database_id)

        self.mock_handler_diagnostic.reset()


if __name__ == "__main__":
    unittest.main()