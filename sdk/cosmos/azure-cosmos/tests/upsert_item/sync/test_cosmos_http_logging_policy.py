# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original activity-id logging test, run on the Rust path.

Uses a test-owned database. The upserts run on a Rust-backed client; the
per-request activity-id log records the legacy HTTP logging policy produced
are not emitted on Rust, so the copy skips at that check.
"""

import logging
import unittest
import uuid

import pytest

from config import settings
from azure.cosmos import CosmosClient, PartitionKey

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


def create_logger(name: str, mock_handler: MockHandler, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addHandler(mock_handler)
    logger.setLevel(level)

    return logger


def _has_request_response_records(mock_handler: MockHandler) -> bool:
    messages = mock_handler.messages
    return len(messages) >= 2 and all(hasattr(m, "activity_id") for m in messages[:2])


@pytest.mark.cosmosEmulator
class TestCosmosHttpLogger(unittest.TestCase):
    host = settings.TestSettings.host
    masterKey = settings.TestSettings.masterKey

    def test_activity_id_logging_policy_rust(self):
        # Source: tests/test_cosmos_http_logging_policy.py::TestCosmosHttpLogger.test_activity_id_logging_policy
        # Create a mock handler and logger for the new client
        self.mock_handler_activity_id = MockHandler()
        self.logger_activity_id = create_logger("upsert_test_logger_activity_id_rust", self.mock_handler_activity_id)
        self.addCleanup(self.logger_activity_id.removeHandler, self.mock_handler_activity_id)

        # Create a new client with the logger and enable diagnostics logging
        self.client_activity_id = CosmosClient(
            self.host,
            self.masterKey,
            consistency_level="Session",
            logger=self.logger_activity_id,
            enable_diagnostics_logging=True,
            _backend="rust",
        )
        self.addCleanup(self.client_activity_id.close)

        # Generate a custom activity ID
        custom_activity_id = str(uuid.uuid4())

        # Create a database and container for the test
        database_id = "upsert_logging_activity_id_" + uuid.uuid4().hex
        container_id = "container_test_activity_id_" + str(uuid.uuid4())
        database = self.client_activity_id.create_database(id=database_id)
        self.addCleanup(self.client_activity_id.delete_database, database_id)
        container = database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
        # Reset the mock handler to clear previous messages
        self.mock_handler_activity_id.reset()

        # Upsert an item and verify the request and response activity IDs match
        item_id = str(uuid.uuid4())
        item_body = {"id": item_id, "pk": item_id}
        container.upsert_item(body=item_body)

        # Verify that the request activity ID matches the response activity ID
        # Having the Request Activity confirms we generated one from SDK
        # Having it match the response means it was passed successfully
        if not _has_request_response_records(self.mock_handler_activity_id):
            pytest.skip(_GAP_33_ACTIVITY_ID_SKIP)
        log_record_request = self.mock_handler_activity_id.messages[0]
        log_record_response = self.mock_handler_activity_id.messages[1]
        assert log_record_request.activity_id == log_record_response.activity_id

        # Upsert another item with the custom activity ID in the initial headers
        headers = {"x-ms-activity-id": custom_activity_id}
        item_id_2 = str(uuid.uuid4())
        item_body_2 = {"id": item_id_2, "pk": item_id_2}
        container.upsert_item(body=item_body_2, initial_headers=headers)

        # Verify that the custom activity ID does not match the request activity ID from the log record
        # Users should not be able to pass in their own activity ID.
        log_record_request_2 = self.mock_handler_activity_id.messages[2]
        assert log_record_request_2.activity_id != custom_activity_id

        self.mock_handler_activity_id.reset()


if __name__ == "__main__":
    unittest.main()
