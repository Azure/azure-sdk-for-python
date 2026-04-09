# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for Cosmos DB OpenTelemetry semantic convention attributes."""

import os
import unittest
from unittest.mock import Mock, patch
from azure.cosmos._cosmos_responses import CosmosDict, CosmosList
from azure.cosmos._cosmos_span_attributes import (
    _add_cosmos_attributes,
    _add_response_attributes,
    _extract_headers,
    cosmos_span_attributes,
    sanitize_query,
)
from azure.cosmos._constants import _Constants
from azure.cosmos.http_constants import HttpHeaders


class TestQuerySanitization(unittest.TestCase):
    """Test query sanitization logic per OpenTelemetry semantic conventions."""

    def test_sanitize_parameterized_query(self):
        """Parameterized queries without inline literals should remain unchanged."""
        query = "SELECT * FROM c WHERE c.userId = @userId AND c.age > @minAge"
        parameters = [{"name": "@userId", "value": "12345"}, {"name": "@minAge", "value": 25}]

        result = sanitize_query(query, parameters)

        # Should return unchanged since it uses parameters
        self.assertEqual(result, query)

    def test_sanitize_parameterized_query_with_inline_literals(self):
        """Parameterized query text should remain unchanged when parameters are supplied."""
        query = "SELECT * FROM c WHERE c.userId = @userId AND c.status = 'active' AND c.age > 21"
        parameters = [{"name": "@userId", "value": "12345"}]

        result = sanitize_query(query, parameters)

        self.assertEqual(result, query)

    def test_sanitize_string_literals(self):
        """String literals should be replaced with '?'."""
        query = "SELECT * FROM c WHERE c.name = 'John Doe' AND c.city = 'Seattle'"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.name = '?' AND c.city = '?'"
        self.assertEqual(result, expected)

    def test_sanitize_numeric_literals_integer(self):
        """Integer literals should be replaced with ?."""
        query = "SELECT * FROM c WHERE c.age = 25 AND c.count > 100"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.age = ? AND c.count > ?"
        self.assertEqual(result, expected)

    def test_sanitize_numeric_literals_float(self):
        """Float literals should be replaced with ?."""
        query = "SELECT * FROM c WHERE c.price = 19.99 AND c.discount > 0.5"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.price = ? AND c.discount > ?"
        self.assertEqual(result, expected)

    def test_sanitize_boolean_literals(self):
        """Boolean literals should be replaced with ?."""
        query = "SELECT * FROM c WHERE c.active = true AND c.deleted = false"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.active = ? AND c.deleted = ?"
        self.assertEqual(result, expected)

    def test_sanitize_boolean_literals_case_insensitive(self):
        """Boolean literals in any case should be replaced."""
        query = "SELECT * FROM c WHERE c.flag1 = TRUE AND c.flag2 = False"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.flag1 = ? AND c.flag2 = ?"
        self.assertEqual(result, expected)

    def test_sanitize_null_literals(self):
        """Null literals should be replaced with ?."""
        query = "SELECT * FROM c WHERE c.optional = null"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.optional = ?"
        self.assertEqual(result, expected)

    def test_sanitize_mixed_literals(self):
        """Query with multiple types of literals should all be sanitized."""
        query = "SELECT * FROM c WHERE c.name = 'Alice' AND c.age = 30 AND c.active = true AND c.score = 95.5"

        result = sanitize_query(query, None)

        expected = "SELECT * FROM c WHERE c.name = '?' AND c.age = ? AND c.active = ? AND c.score = ?"
        self.assertEqual(result, expected)

    def test_sanitize_preserves_parameter_placeholders(self):
        """Should not replace @param placeholders even without parameter list."""
        query = "SELECT * FROM c WHERE c.id = @id AND c.value = 123"

        result = sanitize_query(query, None)

        # @id should remain, but 123 should be sanitized
        expected = "SELECT * FROM c WHERE c.id = @id AND c.value = ?"
        self.assertEqual(result, expected)

    def test_sanitize_empty_string(self):
        """Empty query should return empty."""
        result = sanitize_query("", None)
        self.assertEqual(result, "")

    def test_sanitize_complex_query(self):
        """Complex query with nested conditions."""
        query = """
        SELECT * FROM c 
        WHERE c.category = 'electronics' 
        AND c.price > 100 
        AND (c.inStock = true OR c.onOrder = false)
        AND c.rating >= 4.5
        """

        result = sanitize_query(query, None)

        # All literals should be sanitized
        self.assertIn("'?'", result)
        self.assertNotIn("'electronics'", result)
        self.assertNotIn("100", result)
        self.assertNotIn("4.5", result)
        self.assertIn("?", result)

    def test_sanitize_scientific_notation_literals(self):
        """Scientific notation literals should be sanitized as a single value."""
        query = "SELECT * FROM c WHERE c.large = 1.5e10 AND c.small = -2E-3"

        result = sanitize_query(query, None)

        self.assertEqual(result, "SELECT * FROM c WHERE c.large = ? AND c.small = ?")

    def test_sanitize_parameterized_query_with_scientific_notation_literal(self):
        """Parameterized query text should remain unchanged when parameters are present."""
        query = "SELECT * FROM c WHERE c.id = @id AND c.large = 1.5e10"

        result = sanitize_query(query, [{"name": "@id", "value": "item-1"}])

        self.assertEqual(result, query)


