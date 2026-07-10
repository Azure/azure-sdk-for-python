# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid

import pytest

import test_config
from azure.cosmos import CosmosClient, PartitionKey, GlobalSecondaryIndexDefinition


@pytest.mark.cosmosGSI
class TestGlobalSecondaryIndexLive(unittest.TestCase):
    """Live tests for Global Secondary Index (GSI) container operations.

    These tests require a Cosmos DB account with GSI support enabled.
    The account endpoint and key are sourced from Key Vault secrets:
    - gsi-pipeline-uri -> GSI_ACCOUNT_HOST
    - gsi-pipeline-key -> GSI_ACCOUNT_KEY
    """
    client: CosmosClient = None
    host = os.getenv('GSI_ACCOUNT_HOST', test_config.TestConfig.host)
    masterKey = os.getenv('GSI_ACCOUNT_KEY', test_config.TestConfig.masterKey)
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
        cls.test_db = cls.client.create_database(str(uuid.uuid4()))

    @classmethod
    def tearDownClass(cls):
        if cls.test_db:
            cls.client.delete_database(cls.test_db.id)

    def test_create_gsi_container(self):
        """Test creating a GSI container derived from a source container."""
        # Create source container
        source_container = self.test_db.create_container(
            id="source-container-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id")
        )

        # Create GSI container using GlobalSecondaryIndexDefinition
        gsi_definition = GlobalSecondaryIndexDefinition(
            source_container_id=source_container.id,
            definition="SELECT c.id, c.email, c.name FROM c"
        )
        gsi_container = self.test_db.create_container(
            id="gsi-container-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
            global_secondary_index_definition=gsi_definition
        )

        # Read back the container properties and verify GSI definition is present
        properties = gsi_container.read()
        self.assertIn("globalSecondaryIndexDefinition", properties)
        gsi_props = properties["globalSecondaryIndexDefinition"]
        self.assertEqual(gsi_props["sourceCollectionId"], source_container.id)
        self.assertEqual(gsi_props["definition"], "SELECT c.id, c.email, c.name FROM c")
        self.assertIn("status", gsi_props)

        # Clean up - delete GSI container first, then source
        self.test_db.delete_container(gsi_container.id)
        self.test_db.delete_container(source_container.id)

    def test_create_gsi_container_with_dict(self):
        """Test creating a GSI container using a raw dict instead of the class."""
        # Create source container
        source_container = self.test_db.create_container(
            id="source-dict-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id")
        )

        # Create GSI container using a dict
        gsi_dict = {
            "sourceCollectionId": source_container.id,
            "definition": "SELECT c.id, c.category FROM c"
        }
        gsi_container = self.test_db.create_container(
            id="gsi-dict-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
            global_secondary_index_definition=gsi_dict
        )

        # Verify
        properties = gsi_container.read()
        self.assertIn("globalSecondaryIndexDefinition", properties)

        # Clean up
        self.test_db.delete_container(gsi_container.id)
        self.test_db.delete_container(source_container.id)

    def test_create_gsi_container_if_not_exists(self):
        """Test create_container_if_not_exists with GSI definition."""
        # Create source container
        source_container = self.test_db.create_container(
            id="source-notexist-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id")
        )

        gsi_definition = GlobalSecondaryIndexDefinition(
            source_container_id=source_container.id,
            definition="SELECT c.id, c.timestamp FROM c"
        )
        container_id = "gsi-notexist-" + str(uuid.uuid4())[:8]

        # First call creates
        gsi_container = self.test_db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            global_secondary_index_definition=gsi_definition
        )
        self.assertEqual(gsi_container.id, container_id)

        # Second call returns existing
        gsi_container_again = self.test_db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            global_secondary_index_definition=gsi_definition
        )
        self.assertEqual(gsi_container_again.id, container_id)

        # Clean up
        self.test_db.delete_container(gsi_container.id)
        self.test_db.delete_container(source_container.id)


if __name__ == "__main__":
    unittest.main()
