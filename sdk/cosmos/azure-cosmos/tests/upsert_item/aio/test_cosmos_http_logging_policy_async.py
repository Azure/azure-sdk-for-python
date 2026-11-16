# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async activity-id logging test, run on the Rust path.

Uses a test-owned database. The upserts run on a Rust-backed client; the
per-request activity-id log records the legacy HTTP logging policy produced
are not emitted on Rust, so the copy skips at that check.
"""

import logging
import unittest
import uuid

import pytest

from config import settings
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient

# Known gap 33: `CosmosClient(...)`: settings from first principles, bites 1-15 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-33). Logging is resolved only under the summary-logging contract; Rust emits one summary record per operation (activity id inside the message) with no request/response records and no `activity_id` record attribute.
_GAP_33_ACTIVITY_ID_SKIP = (
    "accepted-vnext-change: Rust emits one diagnostics summary record per operation, not legacy "
    "request/response HTTP log records with an activity_id attribute (known gap 33: summary-logging contract)."
)


class MockHandler(logging.Handler):

    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


def _has_request_response_records(mock_handler: MockHandler) -> bool:
    messages = mock_handler.messages
    return len(messages) >= 2 and all(hasattr(m, "activity_id") for m in messages[:2])


@pytest.mark.cosmosEmulator
class TestCosmosHttpLoggerAsync(unittest.IsolatedAsyncioTestCase):
    host = settings.TestSettings.host
    masterKey = settings.TestSettings.masterKey

    async def asyncSetUp(self):
        self.mock_handler_activity_id = MockHandler()
        self.logger = logging.getLogger("azure.cosmos")
        self.logger.setLevel(logging.INFO)
        self.client_activity_id = None

    async def asyncTearDown(self):
        if self.client_activity_id:
            await self.client_activity_id.close()

    async def test_activity_id_logging_policy_async_rust(self):
        # Source: tests/test_cosmos_http_logging_policy_async.py::TestCosmosHttpLoggerAsync.test_activity_id_logging_policy_async
        # Create a mock handler and logger for the new client
        self.logger.addHandler(self.mock_handler_activity_id)

        # Create a new client with the logger and enable diagnostics logging
        self.client_activity_id = CosmosClient(
            self.host,
            self.masterKey,
            consistency_level="Session",
            logger=self.logger,
            enable_diagnostics_logging=True,
            _backend="rust",
        )
        # Generate a custom activity ID
        custom_activity_id = str(uuid.uuid4())

        # Create a database and container for the test
        database_id = "upsert_logging_activity_id_async_" + uuid.uuid4().hex
        container_id = "container_test_activity_id_" + str(uuid.uuid4())
        try:

            database = await self.client_activity_id.create_database(id=database_id)
            container = await database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))

            # Reset the mock handler to clear previous messages
            self.mock_handler_activity_id.reset()

            # Upsert an item and verify the request and response activity IDs match
            item_id = str(uuid.uuid4())
            item_body = {"id": item_id, "pk": item_id}
            await container.upsert_item(body=item_body)

            # Verify that the request activity ID matches the response activity ID
            if not _has_request_response_records(self.mock_handler_activity_id):
                pytest.skip(_GAP_33_ACTIVITY_ID_SKIP)
            log_record_request = self.mock_handler_activity_id.messages[0]
            log_record_response = self.mock_handler_activity_id.messages[1]
            assert log_record_request.activity_id == log_record_response.activity_id

            # Upsert another item with the custom activity ID in the initial headers
            headers = {"x-ms-activity-id": custom_activity_id}
            item_id_2 = str(uuid.uuid4())
            item_body_2 = {"id": item_id_2, "pk": item_id_2}
            await container.upsert_item(body=item_body_2, initial_headers=headers)

            # Verify that the custom activity ID does not match the request activity ID from the log record
            log_record_request_2 = self.mock_handler_activity_id.messages[2]
            assert log_record_request_2.activity_id != custom_activity_id

        finally:
            # Clean up by deleting the database
            await self.client_activity_id.delete_database(database_id)
            self.mock_handler_activity_id.reset()
            self.logger.removeHandler(self.mock_handler_activity_id)


if __name__ == "__main__":
    unittest.main()
