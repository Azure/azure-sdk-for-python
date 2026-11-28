# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync resource-id tests that upsert items, re-run on the Rust path.

Source: ``tests/test_resource_id.py::TestResourceIds``. Each method keeps the
original steps and assertions; only setup changed. The key-authenticated setup
client and the data client both use ``_backend="rust"``. The originals create
their own uniquely named databases; any that a failed test leaves behind are
deleted afterwards.
"""

import unittest
import uuid

import pytest

import azure.cosmos
from azure.cosmos import PartitionKey, exceptions, http_constants
from config import clients
from config.settings import unique_database_id


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestResourceIds(unittest.TestCase):
    client: azure.cosmos.CosmosClient = None
    last_headers = []

    def setUp(self):
        self.key_client = clients.create_setup_client(_backend="rust")
        self.addCleanup(self.key_client.close)
        self.client = clients.create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self._owned_database_ids = []
        self.addCleanup(self._delete_owned_databases)

    def _unique_database_id(self, label=""):
        database_id = unique_database_id(("upsert_item_" + label) if label else "upsert_item")
        self._owned_database_ids.append(database_id)
        return database_id

    def _delete_owned_databases(self):
        for database_id in self._owned_database_ids:
            try:
                self.key_client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass

    def test_id_unicode_validation_rust(self):
        # Source: tests/test_resource_id.py::TestResourceIds.test_id_unicode_validation
        # Ids are prefixed so the databases are attributable to this run; the unicode and
        # special-character content this test exercises is preserved verbatim after it.
        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        resource_id1 = self._unique_database_id("unicode") + (
            u'\u0939\u093f\u0928\u094d\u0926\u0940 '
            u'\u092d\u093e\u0930\u0924 '
            u'\u0915\u0940 '
            u'\u0930\u093e\u0937\u094d\u091f\u094d\u0930\u0940\u092f '
            u'\u092d\u093e\u0937\u093e '
            u'\u0939\u0948'
        )
        self._owned_database_ids.append(resource_id1)

        # Special allowed chars for Id
        resource_id2 = self._unique_database_id("special-chars") + "!@$%^&*()-~`'_[]{}|;:,.<>"
        self._owned_database_ids.append(resource_id2)

        # verify that databases are created with specified IDs
        created_db1 = self.key_client.create_database_if_not_exists(resource_id1)
        created_db2 = self.key_client.create_database_if_not_exists(resource_id2)

        assert resource_id1 == created_db1.id
        assert resource_id2 == created_db2.id

        # verify that collections are created with specified IDs
        created_collection1_ref = created_db1.create_container(
            id=resource_id1,
            partition_key=PartitionKey(path='/id', kind='Hash'))
        created_collection2_ref = created_db2.create_container(
            id=resource_id2,
            partition_key=PartitionKey(path='/id', kind='Hash'))

        created_collection1 = self.client.get_database_client(resource_id1).get_container_client(created_collection1_ref.id)
        created_collection2 = self.client.get_database_client(resource_id2).get_container_client(created_collection2_ref.id)

        assert resource_id1 == created_collection1.id
        assert resource_id2 == created_collection2.id

        # verify that items are created with specified IDs
        item1 = created_collection1.upsert_item({"id": resource_id1})
        item2 = created_collection1.upsert_item({"id": resource_id2})

        assert resource_id1 == item1.get("id")
        assert resource_id2 == item2.get("id")

        self.key_client.delete_database(resource_id1)
        self.key_client.delete_database(resource_id2)

    def test_create_illegal_characters_rust(self):
        # Source: tests/test_resource_id.py::TestResourceIds.test_create_illegal_characters
        database_id = self._unique_database_id()
        container_id = str(uuid.uuid4())
        partition_key = PartitionKey(path="/id")

        created_database = self.key_client.create_database(id=database_id)
        created_container_ref = created_database.create_container(id=container_id, partition_key=partition_key)
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
            "ID_with_more_than_255" + "_add" * 255,
            "ID_with_trailing_spaces   "
        ]

        # test illegal resource id's for all resources
        for resource_id in illegal_strings:
            try:
                self.key_client.create_database(resource_id)
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

        self.key_client.delete_database(database_id)


if __name__ == '__main__':
    unittest.main()
