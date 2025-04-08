# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos
import test_config
from azure.cosmos import PartitionKey, cosmos_client, exceptions, http_constants


@pytest.mark.cosmosLong
class TestResourceIds(unittest.TestCase):
    client: azure.cosmos.CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)

    def test_id_unicode_validation(self):
        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        resource_id1 = u'हिन्दी भारत की राष्ट्रीय भाषा है' + str(uuid.uuid4())  # cspell:disable-line

        # Special allowed chars for Id
        resource_id2 = "!@$%^&*()-~`'_[]{}|;:,.<>" + str(uuid.uuid4())

        # verify that databases are created with specified IDs
        created_db1 = self.client.create_database_if_not_exists(resource_id1)
        created_db2 = self.client.create_database_if_not_exists(resource_id2)

        assert resource_id1 == created_db1.id
        assert resource_id2 == created_db2.id

        # verify that collections are created with specified IDs
        created_collection1 = created_db1.create_container(
            id=resource_id1,
            partition_key=PartitionKey(path='/id', kind='Hash'))
        created_collection2 = created_db2.create_container(
            id=resource_id2,
            partition_key=PartitionKey(path='/id', kind='Hash'))

        assert resource_id1 == created_collection1.id
        assert resource_id2 == created_collection2.id

        # verify that items are created with specified IDs
        item1 = created_collection1.upsert_item({"id": resource_id1})
        item2 = created_collection1.upsert_item({"id": resource_id2})

        assert resource_id1 == item1.get("id")
        assert resource_id2 == item2.get("id")

        self.client.delete_database(resource_id1)
        self.client.delete_database(resource_id2)

    def test_create_illegal_characters(self):
        database_id = str(uuid.uuid4())
        container_id = str(uuid.uuid4())
        partition_key = PartitionKey(path="/id")

        created_database = self.client.create_database(id=database_id)
        created_container = created_database.create_container(id=container_id, partition_key=partition_key)

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
            "ID_with_more_than_255" + "_add" * 255,
            "ID_with_trailing_spaces   "
        ]

        # test illegal resource id's for all resources
        for resource_id in illegal_strings:
            try:
                self.client.create_database(resource_id)
                self.fail("Database create should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            # Let service throw size exception
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '255' characters." in e.message

            try:
                created_database.create_container(id=resource_id, partition_key=partition_key)
                self.fail("Container create should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '255' characters." in e.message

            try:
                created_container.create_item({"id": resource_id})
                self.fail("Item create should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '1024' characters." in e.message

            try:
                created_container.upsert_item({"id": resource_id})
                self.fail("Item upsert should have failed for id {}".format(resource_id))
            except ValueError as e:
                assert str(e) in error_strings
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
                assert "Ensure to provide a unique non-empty string less than '1024' characters." in e.message

        self.client.delete_database(database_id)


if __name__ == '__main__':
    unittest.main()
