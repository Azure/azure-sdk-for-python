# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of the async transactional-batch tests that seed items with upsert_item.

Setup owns a unique database (key-authenticated Rust client for containers, Rust data
client for item operations) and always deletes it. Test bodies are unchanged.
"""

import unittest
import uuid

import pytest

from azure.cosmos import exceptions, PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from config.clients import create_data_client_async
from config.settings import TestSettings, unique_database_id


def get_subpartition_item(item_id):
    return {'id': item_id,
            'key': 'value',
            'state': 'WA',
            'city': 'Redmond',
            'zipcode': '98052'}


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestTransactionalBatchAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copies of tests/test_transactional_batch_async.py::TestTransactionalBatchAsync."""

    configs = TestSettings
    host = configs.host
    masterKey = configs.masterKey

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = unique_database_id("upsert-batch-async")
        # Key-auth client for control-plane (database and container create/delete)
        self.key_client = CosmosClient(self.host, self.masterKey, _backend="rust")
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.key_database = await self.key_client.create_database(self.TEST_DATABASE_ID)
        self.addAsyncCleanup(self.key_client.delete_database, self.TEST_DATABASE_ID)

        # Data client for data-plane operations (batch execute, create_item, read, etc.)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self.test_database = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def _create_container_for_test(self, container_id, partition_key):
        """Create container via key-auth, return data-plane proxy."""
        await self.key_database.create_container(id=container_id, partition_key=partition_key)
        return self.test_database.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id):
        """Delete container via key-auth."""
        await self.key_database.delete_container(container_id)

    async def test_batch_lsn_async_rust(self):
        # Source: tests/test_transactional_batch_async.py::TestTransactionalBatchAsync.test_batch_lsn_async
        cid = "batch_lsn_async" + str(uuid.uuid4())
        container = await self._create_container_for_test(cid, PartitionKey(path="/company"))
        # Create test items
        await container.upsert_item({"id": "read_item", "company": "Microsoft"})
        await container.upsert_item({"id": "replace_item", "company": "Microsoft", "value": 0})
        await container.upsert_item({"id": "patch_item", "company": "Microsoft"})
        await container.upsert_item({"id": "delete_item", "company": "Microsoft"})

        read_response = await container.read_item(item="read_item", partition_key="Microsoft")
        lsn = read_response.get_response_headers().get(HttpHeaders.LSN)

        batch = [("create", ({"id": "create_item", "company": "Microsoft"},)),
                 ("replace", ("replace_item", {"id": "replace_item", "company": "Microsoft", "value": True})),
                 ("upsert", ({"id": "upsert_item", "company": "Microsoft"},)),
                 ("patch", ("patch_item", [{"op": "add", "path": "/favorite_color", "value": "red"}])),
                 ("read", ("read_item",)),
                 ("delete", ("delete_item",))]

        batch_response = await container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 6
        assert int(lsn) == int(batch_response.get_response_headers().get(HttpHeaders.LSN)) - 1

        await self._delete_container_for_test(cid)

    async def test_batch_subpartition_rust(self):
        # Source: tests/test_transactional_batch_async.py::TestTransactionalBatchAsync.test_batch_subpartition
        cid = "batch_subpartition" + str(uuid.uuid4())
        container = await self._create_container_for_test(
            cid, PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"))
        item_ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        await container.upsert_item({'id': item_ids[0], 'key': 'value',
                                     'state': 'WA',
                                     'city': 'Redmond',
                                     'zipcode': '98052'})
        await container.upsert_item({'id': item_ids[1], 'key': 'value',
                                     'state': 'WA',
                                     'city': 'Redmond',
                                     'zipcode': '98052'})
        await container.upsert_item({'id': item_ids[2],
                                     'key': 'value',
                                     'state': 'WA',
                                     'city': 'Redmond',
                                     'zipcode': '98052'})

        batch = [("create", (get_subpartition_item(str(uuid.uuid4())),)),
                 ("replace", (item_ids[0], {"id": item_ids[0],
                                            'state': 'WA',
                                            'city': 'Redmond',
                                            'zipcode': '98052',
                                            'replaced': True})),
                 ("upsert", (get_subpartition_item(str(uuid.uuid4())),)),
                 ("patch", (item_ids[1], [{"op": "add", "path": "/favorite_color", "value": "red"}])),
                 ("read", (item_ids[2],)),
                 ("delete", (item_ids[2],))]

        batch_response = await container.execute_item_batch(batch_operations=batch,
                                                            partition_key=["WA", "Redmond", "98052"])
        assert len(batch_response) == 6

        # try to use incomplete key
        # Known divergence (unnumbered; "Transactional batch review" in docs/V5/api-review/RUST_PARITY_PUSHBACKS.md, confirmed wrapper defect): on Rust the incomplete-key batch returns an invalid statusCode=-1 that Python accepts as success, so no 400 is raised and self.fail runs.
        try:
            await container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond"])
            self.fail("Request should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Partition key provided either doesn't correspond to " \
                   "definition in the collection or doesn't match partition key " \
                   "field values specified in the document." in e.message

        await self._delete_container_for_test(cid)


if __name__ == "__main__":
    unittest.main()
