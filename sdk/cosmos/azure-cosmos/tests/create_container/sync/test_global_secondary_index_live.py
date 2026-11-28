# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Creation assertions copied from main e1c0306c77b2: test_global_secondary_index_live.py."""

import os
import uuid

import pytest
from azure.cosmos import CosmosClient, GlobalSecondaryIndexDefinition, PartitionKey
from create_container._setup import SyncCreationCase


@pytest.mark.cosmosGSI
class TestGlobalSecondaryIndexLive(SyncCreationCase):

    def _create_client(self):
        return CosmosClient(
            os.environ["GSI_ACCOUNT_HOST"],
            os.environ["GSI_ACCOUNT_KEY"],
            _backend="rust",
        )

    def test_create_gsi_container_rust(self):
        """Test creating a GSI container derived from a source container."""
        source_container = self.test_db.create_container(
            id="source-container-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
        )
        gsi_definition = GlobalSecondaryIndexDefinition(
            source_container_id=source_container.id,
            definition="SELECT c.id, c.email, c.name FROM c",
        )
        gsi_container, create_properties = self.test_db.create_container(
            id="gsi-container-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
            global_secondary_index=gsi_definition,
            return_properties=True,
        )
        self.assertIn("globalSecondaryIndexDefinition", create_properties)
        self.assertNotIn("materializedViewDefinition", create_properties)
        properties = gsi_container.read()
        self.assertIn("globalSecondaryIndexDefinition", properties)
        self.assertNotIn("materializedViewDefinition", properties)
        gsi_props = properties["globalSecondaryIndexDefinition"]
        self.assertEqual(gsi_props["sourceCollectionId"], source_container.id)
        self.assertEqual(gsi_props["definition"], "SELECT c.id, c.email, c.name FROM c")
        if "status" in gsi_props:
            self.assertIsNotNone(gsi_props["status"])
        self.test_db.delete_container(gsi_container.id)
        self.test_db.delete_container(source_container.id)

    def test_create_gsi_container_with_dict_rust(self):
        """Test creating a GSI container using a raw dict instead of the class."""
        source_container = self.test_db.create_container(
            id="source-dict-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
        )
        gsi_dict = {
            "sourceCollectionId": source_container.id,
            "definition": "SELECT c.id, c.category FROM c",
        }
        gsi_container = self.test_db.create_container(
            id="gsi-dict-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
            global_secondary_index=gsi_dict,
        )
        properties = gsi_container.read()
        self.assertIn("globalSecondaryIndexDefinition", properties)
        self.test_db.delete_container(gsi_container.id)
        self.test_db.delete_container(source_container.id)
