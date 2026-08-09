# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Selected v4 database-query tests pinned to the Rust backend.

Original: tests/test_crud_database.py
Copy:     tests/query_databases/sync/legacy/test_crud_database.py
"""

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import cosmos_client


@pytest.mark.cosmosEmulator
class TestCRUDDatabaseOperations(unittest.TestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    key_client: cosmos_client.CosmosClient = None

    @classmethod
    def setUpClass(cls):
        cls.key_client = cosmos_client.CosmosClient(cls.host, cls.masterKey, _backend="rust")

    @classmethod
    def tearDownClass(cls):
        if cls.key_client is not None:
            cls.key_client.close()

    def test_sql_query_crud(self):
        """Query databases by id with a parameterized dict, a no-match filter and a raw string."""
        # Source: tests/test_crud_database.py::TestCRUDDatabaseOperations.test_sql_query_crud
        # create two databases.
        db1 = self.key_client.create_database('database 1' + str(uuid.uuid4()))
        db2 = self.key_client.create_database('database 2' + str(uuid.uuid4()))

        # query with parameters.
        databases = list(self.key_client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': db1.id}
            ]
        }))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        # query without parameters.
        databases = list(self.key_client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id="database non-existing"'
        }))
        self.assertEqual(0, len(databases), 'Unexpected number of query results.')

        # query with a string.
        databases = list(self.key_client.query_databases('SELECT * FROM root r WHERE r.id="' + db2.id + '"'))  # nosec
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')
        self.key_client.delete_database(db1.id)
        self.key_client.delete_database(db2.id)


if __name__ == "__main__":
    unittest.main()
