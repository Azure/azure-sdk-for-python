# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Checks that etag and match_condition still protect delete_database and create_container.

When a caller passes etag with match_condition, the request must carry that condition,
so the service only applies it if the resource still has that etag. If etag is passed
without match_condition, the SDK must raise ValueError.
"""
import unittest
from unittest import mock

import pytest
from azure.core import MatchConditions

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
from azure.cosmos._helpers._request_container import is_create_container_rust_eligible
from azure.cosmos._helpers._request_database import is_delete_database_rust_eligible
from azure.cosmos._helpers._client_context import CosmosClientContext


@pytest.mark.cosmosEmulator
class TestAccessConditionPassthroughUnit(unittest.TestCase):
    """etag and match_condition must reach the request options of each operation."""

    @staticmethod
    def _client():
        """A minimal ``CosmosClient`` with a mocked connection, so nothing is sent."""
        client = cosmos_client.CosmosClient.__new__(cosmos_client.CosmosClient)
        client.client_connection = mock.MagicMock()
        client.client_connection.last_response_headers = {}
        client._adapter = mock.MagicMock()
        client._adapter.name = "rust"
        client._client_context = CosmosClientContext(client._adapter)
        return client

    def test_delete_database_forwards_access_condition_rust(self):
        """A guarded delete must arrive at the helper carrying accessCondition."""
        client = self._client()
        captured = {}

        def fake_delete(database_link, request_options, *, response_hook=None, kwargs=None):
            """Record the arguments so the test can inspect what reached the helper."""
            captured["options"] = request_options
            captured["kwargs"] = kwargs

        with mock.patch.object(cosmos_client, "DatabaseHelper") as helper:
            helper.return_value.delete_database.side_effect = fake_delete
            client.delete_database(
                "db-id",
                etag="etag-value",
                match_condition=MatchConditions.IfNotModified,
            )

        self.assertEqual(
            captured["options"].get("accessCondition"),
            {"type": "IfMatch", "condition": "etag-value"},
        )
        # The SDK has already turned these into request options, so they must
        # not also be passed on as extra keyword arguments.
        self.assertNotIn("etag", captured["kwargs"])
        self.assertNotIn("match_condition", captured["kwargs"])
        self.assertNotIn("session_token", captured["kwargs"])

    def test_delete_database_rejects_etag_without_match_condition_rust(self):
        """``etag`` alone is a caller error and must still raise."""
        client = self._client()
        with mock.patch.object(cosmos_client, "DatabaseHelper"):
            with self.assertRaises(ValueError):
                client.delete_database("db-id", etag="etag-value")

    def test_create_container_forwards_access_condition_rust(self):
        """The same guard must survive ``DatabaseProxy.create_container``."""
        import azure.cosmos.database as database_module

        connection = mock.MagicMock()
        connection._backend = mock.MagicMock(name="backend")
        database = database_module.DatabaseProxy(connection, "db-id")
        captured = {}

        def fake_create(database_link, definition, request_options, **kwargs):
            """Record the options so the test can check that ``accessCondition`` arrived."""
            captured["options"] = request_options
            return {"id": "c"}

        with mock.patch.object(database_module, "ContainerHelper") as helper:
            helper.return_value.create_container.side_effect = fake_create
            database.create_container(
                "c",
                PartitionKey(path="/pk"),
                etag="etag-value",
                match_condition=MatchConditions.IfNotModified,
            )

        self.assertEqual(
            captured["options"].get("accessCondition"),
            {"type": "IfMatch", "condition": "etag-value"},
        )

    def test_access_condition_becomes_a_request_setting_rust(self):
        """Each kind of etag condition becomes its own request setting.

        "IfMatch" becomes if_match (write only if the etag still matches) and "IfNoneMatch"
        becomes if_none_match (write only if it does not). They are opposites, so mixing
        them up would write exactly when it should not.
        """
        from azure.cosmos._helpers._request_settings import build_request_headers_and_settings

        self.assertEqual(
            build_request_headers_and_settings(
                {"accessCondition": {"type": "IfMatch", "condition": "etag-value"}}
            )[1].item.if_match,
            "etag-value",
        )
        self.assertEqual(
            build_request_headers_and_settings(
                {"accessCondition": {"type": "IfNoneMatch", "condition": "etag-value"}}
            )[1].item.if_none_match,
            "etag-value",
        )

    def test_access_condition_is_accepted_rust(self):
        """An etag condition is a supported option, so delete_database and create_container
        accept it rather than raising an "unsupported" error."""
        options = {"accessCondition": {"type": "IfMatch", "condition": "etag-value"}}
        self.assertTrue(is_delete_database_rust_eligible(options, {}))
        self.assertTrue(is_create_container_rust_eligible(options, {}))


if __name__ == "__main__":
    unittest.main()
