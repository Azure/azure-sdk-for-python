# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import unittest
import uuid
import re
from typing import Optional

import test_config
import pytest
from azure.cosmos import CosmosClient
from tests.test_cosmos_http_logging_policy import create_logger


@pytest.mark.cosmosEmulator
class TestUserAgentPrefix(unittest.TestCase):
    """Python User Agent Prefix Tests.
    """

    client: Optional[CosmosClient] = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    def test_user_agent_prefix_no_special_character(self):
        user_agent_prefix = "TestUserAgent"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = self.created_database.read()
        assert read_result['id'] == self.created_database.id

    def test_user_agent_prefix_special_character(self):
        user_agent_prefix = "TéstUserAgent's"  # cspell:disable-line
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = self.created_database.read()
        assert read_result['id'] == self.created_database.id

    def test_user_agent_prefix_unicode_character(self):
        user_agent_prefix = "UnicodeChar鱀InUserAgent"
        try:
            self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
            self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            self.created_database.read()
            pytest.fail("Unicode characters should not be allowed.")
        except UnicodeEncodeError as e:
            assert "ordinal not in range(256)" in e.reason

    def test_user_agent_prefix_space_character(self):
        user_agent_prefix = "UserAgent with space$%_^()*&"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = self.created_database.read()
        assert read_result['id'] == self.created_database.id

    def test_user_agent_prefix_with_features(self):
        os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
        user_agent_prefix = "customString"
        mock_handler_default = test_config.MockHandler()
        logger_default = create_logger("testloggerdefault", mock_handler_default)
        try:
            self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix, logger=logger_default)
            self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = self.created_database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
            container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
        finally:
            os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"
        log_messages = mock_handler_default.messages
        # Parse the log block starting with "Request URL:" and extract the User-Agent header
        counter = 0
        for log_message in log_messages:
            msg = log_message.message
            if msg.startswith("Request URL:"):
                # Find the User-Agent header in this message block
                m = re.search(r"'User-Agent':\s*'([^']+)'", msg, re.MULTILINE)
                if m:
                    ua = m.group(1)
                    assert ua.startswith("customString azsdk-python-cosmos")
                    if counter in [6, 8]:
                        assert ua.endswith("| F2")
            counter += 1

if __name__ == '__main__':
    unittest.main()
