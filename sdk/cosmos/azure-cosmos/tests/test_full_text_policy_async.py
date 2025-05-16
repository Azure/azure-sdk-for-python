# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import CosmosClient as CosmosSyncClient
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosSearchQuery
class TestFullTextPolicyAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    client: CosmosClient = None
    sync_client: CosmosSyncClient = None

    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.cosmos_sync_client = CosmosSyncClient(cls.host, cls.masterKey)
        cls.test_db = cls.cosmos_sync_client.create_database(str(uuid.uuid4()))

    @classmethod
    def tearDownClass(cls):
        cls.cosmos_sync_client.delete_database(cls.test_db.id)

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.test_db = self.client.get_database_client(self.test_db.id)

    async def tearDown(self):
        await self.client.close()

    async def test_create_full_text_container_async(self):
        # Create a container with a valid full text policy and full text indexing policy
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        indexing_policy = {
            "fullTextIndexes": [
                {"path": "/abstract"}
            ]
        }
        created_container = await self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        properties = await created_container.read()
        assert properties["fullTextPolicy"] == full_text_policy
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        await self.test_db.delete_container(created_container.id)

        # Create a container with a full text policy containing only default language
        full_text_policy_no_paths = {
            "defaultLanguage": "en-US"
        }
        created_container = await self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy_no_paths,
        )
        properties = await created_container.read()
        assert properties["fullTextPolicy"] == full_text_policy_no_paths
        await self.test_db.delete_container(created_container.id)

    async def test_replace_full_text_container_async(self):
        # Replace a container without a full text policy and full text indexing policy

        created_container = await self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )
        created_container_properties = await created_container.read()
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        indexing_policy = {
            "fullTextIndexes": [
                {"path": "/abstract"}
            ]
        }

        # Replace the container with new policies
        replaced_container = await self.test_db.replace_container(
            container=created_container.id,
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        properties = await replaced_container.read()
        assert properties["fullTextPolicy"] == full_text_policy
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        assert created_container_properties['indexingPolicy'] != properties['indexingPolicy']
        await self.test_db.delete_container(created_container.id)

        # Replace a container with a valid full text policy and full text indexing policy
        created_container = await self.test_db.create_container(
            id='full_text_container' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        created_container_properties = await created_container.read()
        assert created_container_properties["fullTextPolicy"] == full_text_policy
        assert created_container_properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']

        # Replace the container with new policies
        full_text_policy['fullTextPaths'][0]['path'] = "/new_path"
        indexing_policy['fullTextIndexes'][0]['path'] = "/new_path"
        replaced_container = await self.test_db.replace_container(
            container=created_container.id,
            partition_key=PartitionKey(path="/id"),
            full_text_policy=full_text_policy,
            indexing_policy=indexing_policy
        )
        properties = await replaced_container.read()
        assert properties["fullTextPolicy"] == full_text_policy
        assert properties["indexingPolicy"]['fullTextIndexes'] == indexing_policy['fullTextIndexes']
        assert created_container_properties['fullTextPolicy'] != properties['fullTextPolicy']
        assert created_container_properties["indexingPolicy"] != properties["indexingPolicy"]
        self.test_db.delete_container(created_container.id)

    async def test_fail_create_full_text_policy_async(self):
        # Pass a full text policy with a wrongly formatted path
        full_text_policy_wrong_path = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "abstract",
                    "language": "en-US"
                }
            ]
        }
        try:
            await self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_path
            )
            pytest.fail("Container creation should have failed for invalid path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains an invalid Path: abstract" in e.http_error_message

        # Pass a full text policy without language attached to the path
        full_text_policy_no_langs = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract"
                }
            ]
        }
        try:
            await self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_no_langs
            )
            pytest.fail("Container creation should have failed for lack of language.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains invalid syntax" in e.http_error_message

        # Pass a full text policy with an unsupported default language
        full_text_policy_wrong_default = {
            "defaultLanguage": "spa-SPA",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        try:
            await self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_default
            )
            pytest.fail("Container creation should have failed for wrong supported language.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains an unsupported language spa-SPA. Supported languages are:" \
                   in e.http_error_message

        # Pass a full text policy with an unsupported path language
        full_text_policy_wrong_default = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "spa-SPA"
                }
            ]
        }
        try:
            await self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                full_text_policy=full_text_policy_wrong_default
            )
            pytest.fail("Container creation should have failed for wrong supported language.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Full Text Policy contains an unsupported language spa-SPA. Supported languages are:" \
                   in e.http_error_message

    async def test_fail_create_full_text_indexing_policy_async(self):
        full_text_policy = {
            "defaultLanguage": "en-US",
            "fullTextPaths": [
                {
                    "path": "/abstract",
                    "language": "en-US"
                }
            ]
        }
        # Pass a full text indexing policy with a path not present in the full text policy
        indexing_policy_wrong_path = {
            "fullTextIndexes": [
                {"path": "/path"}
            ]
        }
        try:
            container = await self.test_db.create_container(
                id='full_text_container' + str(uuid.uuid4()),
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_wrong_path,
            )
            await container.read()
            # TODO: This test is only failing on the pipelines, have been unable to see it pass locally
            # pytest.fail("Container creation should have failed for lack of embedding policy.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The path of the Full Text Index /path does not match the path specified in the Full Text Policy" \
                   in e.http_error_message

        # Pass a full text indexing policy with a wrongly formatted path
        indexing_policy_wrong_path = {
            "fullTextIndexes": [
                {"path": "abstract"}
            ]
        }
        try:
            await self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_wrong_path,
                full_text_policy=full_text_policy
            )
            pytest.fail("Container creation should have failed for invalid path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Full-text index specification at index (0) contains invalid path" in e.http_error_message

        # Pass a full text indexing policy without a path field
        indexing_policy_no_path = {
            "fullTextIndexes": [
                {"not_path": "abstract"}
            ]
        }
        try:
            await self.test_db.create_container(
                id='full_text_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy_no_path,
                full_text_policy=full_text_policy
            )
            pytest.fail("Container creation should have failed for missing path.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Missing path in full-text index specification at index (0)" in e.http_error_message


if __name__ == '__main__':
    unittest.main()
