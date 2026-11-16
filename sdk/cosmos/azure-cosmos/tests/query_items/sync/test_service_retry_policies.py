# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copy of the sync service-retry-policy test that exercises query_items.

The original rewrites the legacy client's location cache to three read regions and
patches ``_retry_utility.ExecuteFunction`` to raise ``ServiceRequestError``, then counts
how many regions the legacy ServiceRequestRetryPolicy tries. The Rust backend has
neither the location cache nor the Python retry hook, so this copy runs the steps up to
that point and then skips.
"""

import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


@pytest.mark.cosmosEmulator
class TestServiceRetryPolicies(unittest.TestCase):
    """Rust-path copies of tests/test_service_retry_policies.py::TestServiceRetryPolicies."""

    TEST_CONTAINER_ID = "service-retry-policies-" + str(uuid.uuid4())

    REGION1 = "West US"
    REGION2 = "East US"
    REGION3 = "West US 2"

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = "query_items_service_retry_" + uuid.uuid4().hex
        cls.client = CosmosClient(_host(), _key(), _backend="rust")
        cls.created_database = cls.client.create_database(cls.TEST_DATABASE_ID)
        cls.created_container = cls.created_database.create_container(cls.TEST_CONTAINER_ID,
                                                                      partition_key=PartitionKey("/pk"))

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.client.close()

    def test_service_request_retry_policy_rust(self):
        # Source: tests/test_service_retry_policies.py::TestServiceRetryPolicies.test_service_request_retry_policy
        mock_client = CosmosClient(_host(), _key(), _backend="rust")
        self.addCleanup(mock_client.close)
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        created_item = container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
        assert created_item["pk"]

        # Known gap 11: Closed: driver-owned throttle retry waiting (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-11). Retry policies are owned by the Rust driver.
        pytest.skip("internals-only: the rest of the test rewrites the legacy "
                    "client_connection._global_endpoint_manager.location_cache and patches "
                    "_retry_utility.ExecuteFunction to count legacy ServiceRequestRetryPolicy region "
                    "attempts; the Rust backend has neither and owns its retries "
                    "(known gap 11, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-11). The item was created.")


if __name__ == '__main__':
    unittest.main()
