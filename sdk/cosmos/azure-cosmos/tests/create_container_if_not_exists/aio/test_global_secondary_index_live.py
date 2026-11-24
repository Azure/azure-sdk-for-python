# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async counterpart of main 57f59d5d4851's GSI get-or-create assertions."""

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

    async def test_create_gsi_container_if_not_exists_async_rust(self):
        # Source: tests/test_global_secondary_index_live.py::TestGlobalSecondaryIndexLive.test_create_gsi_container_if_not_exists
        source_container = await self.test_db.create_container(
            id="source-notexist-" + str(uuid.uuid4())[:8],
            partition_key=PartitionKey(path="/id"),
        )
        gsi_definition = GlobalSecondaryIndexDefinition(
            source_container_id=source_container.id,
            definition="SELECT c.id, c.timestamp FROM c",
        )
        container_id = "gsi-notexist-" + str(uuid.uuid4())[:8]

        gsi_container = await self.test_db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            global_secondary_index=gsi_definition,
        )
        self.assertEqual(gsi_container.id, container_id)

        gsi_container_again = await self.test_db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            global_secondary_index=gsi_definition,
        )
        self.assertEqual(gsi_container_again.id, container_id)

        await self.test_db.delete_container(gsi_container.id)
        await self.test_db.delete_container(source_container.id)
