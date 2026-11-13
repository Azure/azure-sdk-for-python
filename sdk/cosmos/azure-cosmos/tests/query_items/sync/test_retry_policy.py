# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync retry-policy tests that exercise query_items.

The originals patch ``_retry_utility.ExecuteFunction`` to raise HTTP 429 (or
connection resets) on every request. That Python hook is never called on the Rust
backend, so the throttle copy injects the same 429 with a Rust fault injection rule on
``QueryItem``. Steps and assertions are unchanged; the assertions that read the
legacy throttle retry totals from ``client_connection.last_response_headers`` are
skipped under known gap 29.
"""

import os
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey
from azure.cosmos.http_constants import HttpHeaders, StatusCodes


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


@pytest.mark.cosmosEmulator
class TestRetryPolicy(unittest.TestCase):
    """Rust-path copies of tests/test_retry_policy.py::TestRetryPolicy."""

    created_database = None
    client = None
    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retry-policy-container-" + str(uuid.uuid4())
    retry_after_in_milliseconds = 1000

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = "query_items_retry_policy_" + uuid.uuid4().hex
        cls.client = cosmos_client.CosmosClient(_host(), _key(), consistency_level="Session", _backend="rust")
        cls.created_database = cls.client.create_database(cls.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.client.close()

    def setUp(self) -> None:
        self.created_collection = self.created_database.create_container(self.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                         partition_key=PartitionKey("/pk"))
        self._clients = []

    def tearDown(self) -> None:
        for client in self._clients:
            client.close()
        try:
            self.created_database.delete_container(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        except exceptions.CosmosHttpResponseError:
            pass

    def test_resource_throttle_retry_policy_query_rust(self):
        # Source: tests/test_retry_policy.py::TestRetryPolicy.test_resource_throttle_retry_policy_query
        # The legacy RetryOptions(5) connection policy has no Rust equivalent; Rust owns the
        # throttle retry budget.
        max_retry_attempt_count = 5

        document_definition = {'id': str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        self.created_collection.create_item(body=document_definition)

        # Replaces the _retry_utility.ExecuteFunction patch that raises 429 on every request.
        rule_id = "query-429-" + uuid.uuid4().hex
        client = cosmos_client.CosmosClient(_host(), _key(), _backend="rust", _fault_injection_rules=[{
            "id": rule_id,
            "operation_type": "QueryItem",
            "container_id": self.TEST_CONTAINER_SINGLE_PARTITION_ID,
            "status_code": 429,
            "hit_limit": None,
        }])
        self._clients.append(client)
        container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            self.TEST_CONTAINER_SINGLE_PARTITION_ID)

        try:
            list(container.query_items(
                {
                    'query': 'SELECT * FROM root r WHERE r.id=@id',
                    'parameters': [
                        {'name': '@id', 'value': document_definition['id']}
                    ]
                }))
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
            # Known gap 29: Throttle retry totals are missing from Python response metadata
            # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-29).
            pytest.skip("driver-gap: known gap 29 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-29) - "
                        "the Rust path does not expose x-ms-throttle-retry-count or "
                        "x-ms-throttle-retry-wait-time-ms in last_response_headers.")
            self.assertEqual(max_retry_attempt_count,
                             container.client_connection.last_response_headers[
                                 HttpHeaders.ThrottleRetryCount])
            self.assertGreaterEqual(container.client_connection.last_response_headers[
                                        HttpHeaders.ThrottleRetryWaitTimeInMs],
                                    max_retry_attempt_count * self.retry_after_in_milliseconds)

    # TODO: Need to validate the query retries
    @pytest.mark.skip(
        reason="internals-only: the legacy original is unconditionally skipped and counts calls to a "
        "patched _retry_utility.ExecuteFunction, which the Rust backend never calls; Rust owns "
        "query retries (known gap 13, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13)."
    )
    def test_default_retry_policy_for_query_rust(self):
        # Source: tests/test_retry_policy.py::TestRetryPolicy.test_default_retry_policy_for_query
        document_definition_1 = {'id': str(uuid.uuid4()),
                                 'pk': 'pk',
                                 'name': 'sample document',
                                 'key': 'value'}
        document_definition_2 = {'id': str(uuid.uuid4()),
                                 'pk': 'pk',
                                 'name': 'sample document',
                                 'key': 'value'}

        self.created_collection.create_item(body=document_definition_1)
        self.created_collection.create_item(body=document_definition_2)

        docs = self.created_collection.query_items(query="Select * from c order by c._ts", max_item_count=1,
                                                   enable_cross_partition_query=True)

        result_docs = list(docs)
        self.assertEqual(result_docs[0]['id'], document_definition_1['id'])
        self.assertEqual(result_docs[1]['id'], document_definition_2['id'])


if __name__ == '__main__':
    unittest.main()
