# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosEmulator
class TestTimeToLive(unittest.TestCase):
    """TTL Unit Tests.
    """

    client = None
    created_db = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    configs = test_config.TestConfig

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)

    def test_collection_and_document_ttl_values(self):
        ttl = 10
        created_collection = self.created_db.create_container(
            id='test_ttl_values1' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id'),
            default_ttl=ttl)
        created_collection_properties = created_collection.read()
        self.assertEqual(created_collection_properties['defaultTtl'], ttl)

        collection_id = 'test_ttl_values4' + str(uuid.uuid4())
        ttl = -10

        # -10 is an unsupported value for defaultTtl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            self.created_db.create_container,
            collection_id,
            PartitionKey(path='/id'),
            None,
            ttl)

        document_definition = {'id': 'doc1' + str(uuid.uuid4()),
                               'name': 'sample document',
                               'key': 'value',
                               'ttl': 0}

        # 0 is an unsupported value for ttl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition)

        document_definition['id'] = 'doc2' + str(uuid.uuid4())
        document_definition['ttl'] = None

        # None is an unsupported value for ttl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition)

        document_definition['id'] = 'doc3' + str(uuid.uuid4())
        document_definition['ttl'] = -10

        # -10 is an unsupported value for ttl. Valid values are -1 or a non-zero positive 32-bit integer value
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition)

        self.created_db.delete_container(container=created_collection)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
