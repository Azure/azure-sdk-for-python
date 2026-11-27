# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Preserve account-default Session behavior without an explicit client override."""

import unittest
import uuid

import pytest

from common._rust_checks import run_on_rust
from config import clients
from config.settings import unique_database_id

from azure.cosmos import exceptions, http_constants, PartitionKey


def get_test_item():
    # Source: tests/test_user_configs.py::get_test_item
    item = {
        "id": "Async_" + str(uuid.uuid4()),
        "test_object": True,
        "lastName": "Smith",
    }
    return item


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestUserConfigs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key_client = clients.create_setup_client(_backend="rust")
        cls.addClassCleanup(cls.key_client.close)
        cls.data_client = clients.create_data_client(_backend="rust")
        cls.addClassCleanup(cls.data_client.close)

    def test_default_account_consistency_rust(self):
        # Source: tests/test_user_configs.py::TestUserConfigs.test_default_account_consistency
        database_id = unique_database_id("user-config")
        container_id = "PythonSDKTestContainer-" + str(uuid.uuid4())
        database_account = self.key_client.client_connection.GetDatabaseAccount()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        self.assertEqual(account_consistency_level, "Session")

        database = self.key_client.create_database(database_id)
        self.addCleanup(self.key_client.delete_database, database_id)
        database.create_container(id=container_id, partition_key=PartitionKey(path="/id"))
        container = self.data_client.get_database_client(database_id).get_container_client(container_id)
        create_response = run_on_rust(self.data_client, lambda: container.create_item(body=get_test_item()))
        session_token = create_response.get_response_headers()[http_constants.CookieHeaders.SessionToken]
        item2 = get_test_item()
        create_response = run_on_rust(self.data_client, lambda: container.create_item(body=item2))
        session_token2 = create_response.get_response_headers()[http_constants.CookieHeaders.SessionToken]
        self.assertNotEqual(session_token, session_token2)

        read_response = run_on_rust(
            self.data_client,
            lambda: container.read_item(item=item2.get("id"), partition_key=item2.get("id")),
        )
        read_session_token = read_response.get_response_headers()[http_constants.CookieHeaders.SessionToken]
        self.assertEqual(session_token2, read_session_token)

        with clients.create_setup_client(_backend="rust", consistency_level="Eventual") as eventual_client:
            database_account = eventual_client.client_connection.GetDatabaseAccount()
            self.assertEqual(
                database_account.ConsistencyPolicy["defaultConsistencyLevel"], account_consistency_level,
            )
            eventual_container = eventual_client.get_database_client(database_id).get_container_client(container_id)
            actual = run_on_rust(
                eventual_client, lambda: eventual_container.read_item(item2["id"], partition_key=item2["id"]),
            )
            self.assertEqual(actual["id"], item2["id"])

        with clients.create_setup_client(_backend="rust", consistency_level="Strong") as strong_client:
            strong_container = strong_client.get_database_client(database_id).get_container_client(container_id)
            with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
                run_on_rust(
                    strong_client, lambda: strong_container.read_item(item2["id"], partition_key=item2["id"]),
                )
            self.assertEqual(caught.exception.status_code, http_constants.StatusCodes.BAD_REQUEST)
