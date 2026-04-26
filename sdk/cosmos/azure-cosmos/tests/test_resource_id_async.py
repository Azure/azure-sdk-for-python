# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import PartitionKey, http_constants, exceptions
from azure.cosmos.aio import CosmosClient, DatabaseProxy


@pytest.mark.cosmosLong
@pytest.mark.cosmosAAD
class TestResourceIdsAsync(unittest.IsolatedAsyncioTestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client: CosmosClient = None
    key_client: CosmosClient = None
    created_database: DatabaseProxy = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.key_client = CosmosClient(self.host, self.masterKey)
        self.client = test_config.TestConfig.create_data_client_async()

    async def asyncTearDown(self):
        await self.client.close()
        await self.key_client.close()

    async def test_id_unicode_validation_async(self):
        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        resource_id1 = u'à¤¹à¤¿à¤¨à¥à¤¦à¥€ à¤­à¤¾à¤°à¤¤ à¤•à¥€ à¤°à¤¾à¤·à¥à¤Ÿà¥à¤°à¥€à¤¯ à¤­à¤¾à¤·à¤¾ à¤¹à¥ˆ' + str(uuid.uuid4())  # cspell:disable-line

        # Special allowed chars for Id
        resource_id2 = "!@$%^&*()-~`'_[]{}|;:,.<>" + str(uuid.uuid4())

        # verify that databases are created with specified IDs (control-plane â†’ key_client)
        created_db1 = await self.key_client.create_database_if_not_exists(resource_id1)
        created_db2 = await self.key_client.create_database_if_not_exists(resource_id2)

        assert resource_id1 == created_db1.id
        assert resource_id2 == created_db2.id

        # verify that collections are created with specified IDs (control-plane â†’ key_client db)
        created_collection1_ref = await created_db1.create_container(
            id=resource_id1,
            partition_key=PartitionKey(path='/id', kind='Hash'))
        created_collection2_ref = await created_db2.create_container(
            id=resource_id2,
            partition_key=PartitionKey(path='/id', kind='Hash'))

        assert resource_id1 == created_collection1_ref.id
        assert resource_id2 == created_collection2_ref.id

        # Get data-plane container proxies via AAD client
        created_collection1 = self.client.get_database_client(resource_id1).get_container_client(created_collection1_ref.id)
        created_collection2 = self.client.get_database_client(resource_id2).get_container_client(created_collection2_ref.id)

        # verify that items are created with specified IDs (data-plane â†’ AAD client)
        item1 = await created_collection1.upsert_item({"id": resource_id1})
        item2 = await created_collection1.upsert_item({"id": resource_id2})

        assert resource_id1 == item1.get("id")
        assert resource_id2 == item2.get("id")

        # Cleanup (control-plane â†’ key_client)
        await self.key_client.delete_database(resource_id1)
        await self.key_client.delete_database(resource_id2)

    async def test_create_illegal_characters_async(self):
        database_id = str(uuid.uuid4())
        container_id = str(uuid.uuid4())
        partition_key = PartitionKey(path="/id")

        # Control-plane: create database and container via key_client
        created_database = await self.key_client.create_database(id=database_id)
        created_container_ref = await created_database.create_container(id=container_id, partition_key=partition_key)
        # Data-plane container via AAD client
        created_container = self.client.get_database_client(database_id).get_container_client(created_container_ref.id)

        # Define errors returned by checks
        error_strings = ['Id contains illegal chars.', 'Id ends with a space or newline.']

        # Define illegal strings
        illegal_strings = [
            "ID_with_back/slash",
            "ID_\\with_forward_slashes",
            "ID_with_question?_mark",
            "ID_with_#pound",
            "ID_with_tab\t",
            "ID\r_with_return_carriage",
            "ID_with_newline\n",
            "ID_with_newline\n2",
            "ID_with_more_than_255" + "_added" * 255,
            "ID_with_trailing_spaces   "
        ]

        # test illegal resource id's for all resources
        for resource_id in illegal_strings:
            # Database create is control-plane â†’ key_client
            try:
                await self.key_client.create_database(resource_id)
                self.fail("Database create should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '255' characters." in e.message

            # Container create is control-plane â†’ key_client db
            try:
                await created_database.create_container(id=resource_id, partition_key=partition_key)
                self.fail("Container create should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '255' characters." in e.message

            # Item create is data-plane â†’ AAD client container
            try:
                await created_container.create_item({"id": resource_id})
                self.fail("Item create should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '1024' characters." in e.message

            # Item upsert is data-plane â†’ AAD client container
            try:
                await created_container.upsert_item({"id": resource_id})
                self.fail("Item upsert should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '1024' characters." in e.message

        # Cleanup (control-plane â†’ key_client)
        await self.key_client.delete_database(created_database)


if __name__ == '__main__':
    unittest.main()
