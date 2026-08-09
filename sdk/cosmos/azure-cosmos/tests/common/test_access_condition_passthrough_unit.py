# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Access-condition passthrough for the migrated control-plane operations.

These pin a regression the Rust migration introduced and this change reverts.
``CosmosClient.delete_database`` and ``DatabaseProxy.create_container`` briefly
popped ``etag`` / ``match_condition`` / ``session_token`` out of ``kwargs``
before calling ``build_options``. That looked harmless -- both had just been
deprecation-warned as inapplicable -- but it was not:

* ``build_options`` is what turns ``etag`` + ``match_condition`` into
  ``request_options["accessCondition"]``, which becomes an ``If-Match`` header
  on both engines. Dropping it silently removed a caller's optimistic
  concurrency guard, so a guarded delete destroyed a database the service would
  otherwise have refused to touch with a 412.
* ``build_options`` also raises ``ValueError`` when ``etag`` is passed without a
  ``match_condition``. Popping the keys swallowed that error.

The pops were redundant besides: ``_get_match_headers`` and ``COMMON_OPTIONS``
already consume all three keys, so none of them ever survived into the kwargs
the Rust eligibility gate inspects.
"""
import unittest
from unittest import mock

import pytest
from azure.core import MatchConditions

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
from azure.cosmos._helpers._request_prep import (
    flatten_options_to_headers,
    is_create_container_rust_eligible,
    is_delete_database_rust_eligible,
)


@pytest.mark.cosmosEmulator
class TestAccessConditionPassthroughUnit(unittest.TestCase):
    """The access condition must reach ``request_options`` on both engines."""

    @staticmethod
    def _client():
        """A minimal ``CosmosClient`` with a mocked connection, so requests are captured not sent."""
        client = cosmos_client.CosmosClient.__new__(cosmos_client.CosmosClient)
        client.client_connection = mock.MagicMock()
        client.client_connection.last_response_headers = {}
        client._backend = "rust"
        return client

    def test_delete_database_forwards_access_condition(self):
        """A guarded delete must arrive at the helper carrying accessCondition."""
        client = self._client()
        captured = {}

        def fake_delete(database_link, request_options, kwargs=None):
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
        # The keys are consumed by build_options, so nothing strays into the
        # kwargs the eligibility gate inspects -- which is why no pop is needed.
        self.assertNotIn("etag", captured["kwargs"])
        self.assertNotIn("match_condition", captured["kwargs"])
        self.assertNotIn("session_token", captured["kwargs"])

    def test_delete_database_rejects_etag_without_match_condition(self):
        """``etag`` alone is a caller error and must still raise."""
        client = self._client()
        with mock.patch.object(cosmos_client, "DatabaseHelper"):
            with self.assertRaises(ValueError):
                client.delete_database("db-id", etag="etag-value")

    def test_create_container_forwards_access_condition(self):
        """The same guard must survive ``DatabaseProxy.create_container``."""
        import azure.cosmos.database as database_module

        database = database_module.DatabaseProxy(mock.MagicMock(), "db-id")
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

    def test_access_condition_becomes_a_wire_header_on_the_rust_path(self):
        """Rust has no legacy GetHeaders step, so the flattener must emit it."""
        self.assertEqual(
            flatten_options_to_headers(
                {"accessCondition": {"type": "IfMatch", "condition": "etag-value"}}
            )["If-Match"],
            "etag-value",
        )
        self.assertEqual(
            flatten_options_to_headers(
                {"accessCondition": {"type": "IfNoneMatch", "condition": "etag-value"}}
            )["If-None-Match"],
            "etag-value",
        )

    def test_access_condition_does_not_force_a_legacy_fallback(self):
        """Rust honors the header, so a guarded call stays on the Rust path."""
        options = {"accessCondition": {"type": "IfMatch", "condition": "etag-value"}}
        self.assertTrue(is_delete_database_rust_eligible(options, {}))
        self.assertTrue(is_create_container_rust_eligible(options, {}))


if __name__ == "__main__":
    unittest.main()
