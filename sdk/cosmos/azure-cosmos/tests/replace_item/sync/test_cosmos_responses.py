# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync point-operation header test that replaces an item, re-run on the Rust path.

Source: ``tests/test_cosmos_responses.py::TestCosmosResponses``. The method keeps
the original steps and assertions; only setup changed. Both clients use
``_backend="rust"``: a key-authenticated setup client owns a uniquely named
database (deleted afterwards) and a data client runs the item operations, like
the original key/data client pair.
"""

import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy, DatabaseProxy
from config import clients
from config.settings import unique_database_id


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestCosmosResponses(unittest.TestCase):
    """Python Cosmos Responses Tests.
    """

    client: CosmosClient = None
    data_client: CosmosClient = None
    test_database: DatabaseProxy = None
    data_test_database: DatabaseProxy = None

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("replace_item_responses")
        cls.client = clients.create_setup_client(_backend="rust")
        try:
            cls.test_database = cls.client.create_database(cls.TEST_DATABASE_ID)
            cls.data_client = clients.create_data_client(_backend="rust")
            cls.data_test_database = cls.data_client.get_database_client(cls.TEST_DATABASE_ID)
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.test_database is not None:
                cls.client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            if cls.data_client is not None:
                cls.data_client.close()
            cls.client.close()

    def test_point_operation_headers_rust(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_point_operation_headers
        # Container create stays on key-auth (control-plane); data ops route through AAD.
        container_id = "responses_test" + str(uuid.uuid4())
        self.test_database.create_container(id=container_id,
                                            partition_key=PartitionKey(path="/company"))
        container = self.data_test_database.get_container_client(container_id)
        first_response = container.upsert_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        lsn = first_response.get_response_headers()['lsn']

        create_response = container.create_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        assert len(create_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(create_response.get_response_headers()['lsn'])
        lsn = create_response.get_response_headers()['lsn']

        read_response = container.read_item(create_response['id'], create_response['company'])
        assert len(read_response.get_response_headers()) > 0

        upsert_response = container.upsert_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        assert len(upsert_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(upsert_response.get_response_headers()['lsn'])
        lsn = upsert_response.get_response_headers()['lsn']

        upsert_response['replace'] = True
        replace_response = container.replace_item(upsert_response['id'], upsert_response)
        assert replace_response['replace'] is not None
        assert len(replace_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(replace_response.get_response_headers()['lsn'])

        batch = []
        for i in range(50):
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response.get_response_headers()) > 0
        assert int(lsn) + 1 < int(batch_response.get_response_headers()['lsn'])


if __name__ == '__main__':
    unittest.main()
