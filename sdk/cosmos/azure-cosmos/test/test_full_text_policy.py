# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import CosmosClient, PartitionKey


class TestFullTextPolicy(unittest.TestCase):
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

        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
        cls.test_db = cls.client.create_database(str(uuid.uuid4()))

    def test_create_full_text_container(self):
        return

    def test_fail_create_full_text_policy(self):
        return

    def test_fail_create_full_text_indexing_policy(self):
        return

    def test_replace_full_text_policy(self):
        return

    def test_replace_full_text_indexing_policy(self):
        return



if __name__ == '__main__':
    unittest.main()
