# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for query sanitization and async pager tracing behavior."""

import inspect
import unittest
from unittest.mock import Mock, patch

from azure.core.tracing.decorator import distributed_trace
from azure.cosmos._constants import _Constants
from azure.cosmos.aio._container import ContainerProxy
from azure.cosmos.aio._cosmos_client import CosmosClient
from azure.cosmos.aio._cosmos_span_attributes_async import sanitize_query
from azure.cosmos.aio._database import DatabaseProxy
from azure.cosmos.aio._user import UserProxy


class _EmptyAsyncIterable:
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


class TestQuerySanitizationAsync(unittest.TestCase):
    """Test query sanitization for async operations."""

    def test_parameterized_query_not_sanitized(self):
        """Parameterized queries with @param should NOT be sanitized."""
        query = "SELECT * FROM c WHERE c.id = @id"
        result = sanitize_query(query, None)
        self.assertEqual(result, query, "Parameterized query should not be modified")

    def test_parameterized_query_multiple_params(self):
        """Multiple @params should be preserved."""
        query = "SELECT * FROM c WHERE c.price > @minPrice AND c.category = @cat"
        result = sanitize_query(query, None)
        self.assertEqual(result, query)

    def test_string_literal_sanitized(self):
        """String literals should be replaced with '?'."""
        query = "SELECT * FROM c WHERE c.name = 'John Doe'"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?'")

    def test_multiple_string_literals(self):
        """Multiple string literals should all be sanitized."""
        query = "SELECT * FROM c WHERE c.name = 'John' AND c.city = 'Seattle'"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?' AND c.city = '?'")

    def test_numeric_literal_sanitized(self):
        """Numeric literals should be replaced with ?."""
        query = "SELECT * FROM c WHERE c.age = 25"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.age = ?")

    def test_float_literal_sanitized(self):
        """Float literals should be sanitized."""
        query = "SELECT * FROM c WHERE c.price = 19.99"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.price = ?")

    def test_boolean_literals_sanitized(self):
        """Boolean literals (true/false) should be sanitized."""
        query = "SELECT * FROM c WHERE c.active = true AND c.deleted = false"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.active = ? AND c.deleted = ?")

    def test_null_literal_sanitized(self):
        """Null literals should be sanitized."""
        query = "SELECT * FROM c WHERE c.value = null"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.value = ?")

    def test_boolean_field_names_preserved(self):
        """Field names containing 'true' or 'false' should NOT be sanitized (M7 fix)."""
        query = "SELECT * FROM c WHERE c.true = 'yes' AND c.false = 'no' AND c.isTrue = 1"
        result = sanitize_query(query, None)
        expected = "SELECT * FROM c WHERE c.true = '?' AND c.false = '?' AND c.isTrue = ?"
        self.assertEqual(result, expected)

    def test_mixed_literals(self):
        """Mix of different literal types should all be sanitized."""
        query = "SELECT * FROM c WHERE c.name = 'Alice' AND c.age = 30 AND c.active = true"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?' AND c.age = ? AND c.active = ?")

    def test_parameterized_with_literals(self):
        """Parameterized queries can have literals that should be sanitized."""
        query = "SELECT * FROM c WHERE c.id = @id AND c.status = 'active'"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.id = @id AND c.status = '?'")

    def test_parameterized_with_literals_and_parameters(self):
        """Inline literals are sanitized even when parameters are provided (M2 fix)."""
        query = "SELECT * FROM c WHERE c.id = @id AND c.status = 'active' AND c.priority >= 5"
        parameters = [{"name": "@id", "value": "thread-1"}]
        result = sanitize_query(query, parameters)
        expected = "SELECT * FROM c WHERE c.id = @id AND c.status = '?' AND c.priority >= ?"
        self.assertEqual(result, expected)

    def test_complex_query_with_functions(self):
        """Complex queries with functions and literals."""
        query = "SELECT * FROM c WHERE CONTAINS(c.name, 'test') AND c.count > 100"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE CONTAINS(c.name, '?') AND c.count > ?")

    def test_in_clause_with_literals(self):
        """IN clause with multiple literals."""
        query = "SELECT * FROM c WHERE c.category IN ('A', 'B', 'C')"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.category IN ('?', '?', '?')")

    def test_empty_string_literal(self):
        """Empty string literals should be sanitized."""
        query = "SELECT * FROM c WHERE c.name = ''"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?'")

    def test_string_with_escaped_quotes(self):
        """String literals with escaped quotes."""
        query = "SELECT * FROM c WHERE c.message = 'She said \\'hello\\''"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.message = '?'")

    def test_negative_numbers(self):
        """Negative numbers should be sanitized."""
        query = "SELECT * FROM c WHERE c.temperature = -5.5 AND c.balance = -100"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.temperature = ? AND c.balance = ?")

    def test_scientific_notation_literals(self):
        """Scientific notation literals should be sanitized as complete values."""
        query = "SELECT * FROM c WHERE c.large = 1.5e10 AND c.small = -2E-3"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.large = ? AND c.small = ?")

    def test_parameterized_query_with_scientific_notation_literal(self):
        """Inline scientific notation is sanitized even when parameters exist (M2 fix)."""
        query = "SELECT * FROM c WHERE c.id = @id AND c.large = 1.5e10"
        result = sanitize_query(query, [{"name": "@id", "value": "item-1"}])
        expected = "SELECT * FROM c WHERE c.id = @id AND c.large = ?"
        self.assertEqual(result, expected)

    def test_real_world_auth_query(self):
        """Real-world authentication query with sensitive data."""
        query = "SELECT * FROM c WHERE c.username = 'admin@example.com' AND c.password = 'P@ssw0rd123'"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.username = '?' AND c.password = '?'")

    def test_real_world_financial_query(self):
        """Real-world financial query with sensitive amounts."""
        query = "SELECT * FROM c WHERE c.accountId = 'ACC-12345' AND c.balance > 50000.00"
        result = sanitize_query(query, None)
        self.assertEqual(result, "SELECT * FROM c WHERE c.accountId = '?' AND c.balance > ?")


