# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import test_config
import pytest
from azure.cosmos import CosmosClient


@pytest.mark.cosmosEmulator
class TestUserAgentSuffix(unittest.TestCase):
    """Python User Agent Suffix Tests.
    """

    client: CosmosClient = None
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

    def test_user_agent_suffix_no_special_character(self):
        user_agent_suffix = "TestUserAgent"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = self.created_database.read()
        assert read_result['id'] == self.created_database.id

    def test_user_agent_suffix_special_character(self):
        user_agent_suffix = "TéstUserAgent's"  # cspell:disable-line
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = self.created_database.read()
        assert read_result['id'] == self.created_database.id

    def test_user_agent_suffix_unicode_character(self):
        user_agent_suffix = "UnicodeChar鱀InUserAgent"
        try:
            self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
            self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            self.created_database.read()
            pytest.fail("Unicode characters should not be allowed.")
        except UnicodeEncodeError as e:
            assert "ordinal not in range(256)" in e.reason

    def test_user_agent_suffix_space_character(self):
        user_agent_suffix = "UserAgent with space$%_^()*&"
        self.client = CosmosClient(self.host, self.masterKey, user_agent=user_agent_suffix)
        self.created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

        read_result = self.created_database.read()
        assert read_result['id'] == self.created_database.id


if __name__ == '__main__':
    unittest.main()
