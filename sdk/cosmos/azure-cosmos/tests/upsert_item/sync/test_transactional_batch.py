# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of the sync transactional-batch tests that seed items with upsert_item.

Setup owns a unique database (key-authenticated Rust client for containers, Rust data
client for item operations) and always deletes it. Test bodies are unchanged.
"""

import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions, PartitionKey, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from config.clients import create_data_client, create_setup_client
from config.settings import unique_database_id


def get_subpartition_item(item_id):
    return {'id': item_id,
            'key': 'value',
            'state': 'WA',
            'city': 'Redmond',
            'zipcode': '98052'}


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestTransactionalBatch(unittest.TestCase):
    """Rust-path copies of tests/test_transactional_batch.py::TestTransactionalBatch."""

    client: CosmosClient = None
    key_client: CosmosClient = None
    test_database: DatabaseProxy = None
    key_database: DatabaseProxy = None

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("upsert-batch")
        cls.key_client = create_setup_client(_backend="rust")
        cls.addClassCleanup(cls.key_client.close)
        cls.key_database = cls.key_client.create_database(cls.TEST_DATABASE_ID)
        cls.addClassCleanup(cls.key_client.delete_database, cls.TEST_DATABASE_ID)
        cls.client = create_data_client(_backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls.test_database = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via key-auth setup client (control-plane), return data-plane proxy."""
        self.key_database.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.test_database.get_container_client(container_id)

    def _delete_container_for_test(self, container_id):
        """Delete container via key-auth setup client (control-plane)."""
        self.key_database.delete_container(container_id)

    def test_batch_lsn_rust(self):
        # Source: tests/test_transactional_batch.py::TestTransactionalBatch.test_batch_lsn
        container = self._create_container_for_test("batch_lsn" + str(uuid.uuid4()),
                                                    partition_key=PartitionKey(path="/company"))
        # create test items
        container.upsert_item({"id": "read_item", "company": "Microsoft"})
        container.upsert_item({"id": "replace_item", "company": "Microsoft", "value": 0})
        container.upsert_item({"id": "patch_item", "company": "Microsoft"})
        container.upsert_item({"id": "delete_item", "company": "Microsoft"})

        read_response = container.read_item(item="read_item", partition_key="Microsoft")
        lsn = read_response.get_response_headers().get(HttpHeaders.LSN)

        batch = [("create", ({"id": "create_item", "company": "Microsoft"},)),
                 ("replace", ("replace_item", {"id": "replace_item", "company": "Microsoft", "value": True})),
                 ("upsert", ({"id": "upsert_item", "company": "Microsoft"},)),
                 ("patch", ("patch_item", [{"op": "add", "path": "/favorite_color", "value": "red"}])),
                 ("read", ("read_item",)),
                 ("delete", ("delete_item",))]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 6
        assert int(lsn) == int(batch_response.get_response_headers().get(HttpHeaders.LSN)) - 1

        self._delete_container_for_test(container.id)

    def test_batch_subpartition_rust(self):
        # Source: tests/test_transactional_batch.py::TestTransactionalBatch.test_batch_subpartition
        container = self._create_container_for_test(
            "batch_subpartition" + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"))
        item_ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        container.upsert_item({'id': item_ids[0],
                               'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        container.upsert_item({'id': item_ids[1],
                               'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        container.upsert_item({'id': item_ids[2],
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

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond", "98052"])
        assert len(batch_response) == 6

        # try to use incomplete key
        # Known divergence (unnumbered; "Transactional batch review" in docs/V5/api-review/RUST_PARITY_PUSHBACKS.md, confirmed wrapper defect): on Rust the incomplete-key batch returns an invalid statusCode=-1 that Python accepts as success, so no 400 is raised and self.fail runs.
        try:
            container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond"])
            self.fail("Request should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Partition key provided either doesn't correspond to " \
                   "definition in the collection or doesn't match partition key " \
                   "field values specified in the document." in e.message

        self._delete_container_for_test(container.id)


if __name__ == '__main__':
    unittest.main()
