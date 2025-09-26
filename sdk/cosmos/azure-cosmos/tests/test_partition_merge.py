# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import http_constants

def response_hook(raw_response):
    header = raw_response.http_request.headers
    assert http_constants.HttpHeaders.SDKSupportedCapabilities in header
    assert header[http_constants.HttpHeaders.SDKSupportedCapabilities] == \
           http_constants.SDKSupportedCapabilities.PARTITION_MERGE

@pytest.mark.cosmosQuery
class TestPartitionMerge(unittest.TestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_CONTAINER_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.container = cls.database.get_container_client(cls.TEST_CONTAINER_ID)

    def test_header_enabled_partition_merge(self):
        # This test only runs read API to verify if the header was set correctly, because all APIs are using the same
        # base method to set the header(GetHeaders).
        self.container.read(raw_response_hook=response_hook)

if __name__ == "__main__":
    unittest.main()
