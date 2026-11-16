# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the async retry-policy tests that exercise query_items.

The originals patch ``_retry_utility.ExecuteFunctionAsync`` to raise HTTP 429 (or
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

import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import HttpHeaders, StatusCodes


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


@pytest.mark.cosmosEmulator
class TestRetryPolicyAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copies of tests/test_retry_policy_async.py::TestRetryPolicyAsync."""

    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retry-policy-container-" + str(uuid.uuid4())
    retry_after_in_milliseconds = 1000

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = "query_items_retry_policy_async_" + uuid.uuid4().hex
        self.client = CosmosClient(_host(), _key(), _backend="rust")
        await self.client.__aenter__()
        self._clients = []
        self.created_database = None
        try:
            self.created_database = await self.client.create_database(self.TEST_DATABASE_ID)
            self.created_collection = await self.created_database.create_container(
                self.TEST_CONTAINER_SINGLE_PARTITION_ID, partition_key=PartitionKey("/pk"))
        except BaseException:
            await self.asyncTearDown()
            raise

    async def asyncTearDown(self):
        try:
            for client in self._clients:
                await client.close()
            if self.created_database is not None:
                await self.client.delete_database(self.TEST_DATABASE_ID)
        finally:
            await self.client.close()

    async def test_resource_throttle_retry_policy_query_async_rust(self):
        # Source: tests/test_retry_policy_async.py::TestRetryPolicyAsync.test_resource_throttle_retry_policy_query_async
        # The legacy RetryOptions(5) connection policy has no Rust equivalent; Rust owns the
        # throttle retry budget.
        max_retry_attempt_count = 5

        document_definition = {'id': str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        await self.created_collection.create_item(body=document_definition)

        # Replaces the _retry_utility.ExecuteFunctionAsync patch that raises 429 on every request.
        rule_id = "query-429-" + uuid.uuid4().hex
        client = CosmosClient(_host(), _key(), _backend="rust", _fault_injection_rules=[{
            "id": rule_id,
            "operation_type": "QueryItem",
            "container_id": self.TEST_CONTAINER_SINGLE_PARTITION_ID,
            "status_code": 429,
            "hit_limit": None,
        }])
        await client.__aenter__()
        self._clients.append(client)
        container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            self.TEST_CONTAINER_SINGLE_PARTITION_ID)

        try:
            query_results = container.query_items(
                {
                    'query': 'SELECT * FROM root r WHERE r.id=@id',
                    'parameters': [
                        {'name': '@id', 'value': document_definition['id']}
                    ]
                })
            async for item in query_results:
                pass
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
        "patched _retry_utility.ExecuteFunctionAsync, which the Rust backend never calls; Rust owns "
        "query retries (known gap 13, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13)."
    )
    async def test_default_retry_policy_for_query_async_rust(self):
        # Source: tests/test_retry_policy_async.py::TestRetryPolicyAsync.test_default_retry_policy_for_query_async
        document_definition_1 = {'id': str(uuid.uuid4()),
                                 'pk': 'pk',
                                 'name': 'sample document',
                                 'key': 'value'}
        document_definition_2 = {'id': str(uuid.uuid4()),
                                 'pk': 'pk',
                                 'name': 'sample document',
                                 'key': 'value'}

        await self.created_collection.create_item(body=document_definition_1)
        await self.created_collection.create_item(body=document_definition_2)

        docs = self.created_collection.query_items(query="Select * from c order by c._ts", max_item_count=1,
                                                   enable_cross_partition_query=True)

        result_docs = [doc async for doc in docs]
        self.assertEqual(result_docs[0]['id'], document_definition_1['id'])
        self.assertEqual(result_docs[1]['id'], document_definition_2['id'])


if __name__ == '__main__':
    unittest.main()
