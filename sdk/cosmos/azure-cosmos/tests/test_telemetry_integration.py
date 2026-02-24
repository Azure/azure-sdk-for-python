# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Integration tests for Cosmos DB OpenTelemetry with actual operations.

This test verifies:
1. Query sanitization works correctly for different query types
2. Cosmos-specific attributes are added to spans
3. Parameter values are NOT logged (opt-in per semantic conventions)
4. db.system attribute is added even on errors
5. All operation types are correctly set
"""

import unittest
import uuid
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos._constants import _Constants
import test_config

# OpenTelemetry setup for testing
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult, SimpleSpanProcessor


class InMemorySpanExporter(SpanExporter):
    """Captures spans in memory for testing."""

    def __init__(self):
        self.spans = []

    def export(self, span_data):
        for span in span_data:
            span_dict = {
                "name": span.name,
                "attributes": dict(span.attributes) if span.attributes else {}
            }
            self.spans.append(span_dict)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def clear(self):
        self.spans = []


class TestTelemetryIntegration(unittest.TestCase):
    """Integration tests for OpenTelemetry with Cosmos DB operations."""

    @classmethod
    def setUpClass(cls):
        """Set up OpenTelemetry and Cosmos client."""
        # Enable OpenTelemetry tracing
        settings.tracing_implementation = OpenTelemetrySpan

        # Set up in-memory exporter
        cls.exporter = InMemorySpanExporter()
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(cls.exporter))

        # Use test config like other cosmos tests
        cls.client = CosmosClient(test_config.TestConfig.host, test_config.TestConfig.masterKey)
        cls.test_db_name = f"TestTelemetryDB_{uuid.uuid4().hex[:8]}"
        cls.test_container_name = "TestTelemetryContainer"

        try:
            cls.database = cls.client.create_database(cls.test_db_name)
            cls.container = cls.database.create_container(
                id=cls.test_container_name,
                partition_key=PartitionKey(path="/pk")
            )
        except Exception as e:
            print(f"Setup failed: {e}")
            raise

    @classmethod
    def tearDownClass(cls):
        """Clean up test resources."""
        try:
            cls.client.delete_database(cls.test_db_name)
        except:
            pass

    def setUp(self):
        """Clear captured spans before each test."""
        self.exporter.clear()

    def test_parameterized_query_not_sanitized(self):
        """Verify parameterized queries are NOT sanitized in telemetry."""
        # Create test item
        self.container.create_item({"id": "test1", "pk": "pk1", "value": 100})
        self.exporter.clear()  # Clear the create span

        # Query with parameters
        query = "SELECT * FROM c WHERE c.value > @minValue"
        parameters = [{"name": "@minValue", "value": 50}]

        list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

        # Find the query span
        query_spans = [s for s in self.exporter.spans if "query" in s.get("name", "").lower()]

        self.assertGreater(len(query_spans), 0, "Should have at least one query span")
        attrs = query_spans[0]["attributes"]
        query_text = attrs.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, "")

        # Should NOT be sanitized
        self.assertIn("@minValue", query_text, "Parameter placeholder should remain")
        self.assertNotIn("50", query_text, "Parameter VALUE should not be in query")

        # Verify parameter values are NOT logged as attributes
        param_keys = [k for k in attrs.keys() if "db.query.parameter" in k]
        self.assertEqual(len(param_keys), 0, "Parameter values should NOT be logged")

        # Verify db.system is present
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_SYSTEM), "cosmosdb")

        # Verify operation type
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_OPERATION_TYPE), "query")

    def test_literal_query_is_sanitized(self):
        """Verify queries with literal values ARE sanitized in telemetry."""
        self.exporter.clear()

        # Query with literal values
        query = "SELECT * FROM c WHERE c.value = 100 AND c.name = 'test'"

        list(self.container.query_items(query=query, enable_cross_partition_query=True))

        # Find the query span
        query_spans = [s for s in self.exporter.spans if "query" in s.get("name", "").lower()]

        self.assertGreater(len(query_spans), 0)
        attrs = query_spans[0]["attributes"]
        query_text = attrs.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, "")

        # Should be sanitized
        self.assertNotIn("100", query_text, "Numeric literal should be sanitized")
        self.assertNotIn("'test'", query_text, "String literal should be sanitized")
        self.assertIn("?", query_text, "Literals should be replaced with ?")

    def test_cosmos_attributes_present(self):
        """Verify Cosmos-specific attributes are added to spans."""
        self.exporter.clear()

        # Create an item
        self.container.create_item({"id": f"attr_test_{uuid.uuid4().hex[:4]}", "pk": "pk1", "value": 200})

        # Find the create span
        create_spans = [s for s in self.exporter.spans if "create" in s.get("name", "").lower()]

        self.assertGreater(len(create_spans), 0)
        attrs = create_spans[0]["attributes"]

        # Verify required attributes
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_SYSTEM), "cosmosdb")
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_OPERATION_NAME), "create_item")
        self.assertEqual(attrs.get(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_OPERATION_TYPE), "create")
        self.assertIn(self.test_container_name, attrs.get(_Constants.OpenTelemetryAttributes.DB_COLLECTION_NAME, ""))
        self.assertIn(self.test_db_name, attrs.get(_Constants.OpenTelemetryAttributes.DB_NAMESPACE, ""))

        # Verify response attributes
        self.assertIn(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_REQUEST_CHARGE, attrs)

    def test_error_has_db_system_attribute(self):
        """Verify db.system attribute is added even when operations fail."""
        self.exporter.clear()

        try:
            # Try to read non-existent item (will fail)
            self.container.read_item(item="nonexistent", partition_key="nonexistent")
        except exceptions.CosmosResourceNotFoundError:
            pass  # Expected

        # Find spans
        spans = [s for s in self.exporter.spans if s.get("attributes")]

        self.assertGreater(len(spans), 0, "Should have captured error span")

        # Check if db.system is in any span
        has_db_system = any(
            s["attributes"].get(_Constants.OpenTelemetryAttributes.DB_SYSTEM) == "cosmosdb"
            for s in spans
        )
        self.assertTrue(has_db_system, "db.system should be present even on error")


if __name__ == '__main__':
    unittest.main()


