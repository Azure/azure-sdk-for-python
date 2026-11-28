# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Creation assertions copied from main e1c0306c77b2: test_global_secondary_index_live.py."""

import os
import uuid

import pytest
from azure.cosmos import GlobalSecondaryIndexDefinition, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from create_container._setup import AsyncCreationCase


@pytest.mark.cosmosGSI
class TestGlobalSecondaryIndexLiveAsync(AsyncCreationCase):

    def _create_client(self):
        return AsyncCosmosClient(
            os.environ["GSI_ACCOUNT_HOST"],
            os.environ["GSI_ACCOUNT_KEY"],
            _backend="rust",
        )

    async def test_create_gsi_container_async_rust(self):
        """Test creating a GSI container derived from a source container."""
        source_container = await self.test_db.create_container(
            id="source-container-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
        )
        gsi_definition = GlobalSecondaryIndexDefinition(
            source_container_id=source_container.id,
            definition="SELECT c.id, c.email, c.name FROM c",
        )
        gsi_container, create_properties = await self.test_db.create_container(
            id="gsi-container-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
            global_secondary_index=gsi_definition,
            return_properties=True,
        )
        self.assertIn("globalSecondaryIndexDefinition", create_properties)
        self.assertNotIn("materializedViewDefinition", create_properties)
        properties = await gsi_container.read()
        self.assertIn("globalSecondaryIndexDefinition", properties)
        self.assertNotIn("materializedViewDefinition", properties)
        gsi_props = properties["globalSecondaryIndexDefinition"]
        self.assertEqual(gsi_props["sourceCollectionId"], source_container.id)
        self.assertEqual(gsi_props["definition"], "SELECT c.id, c.email, c.name FROM c")
        if "status" in gsi_props:
            self.assertIsNotNone(gsi_props["status"])
        await self.test_db.delete_container(gsi_container.id)
        await self.test_db.delete_container(source_container.id)

    async def test_create_gsi_container_with_dict_async_rust(self):
        """Test creating a GSI container using a raw dict instead of the class."""
        source_container = await self.test_db.create_container(
            id="source-dict-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
        )
        gsi_dict = {
            "sourceCollectionId": source_container.id,
            "definition": "SELECT c.id, c.category FROM c",
        }
        gsi_container = await self.test_db.create_container(
            id="gsi-dict-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
            global_secondary_index=gsi_dict,
        )
        properties = await gsi_container.read()
        self.assertIn("globalSecondaryIndexDefinition", properties)
        await self.test_db.delete_container(gsi_container.id)
        await self.test_db.delete_container(source_container.id)
