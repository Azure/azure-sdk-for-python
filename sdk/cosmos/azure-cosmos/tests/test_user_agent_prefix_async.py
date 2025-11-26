# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid
import re
import pytest
import test_config
from azure.cosmos.aio import CosmosClient
from tests.test_cosmos_http_logging_policy import create_logger


@pytest.mark.cosmosEmulator
class TestUserAgentPrefixAsync(unittest.IsolatedAsyncioTestCase):
    """Python User Agent Prefix Tests (async).
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncTearDown(self):
        # Ensure client is closed if created
        client = getattr(self, "client", None)
        if client is not None:
            await client.close()

    async def test_user_agent_prefix_no_special_character_async(self):
        user_agent_prefix = "TestUserAgent"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id

    async def test_user_agent_prefix_special_character_async(self):
        user_agent_prefix = "TéstUserAgent's"  # cspell:disable-line
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id

    async def test_user_agent_prefix_unicode_character_async(self):
        user_agent_prefix = "UnicodeChar鱀InUserAgent"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id
        await self.client.close()

    async def test_user_agent_prefix_space_character_async(self):
        user_agent_prefix = "UserAgent with space$%_^()*&"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id

    async def test_user_agent_prefix_with_features_async(self):
        os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
        user_agent_prefix = "customString"
        mock_handler_default = test_config.MockHandler()
        logger_default = create_logger("testloggerdefault_async", mock_handler_default)
        try:
            self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_prefix, logger=logger_default)
            self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
            container = self.created_database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            await container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
            await container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
        finally:
            os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"
        log_messages = mock_handler_default.messages
        counter = 0
        for log_message in log_messages:
            msg = log_message.message
            if msg.startswith("Request URL:"):
                m = re.search(r"'User-Agent':\s*'([^']+)'", msg, re.MULTILINE)
                if m:
                    ua = m.group(1)
                    assert ua.startswith("customString azsdk-python-cosmos")
                    if counter in [6, 8]:
                        assert ua.endswith("| F2")
            counter += 1


if __name__ == "__main__":
    unittest.main()

