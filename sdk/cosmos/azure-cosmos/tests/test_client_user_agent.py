# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

from azure.cosmos import CosmosClient as sync_client
from azure.cosmos.aio import CosmosClient as async_client
from test_config import TestConfig


@pytest.mark.skip
class TestClientUserAgent(unittest.IsolatedAsyncioTestCase):

    async def test_client_user_agent(self):
        async with async_client(url=TestConfig.host, credential=TestConfig.masterKey) as client_async:
            client_sync = sync_client(url=TestConfig.host, credential=TestConfig.masterKey)

            self.assertTrue(client_sync.client_connection._user_agent.startswith("azsdk-python-cosmos/"))
            self.assertTrue(client_async.client_connection._user_agent.startswith("azsdk-python-cosmos-async/"))
            self.assertTrue(client_async.client_connection._user_agent != client_sync.client_connection._user_agent)


if __name__ == "__main__":
    unittest.main()
