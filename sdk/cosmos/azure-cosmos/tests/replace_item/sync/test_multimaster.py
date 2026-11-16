# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync multi-master tentative-writes tests that exercise replace_item.

The originals patch ``_retry_utility.ExecuteFunction`` to report a multi-write account
and to record whether each outgoing request carries ``x-ms-cosmos-allow-tentative-writes``.
Rust requests bypass that Python function: the driver derives the header from the real
account topology, and its outgoing requests cannot be observed. Every operation still
runs in order; the test then skips before the header-count assertions it cannot verify.
"""

import os
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey


@pytest.mark.cosmosEmulator
class TestMultiMaster(unittest.TestCase):
    """Rust-path copies of tests/test_multimaster.py::TestMultiMaster."""

    host = os.environ.get("ACCOUNT_HOST")
    masterKey = os.environ.get("ACCOUNT_KEY")
    counter = 0
    last_headers = []

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = "replace_item_multimaster_" + uuid.uuid4().hex
        cls.TEST_SINGLE_PARTITION_CONTAINER_ID = "single_partition_" + uuid.uuid4().hex[:8]
        cls.setup_client = cosmos_client.CosmosClient(cls.host, cls.masterKey, _backend="rust")
        database = cls.setup_client.create_database(cls.TEST_DATABASE_ID)
        database.create_container(cls.TEST_SINGLE_PARTITION_CONTAINER_ID, PartitionKey(path="/pk"))

    @classmethod
    def tearDownClass(cls):
        try:
            cls.setup_client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.setup_client.close()

    def test_tentative_writes_header_present_rust(self):
        # Source: tests/test_multimaster.py::TestMultiMaster.test_tentative_writes_header_present
        self.last_headers = []
        self.EnableMultipleWritableLocations = True
        self._validate_tentative_write_headers()

    def test_tentative_writes_header_not_present_rust(self):
        # Source: tests/test_multimaster.py::TestMultiMaster.test_tentative_writes_header_not_present
        self.last_headers = []
        self.EnableMultipleWritableLocations = False
        self._validate_tentative_write_headers()

    def _validate_tentative_write_headers(self):
        self.counter = 0  # Reset counter for each test run
        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). The original's
        # ExecuteFunction patch that fakes the account's EnableMultipleWritableLocations and the
        # UseMultipleWriteLocations connection-policy assignment have no Rust equivalent (the
        # assignment is rejected), so the driver uses the real account topology.
        client = cosmos_client.CosmosClient(TestMultiMaster.host, TestMultiMaster.masterKey,
                                            consistency_level="Session", _backend="rust")
        try:
            created_db = client.get_database_client(self.TEST_DATABASE_ID)

            created_collection = created_db.get_container_client(self.TEST_SINGLE_PARTITION_CONTAINER_ID)

            document_definition = {'id': 'doc' + str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'operation': 'insertion'}
            created_document = created_collection.create_item(body=document_definition)

            created_collection.read_item(
                item=created_document,
                partition_key='pk'
            )

            created_document['operation'] = 'replace'
            replaced_document = created_collection.replace_item(
                item=created_document['id'],
                body=created_document
            )

            replaced_document['operation'] = 'upsert'
            upserted_document = created_collection.upsert_item(body=replaced_document)

            created_collection.delete_item(
                item=upserted_document,
                partition_key='pk'
            )

            is_allow_tentative_writes_set = self.EnableMultipleWritableLocations is True

            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust outgoing request headers are not observable, so x-ms-cosmos-allow-tentative-writes cannot be counted.
            pytest.skip("internals-only: the tentative-writes header count came from patching legacy "
                        "_retry_utility.ExecuteFunction; Rust outgoing request headers are not observable "
                        "(known gap 6). All create/read/replace/upsert/delete operations ran.")

            # Count operations with the tentative writes header
            headers_with_tentative_writes = sum(1 for h in self.last_headers if h)

            if is_allow_tentative_writes_set:
                # Create, replace, upsert and delete each require the header.
                self.assertGreaterEqual(headers_with_tentative_writes, 4,
                    f"Expected at least 4 write operations with tentative writes header, "
                    f"got {headers_with_tentative_writes}")
            else:
                # When multi-write is disabled, no operations should have the header
                self.assertEqual(headers_with_tentative_writes, 0,
                    f"Expected 0 operations with tentative writes header, "
                    f"got {headers_with_tentative_writes}")
        finally:
            client.close()


if __name__ == '__main__':
    unittest.main()
