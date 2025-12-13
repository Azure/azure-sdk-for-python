# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid
import re
from typing import Any

import pytest
import test_config
from azure.cosmos.aio import CosmosClient
from test_cosmos_http_logging_policy import create_logger


@pytest.mark.cosmosEmulator
class TestUserAgentAsync(unittest.IsolatedAsyncioTestCase):
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

    async def _check(self, user_agent_kw):
        self.client = CosmosClient(self.host, self.masterKey, **user_agent_kw)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        read_result = await self.created_database.read()
        assert read_result['id'] == self.created_database.id
        await self.client.close()

    async def test_user_agent_special_characters_async(self):
        user_agents = ["TestUserAgent", "TéstUserAgent's", "UnicodeChar鱀InUserAgent", "UserAgent with space$%_^()*&"] # cspell:disable-line
        for user_agent in user_agents:
            await self._check({'user_agent': user_agent})
            await self._check({'user_agent_suffix': user_agent})

    async def test_user_agent_with_features_async(self):
        async def _run_case(use_suffix: bool):
            os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
            user_agent = "customString"
            mock_handler = test_config.MockHandler()
            logger = create_logger("testloggerdefault_async", mock_handler)
            try:
                kwargs: dict[str, Any] = {"logger": logger}
                if use_suffix:
                    kwargs["user_agent_suffix"] = user_agent
                else:
                    kwargs["user_agent"] = user_agent
                self.client = CosmosClient(self.host, self.masterKey, **kwargs)
                self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
                container = self.created_database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
                await container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
                await container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
            finally:
                os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"

            log_messages = mock_handler.messages
            for log_message in log_messages:
                msg = log_message.message
                if msg.startswith("Request URL:"):
                    m = re.search(r"'User-Agent':\s*'([^']+)'", msg, re.MULTILINE)
                    if m:
                        ua = m.group(1)
                        if use_suffix:
                            assert ua.startswith("azsdk-python-cosmos")
                            assert ua.endswith("customString | F2")
                        else:
                            assert ua.startswith("customString azsdk-python-cosmos")
                            assert ua.endswith("| F2")
            await self.client.close()

        # run both cases: prefix then suffix
        await _run_case(False)
        await _run_case(True)


if __name__ == "__main__":
    unittest.main()

