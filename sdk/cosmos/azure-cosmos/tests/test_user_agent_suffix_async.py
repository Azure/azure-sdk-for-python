# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import pytest
import test_config
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
class TestUserAgentSuffixAsync(unittest.IsolatedAsyncioTestCase):
    """Python User Agent Suffix Tests.
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

    async def test_user_agent_suffix_no_special_character_async(self):
        user_agent_suffix = "TestUserAgent"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id
        await self.client.close()

    async def test_user_agent_suffix_special_character_async(self):
        user_agent_suffix = "TéstUserAgent's"  # cspell:disable-line
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id
        await self.client.close()

    async def test_user_agent_suffix_unicode_character_async(self):
        user_agent_suffix = "UnicodeChar鱀InUserAgent"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id
        await self.client.close()

    async def test_user_agent_suffix_space_character_async(self):
        user_agent_suffix = "UserAgent with space$%_^()*&"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id
        await self.client.close()


if __name__ == "__main__":
    unittest.main()
