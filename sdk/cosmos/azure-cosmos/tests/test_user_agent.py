# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import unittest
import uuid
import re
from typing import Optional, Any

import test_config
import pytest
from azure.cosmos import CosmosClient
from test_cosmos_http_logging_policy import create_logger


@pytest.mark.cosmosEmulator
class TestUserAgent(unittest.TestCase):
    """Python User Agent Prefix/Suffix Tests (sync)."""

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

    def _check(self, user_agent_kw: dict[str, Any]) -> None:
        self.client = CosmosClient(self.host, self.masterKey, **user_agent_kw)
        created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
        read_result = created_database.read()
        assert read_result['id'] == created_database.id

    def test_user_agent_special_characters(self):
        # Values cover normal, accented, apostrophe, unicode, and spaces / symbols
        user_agents = ["TestUserAgent", "TéstUserAgent's", "UserAgent with space$%_^()*&"] # cspell:disable-line
        for ua in user_agents:
            # Prefix usage
            self._check({'user_agent': ua})
            # Suffix usage
            self._check({'user_agent_suffix': ua})

        # Explicit negative test for disallowed unicode (same logic as previous unicode test)
        bad = "UnicodeChar鱀InUserAgent"  # expecting potential encode issues when used as prefix
        try:
            # Prefix usage
            self._check({'user_agent': bad})
            # Suffix usage
            self._check({'user_agent_suffix': bad})
            pytest.fail("Unicode characters should not be allowed.")
        except UnicodeEncodeError as e:
            assert "ordinal not in range(256)" in e.reason

    def test_user_agent_with_features(self):
        def _run_case(use_suffix: bool) -> None:
            os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
            user_agent_value = "customString"
            mock_handler = test_config.MockHandler()
            logger = create_logger("testloggerdefault_sync", mock_handler)
            try:
                kwargs: dict[str, Any] = {"logger": logger}
                if use_suffix:
                    kwargs["user_agent_suffix"] = user_agent_value
                else:
                    kwargs["user_agent"] = user_agent_value
                self.client = CosmosClient(self.host, self.masterKey, **kwargs)
                created_database = self.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
                container = created_database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
                container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
                container.create_item(body={"id": "testItem" + str(uuid.uuid4()), "content": "testContent"})
            finally:
                os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"

            # Examine log messages for User-Agent header
            for log_message in mock_handler.messages:
                msg = log_message.message
                if msg.startswith("Request URL:"):
                    m = re.search(r"'User-Agent':\s*'([^']+)'", msg, re.MULTILINE)
                    if m:
                        ua = m.group(1)
                        if use_suffix:
                            # Suffix case: SDK core first then suffix at end
                            assert ua.startswith("azsdk-python-cosmos")
                            assert ua.endswith("customString | F2")
                        else:
                            # Prefix case: custom part first
                            assert ua.startswith("customString azsdk-python-cosmos")
                            assert ua.endswith("| F2")

        _run_case(False)  # prefix scenario
        _run_case(True)   # suffix scenario


if __name__ == '__main__':
    unittest.main()