class TestCosmosSpanAttributes(unittest.TestCase):
    """Test Cosmos DB span attribute addition logic."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_span = Mock()
        self.mock_span_impl = Mock()
        self.mock_span_impl.get_current_span.return_value = self.mock_span
        self.mock_span.is_recording.return_value = True

        # Mock the span wrapper
        self.mock_span_wrapper = Mock()
        self.mock_span_impl.return_value = self.mock_span_wrapper

    def test_extract_headers_parses_supported_values(self):
        """Header extraction should parse supported numeric header values."""
        headers = {
            HttpHeaders.RequestCharge: "3.5",
            HttpHeaders.ActivityId: "activity-id",
            HttpHeaders.SubStatus: "1002",
            HttpHeaders.ItemCount: "7",
            HttpHeaders.ContentLength: "128",
        }

        _extract_headers(self.mock_span_wrapper, headers)

        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE), 3.5)
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_RESPONSE_SUB_STATUS_CODE), 1002)
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_RESPONSE_RETURNED_ROWS), 7)

    def test_add_response_attributes_cosmos_dict_extracts_headers(self):
        """CosmosDict responses should emit supported telemetry from real response headers."""
        result = CosmosDict(
            {"id": "item-1"},
            response_headers={HttpHeaders.RequestCharge: "2.25", HttpHeaders.SubStatus: "1002"},
        )

        _add_response_attributes(self.mock_span_wrapper, result)

        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE), 2.25)
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_RESPONSE_SUB_STATUS_CODE), 1002)

    def test_add_response_attributes_cosmos_list_uses_list_branch(self):
        """CosmosList responses should emit len-based item count and supported headers."""
        result = CosmosList(
            [{"id": "item-1"}, {"id": "item-2"}],
            response_headers={HttpHeaders.RequestCharge: "1.5"},
        )

        _add_response_attributes(self.mock_span_wrapper, result)

        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_RESPONSE_RETURNED_ROWS), 2)
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE), 1.5)

    def test_add_response_attributes_generic_response_with_status_code(self):
        """Generic response objects should emit status from both attribute and headers."""

        class _GenericResponse:
            status_code = 204

            @staticmethod
            def get_response_headers():
                return {HttpHeaders.RequestCharge: "1.0"}

        _add_response_attributes(self.mock_span_wrapper, _GenericResponse())

        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_RESPONSE_STATUS_CODE), "204")
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE), 1.0)

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_add_cosmos_attributes_basic(self, mock_settings):
        """Test basic attribute addition."""
        mock_settings.tracing_implementation.return_value = self.mock_span_impl

        # Create mock container
        mock_container = Mock()
        mock_container.id = "test-container"
        mock_container.container_link = "/dbs/test-db/colls/test-container"
        mock_container.client_connection = Mock()

        # Call the function
        _add_cosmos_attributes(
            self.mock_span_wrapper,
            _Constants.OpenTelemetryOperationNames.CREATE_ITEM,
            (mock_container,),
            {}
        )

        # Verify core attributes were added
        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}

        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_SYSTEM_NAME), "azure.cosmosdb")
        self.assertEqual(
            calls.get(_Constants.OpenTelemetryAttributes.DB_OPERATION_NAME),
            _Constants.OpenTelemetryOperationNames.CREATE_ITEM,
        )
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_COLLECTION_NAME), "test-container")
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_NAMESPACE), "test-db")

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_add_cosmos_attributes_with_query(self, mock_settings):
        """Query text should be emitted only when explicit opt-in is enabled."""
        mock_settings.tracing_implementation.return_value = self.mock_span_impl

        mock_container = Mock()
        mock_container.id = "test-container"
        mock_container.container_link = "/dbs/test-db/colls/test-container"
        mock_container.client_connection = Mock()

        query = "SELECT * FROM c WHERE c.id = 'test123' AND c.value = 100"

        with patch.dict(os.environ, {_Constants.OTEL_ENABLE_QUERY_TEXT: "true"}, clear=False):
            _add_cosmos_attributes(
                self.mock_span_wrapper,
                _Constants.OpenTelemetryOperationNames.QUERY_ITEMS,
                (mock_container,),
                {"query": query}
            )

        # Find the query text attribute
        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        query_text = calls.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT)

        # Query should be sanitized
        self.assertIsNotNone(query_text)
        self.assertNotIn("test123", query_text)
        self.assertNotIn("100", query_text)
        self.assertIn("'?'", query_text)
        self.assertIn("?", query_text)

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_add_cosmos_attributes_with_parameterized_query(self, mock_settings):
        """Test attribute addition with parameterized query (should NOT be sanitized)."""
        mock_settings.tracing_implementation.return_value = self.mock_span_impl

        mock_container = Mock()
        mock_container.id = "test-container"
        mock_container.container_link = "/dbs/test-db/colls/test-container"
        mock_container.client_connection = Mock()

        query = "SELECT * FROM c WHERE c.id = @id AND c.value = @value"
        parameters = [{"name": "@id", "value": "test123"}, {"name": "@value", "value": 100}]

        with patch.dict(os.environ, {_Constants.OTEL_ENABLE_QUERY_TEXT: "true"}, clear=False):
            _add_cosmos_attributes(
                self.mock_span_wrapper,
                _Constants.OpenTelemetryOperationNames.QUERY_ITEMS,
                (mock_container,),
                {"query": query, "parameters": parameters}
            )

        # Find the query text attribute
        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        query_text = calls.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT)

        # Query should NOT be sanitized (has parameters)
        self.assertIsNotNone(query_text)
        self.assertEqual(query_text, query)
        self.assertIn("@id", query_text)
        self.assertIn("@value", query_text)

        # Parameter VALUES should NOT be logged
        for key in calls.keys():
            self.assertNotIn("db.query.parameter", key)

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_query_text_not_emitted_without_opt_in(self, mock_settings):
        """db.query.text should not be emitted unless explicit opt-in is enabled."""
        mock_settings.tracing_implementation.return_value = self.mock_span_impl

        mock_container = Mock()
        mock_container.id = "test-container"
        mock_container.container_link = "/dbs/test-db/colls/test-container"
        mock_container.client_connection = Mock()

        _add_cosmos_attributes(
            self.mock_span_wrapper,
            _Constants.OpenTelemetryOperationNames.QUERY_ITEMS,
            (mock_container,),
            {"query": "SELECT * FROM c WHERE c.id = 'secret'"}
        )

        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        self.assertNotIn(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, calls)

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_query_text_emitted_when_query_text_opted_in(self, mock_settings):
        """OTEL_ENABLE_QUERY_TEXT should enable db.query.text emission."""
        mock_settings.tracing_implementation.return_value = self.mock_span_impl

        mock_container = Mock()
        mock_container.id = "test-container"
        mock_container.container_link = "/dbs/test-db/colls/test-container"
        mock_container.client_connection = Mock()

        with patch.dict(os.environ, {_Constants.OTEL_ENABLE_QUERY_TEXT: "true"}, clear=False):
            _add_cosmos_attributes(
                self.mock_span_wrapper,
                _Constants.OpenTelemetryOperationNames.QUERY_ITEMS,
                (mock_container,),
                {"query": "SELECT * FROM c WHERE c.id = 'secret'"}
            )

        calls = {call[0][0]: call[0][1] for call in self.mock_span_wrapper.add_attribute.call_args_list}
        self.assertEqual(calls.get(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT), "SELECT * FROM c WHERE c.id = '?'")

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_add_cosmos_attributes_no_span(self, mock_settings):
        """Test that function handles gracefully when no span exists."""
        mock_settings.tracing_implementation.return_value = None

        mock_container = Mock()
        mock_container.id = "test-container"

        # Should not raise exception
        try:
            _add_cosmos_attributes(
                self.mock_span_wrapper,
                _Constants.OpenTelemetryOperationNames.CREATE_ITEM,
                (mock_container,),
                {}
            )
        except Exception as e:
            self.fail(f"Function raised exception when no span: {e}")


class TestDecoratorIntegration(unittest.TestCase):
    """Test the decorator integration."""

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_sync_decorator_execution(self, mock_settings):
        """Test sync decorator executes function correctly."""
        mock_span_impl = Mock()
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_span_impl.get_current_span.return_value = mock_span
        mock_settings.tracing_implementation.return_value = mock_span_impl

        @cosmos_span_attributes(operation_name=_Constants.OpenTelemetryOperationNames.READ_ITEM)
        def test_function():
            return "test_result"

        result = test_function()
        self.assertEqual(result, "test_result")

    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_sync_decorator_with_exception(self, mock_settings):
        """Test sync decorator handles exceptions correctly."""
        mock_span_impl = Mock()
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_span_impl.get_current_span.return_value = mock_span
        mock_settings.tracing_implementation.return_value = mock_span_impl

        @cosmos_span_attributes(operation_name=_Constants.OpenTelemetryOperationNames.READ_ITEM)
        def test_function():
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            test_function()

    @patch('azure.cosmos._cosmos_span_attributes._add_cosmos_telemetry')
    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_sync_decorator_normalizes_dict_query_payload(self, mock_settings, mock_add_cosmos_telemetry):
        """Decorator should normalize dict-style query payloads before telemetry is emitted."""
        mock_span_impl = Mock()
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_span_impl.get_current_span.return_value = mock_span
        mock_settings.tracing_implementation.return_value = mock_span_impl

        @cosmos_span_attributes(operation_name=_Constants.OpenTelemetryOperationNames.QUERY_ITEMS)
        def test_function(**kwargs):
            return ["ok"]

        test_function(query={"query": "SELECT * FROM c WHERE c.id = @id", "parameters": [{"name": "@id", "value": "1"}]})

        telemetry_kwargs = mock_add_cosmos_telemetry.call_args.args[2]
        self.assertEqual(telemetry_kwargs["query"], "SELECT * FROM c WHERE c.id = @id")
        self.assertEqual(telemetry_kwargs["parameters"], [{"name": "@id", "value": "1"}])


if __name__ == '__main__':
    unittest.main()


