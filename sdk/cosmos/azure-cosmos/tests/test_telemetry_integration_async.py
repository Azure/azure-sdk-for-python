# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Integration tests for Cosmos DB OpenTelemetry with actual async operations."""

import unittest
import uuid
import asyncio
import importlib.util
import os
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos._constants import _Constants
import test_config

# Use Azure Core tracing abstractions
from tracing_common import setup_tracing, cleanup_tracing


class TestTelemetryIntegrationAsync(unittest.IsolatedAsyncioTestCase):
    """Integration tests for OpenTelemetry with async Cosmos DB operations."""

    @classmethod
    def setUpClass(cls):
        """Set up tracing and Cosmos client."""
        if importlib.util.find_spec("aiohttp") is None:
            raise unittest.SkipTest("aiohttp is required for async Cosmos integration tests")

        cls._previous_query_text_opt_in = os.environ.get(_Constants.OTEL_ENABLE_QUERY_TEXT)
        os.environ[_Constants.OTEL_ENABLE_QUERY_TEXT] = "true"

        # Enable tracing using Azure Core abstractions
        cls.tracing_helper = setup_tracing()

        cls.test_db_name = f"TestTelemetryAsyncDB_{uuid.uuid4().hex[:8]}"
        cls.test_container_name = "TestTelemetryAsyncContainer"

    async def asyncSetUp(self):
        """Set up async resources."""
        self.client = CosmosClient(test_config.TestConfig.host, test_config.TestConfig.masterKey)
        self.database = await self.client.create_database_if_not_exists(self.test_db_name)
        self.container = await self.database.create_container_if_not_exists(
            id=self.test_container_name,
            partition_key=PartitionKey(path="/pk")
        )
        self.tracing_helper.clear()

    async def asyncTearDown(self):
        """Clean up async resources."""
        await self.client.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up test resources."""
        # Need to run async cleanup
        async def cleanup():
            client = CosmosClient(test_config.TestConfig.host, test_config.TestConfig.masterKey)
            try:
                await client.delete_database(cls.test_db_name)
            except:
                pass
            await client.close()

        asyncio.run(cleanup())
        if cls._previous_query_text_opt_in is None:
            os.environ.pop(_Constants.OTEL_ENABLE_QUERY_TEXT, None)
        else:
            os.environ[_Constants.OTEL_ENABLE_QUERY_TEXT] = cls._previous_query_text_opt_in
        cleanup_tracing()

    async def test_parameterized_query_not_sanitized(self):
        """Verify parameterized queries are NOT sanitized in telemetry."""
        # Create test item
        await self.container.create_item({"id": "test1", "pk": "pk1", "metric": 100, "label": "test"})
        self.tracing_helper.clear()

        # Query with parameters
        query = "SELECT * FROM c WHERE c.metric > @minValue"
        parameters = [{"name": "@minValue", "value": 50}]

        items = []
        async for item in self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True):
            items.append(item)

        # Find the query span
        all_spans = self.tracing_helper.get_spans()
        query_spans = [s for s in all_spans if "query" in s.get("name", "").lower()]

        self.assertGreater(len(query_spans), 0, "Should have at least one query span")
        attrs = query_spans[0]["attributes"]
        query_text = attrs.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, "")

        # Should NOT be sanitized
        self.assertIn("@minValue", query_text, "Parameter placeholder should remain")
        self.assertNotIn("50", query_text, "Parameter VALUE should not be in query")

        # Verify parameter values are NOT logged as attributes
        param_keys = [k for k in attrs.keys() if "db.query.parameter" in k]
        self.assertEqual(len(param_keys), 0, "Parameter values should NOT be logged")

        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_SYSTEM_NAME), "azure.cosmosdb")

    async def test_literal_query_is_sanitized(self):
        """Verify queries with literal values ARE sanitized in telemetry."""
        self.tracing_helper.clear()

        # Query with literal values
        await self.container.create_item({"id": "test2", "pk": "pk1", "metric": 100, "label": "test"})
        self.tracing_helper.clear()

        query = "SELECT * FROM c WHERE c.metric = 100 AND c.label = 'test'"

        items = []
        async for item in self.container.query_items(query=query, enable_cross_partition_query=True):
            items.append(item)

        # Find the query span
        all_spans = self.tracing_helper.get_spans()
        query_spans = [s for s in all_spans if "query" in s.get("name", "").lower()]

        self.assertGreater(len(query_spans), 0)
        attrs = query_spans[0]["attributes"]
        query_text = attrs.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, "")

        # Should be sanitized
        self.assertNotIn("100", query_text, "Numeric literal should be sanitized")
        self.assertNotIn("'test'", query_text, "String literal should be sanitized")
        self.assertIn("?", query_text, "Literals should be replaced with ?")

    async def test_cosmos_attributes_present(self):
        """Verify Cosmos-specific attributes are added to spans."""
        self.tracing_helper.clear()

        # Create an item
        await self.container.create_item({"id": f"attr_test_{uuid.uuid4().hex[:4]}", "pk": "pk1", "value": 200})

        # Find the Cosmos-enriched create span
        all_spans = self.tracing_helper.get_spans()
        create_spans = [
            s for s in all_spans
            if s.get("attributes", {}).get(_Constants.OpenTelemetryAttributes.DB_OPERATION_NAME) == "create_item"
        ]

        self.assertGreater(len(create_spans), 0)
        attrs = create_spans[0]["attributes"]

        # Verify required attributes
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_SYSTEM_NAME), "azure.cosmosdb")
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_OPERATION_NAME), "create_item")
        self.assertIn(self.test_container_name, attrs.get(_Constants.OpenTelemetryAttributes.DB_COLLECTION_NAME, ""))
        self.assertIn(self.test_db_name, attrs.get(_Constants.OpenTelemetryAttributes.DB_NAMESPACE, ""))

        # Verify response attributes
        self.assertIn(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE, attrs)

    async def test_error_has_db_system_attribute(self):
        """Verify db.system attribute is added even when operations fail."""
        self.tracing_helper.clear()

        try:
            # Try to read non-existent item (will fail)
            await self.container.read_item(item="nonexistent", partition_key="nonexistent")
        except exceptions.CosmosResourceNotFoundError:
            pass  # Expected

        # Find spans
        all_spans = self.tracing_helper.get_spans()
        spans = [s for s in all_spans if s.get("attributes")]

        self.assertGreater(len(spans), 0, "Should have captured error span")

        # Check if db.system.name is in any span
        has_db_system = any(
            s["attributes"].get(_Constants.OpenTelemetryAttributes.DB_SYSTEM_NAME) == "azure.cosmosdb"
            for s in spans
        )
        self.assertTrue(has_db_system, "db.system.name should be present even on error")


if __name__ == '__main__':
    unittest.main()