class TestAsyncPagerTracingRegression(unittest.TestCase):
    """Regression tests for aio pager factory tracing behavior."""

    def test_cosmos_async_span_decorator_preserves_async_iterable_factories(self):
        """Sync aio pager factories must remain directly iterable with async for."""

        from azure.cosmos.aio._cosmos_span_attributes_async import cosmos_span_attributes_async

        @distributed_trace
        @cosmos_span_attributes_async(operation_name=_Constants.OpenTelemetryOperationNames.QUERY_ITEMS)
        def pager_factory():
            return _EmptyAsyncIterable()

        result = pager_factory()

        self.assertFalse(inspect.isawaitable(result))
        self.assertTrue(hasattr(result, "__aiter__"))

    def test_aio_pager_factory_methods_are_not_coroutines(self):
        """Aio methods used with async for must not become coroutine functions."""
        pager_methods = [
            CosmosClient.list_databases,
            CosmosClient.query_databases,
            DatabaseProxy.list_containers,
            DatabaseProxy.query_containers,
            DatabaseProxy.list_users,
            DatabaseProxy.query_users,
            ContainerProxy.read_all_items,
            ContainerProxy.query_items,
            ContainerProxy.query_items_change_feed,
            ContainerProxy.list_conflicts,
            ContainerProxy.query_conflicts,
            ContainerProxy.read_feed_ranges,
            UserProxy.list_permissions,
            UserProxy.query_permissions,
        ]

        for method in pager_methods:
            with self.subTest(method=method.__qualname__):
                self.assertFalse(inspect.iscoroutinefunction(method))

    def test_true_aio_coroutine_methods_remain_coroutines(self):
        """Actual aio coroutine methods must remain coroutine functions."""
        coroutine_methods = [
            CosmosClient.create_database,
            DatabaseProxy.create_container,
            ContainerProxy.create_item,
            ContainerProxy.read_item,
            UserProxy.create_permission,
        ]

        for method in coroutine_methods:
            with self.subTest(method=method.__qualname__):
                self.assertTrue(inspect.iscoroutinefunction(method))

    @patch('azure.cosmos.aio._cosmos_span_attributes_async._add_cosmos_telemetry')
    @patch('azure.cosmos.aio._cosmos_span_attributes_async._add_cosmos_error_telemetry')
    @patch('azure.cosmos._cosmos_span_attributes.settings')
    def test_async_decorator_normalizes_dict_query_payload(
        self,
        mock_settings,
        _mock_add_error_telemetry,
        mock_add_cosmos_telemetry,
    ):
        """Decorator should normalize dict-style query payloads before telemetry is emitted."""
        mock_span_impl = Mock()
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_span_impl.get_current_span.return_value = mock_span
        mock_settings.tracing_implementation.return_value = mock_span_impl

        from azure.cosmos.aio._cosmos_span_attributes_async import cosmos_span_attributes_async

        @cosmos_span_attributes_async(operation_name=_Constants.OpenTelemetryOperationNames.QUERY_ITEMS)
        def pager_factory(**kwargs):
            return _EmptyAsyncIterable()

        pager_factory(query={"query": "SELECT * FROM c WHERE c.id = @id", "parameters": [{"name": "@id", "value": "1"}]})

        telemetry_kwargs = mock_add_cosmos_telemetry.call_args.args[2]
        self.assertEqual(telemetry_kwargs["query"], "SELECT * FROM c WHERE c.id = @id")
        self.assertEqual(telemetry_kwargs["parameters"], [{"name": "@id", "value": "1"}])


if __name__ == "__main__":
    unittest.main()

