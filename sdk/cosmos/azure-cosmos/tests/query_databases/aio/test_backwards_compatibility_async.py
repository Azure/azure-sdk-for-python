# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Selected async legacy session-token compatibility test pinned to the Rust backend.

Original: tests/test_backwards_compatibility_async.py
Copy:     tests/query_databases/aio/test_backwards_compatibility_async.py
"""

import unittest
import uuid

import pytest

from config import clients, settings
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
@pytest.mark.skip(
    reason=(
        "accepted-vnext-change: API review section 5 "
        "(docs/api-review.md#5---querying-databases) excludes acceptance of ignored "
        "session_token values; this is not a driver gap. TypeError coverage: "
        "tests/common/test_query_databases_paging_unit.py::test_rejected_options_have_no_nested_bypass_rust"
    )
)
class TestBackwardsCompatibilityAsync(unittest.IsolatedAsyncioTestCase):
    configs = settings.TestSettings

    async def asyncSetUp(self):
        self.client = CosmosClient(
            self.configs.host,
            self.configs.masterKey,
            _backend="rust",
        )
        self.created_database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.data_client = clients.create_data_client_async()
        self.data_database = self.data_client.get_database_client(self.configs.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()
        await self.data_client.close()

    async def test_session_token_compatibility_async_rust(self):
        """Retain the excluded legacy acceptance check for migration traceability.

        This sweep passes non-None session tokens to database and container
        operations. API review section 5 excludes that ignored-input behavior
        for query_databases; its rejection coverage is named in the skip reason.
        This exclusion does not approve every other option-rejection proposal.
        """
        # Source: tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync.test_session_token_compatibility_async
        # Verifying that behavior is unaffected across the board for using `session_token` on irrelevant methods
        # Database
        database = await self.client.create_database(
            settings.unique_database_id("backcompat"), session_token=str(uuid.uuid4())
        )
        assert database is not None
        database2 = await self.client.create_database_if_not_exists(
            settings.unique_database_id("backcompat"), session_token=str(uuid.uuid4())
        )
        assert database2 is not None
        database_ids = {db["id"] async for db in self.client.list_databases(session_token=str(uuid.uuid4()))}
        database_ids2 = {
            db["id"]
            async for db in self.client.query_databases(query="select * from c", session_token=str(uuid.uuid4()))
        }
        assert database.id in database_ids
        assert database.id in database_ids2
        database_read = await database.read(session_token=str(uuid.uuid4()))
        assert database_read is not None
        await self.client.delete_database(database2.id, session_token=str(uuid.uuid4()))
        try:
            await database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = await self.created_database.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container is not None
        container2 = await self.created_database.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container2 is not None
        container_ids = {c["id"] async for c in self.created_database.list_containers(session_token=str(uuid.uuid4()))}
        container_ids2 = {
            c["id"]
            async for c in self.created_database.query_containers(
                query="select * from c", session_token=str(uuid.uuid4())
            )
        }
        assert container.id in container_ids
        assert container.id in container_ids2
        container2_read = await container2.read(session_token=str(uuid.uuid4()))
        assert container2_read is not None
        replace_container = await self.created_database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30, session_token=str(uuid.uuid4()))
        replace_container_read = await replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        assert replace_container_read['defaultTtl'] == 30
        await self.created_database.delete_container(replace_container.id, session_token=str(uuid.uuid4()))
        try:
            await container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        await self.client.delete_database(database.id)
