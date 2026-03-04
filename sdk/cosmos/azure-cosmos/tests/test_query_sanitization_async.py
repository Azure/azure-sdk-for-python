# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for query sanitization in async cosmos_span_attributes_async decorator."""

import unittest
from azure.cosmos.aio._cosmos_span_attributes_async import _sanitize_query


class TestQuerySanitizationAsync(unittest.TestCase):
    """Test query sanitization for async operations."""

    def test_parameterized_query_not_sanitized(self):
        """Parameterized queries with @param should NOT be sanitized."""
        query = "SELECT * FROM c WHERE c.id = @id"
        result = _sanitize_query(query)
        self.assertEqual(result, query, "Parameterized query should not be modified")

    def test_parameterized_query_multiple_params(self):
        """Multiple @params should be preserved."""
        query = "SELECT * FROM c WHERE c.price > @minPrice AND c.category = @cat"
        result = _sanitize_query(query)
        self.assertEqual(result, query)

    def test_string_literal_sanitized(self):
        """String literals should be replaced with '?'."""
        query = "SELECT * FROM c WHERE c.name = 'John Doe'"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?'")

    def test_multiple_string_literals(self):
        """Multiple string literals should all be sanitized."""
        query = "SELECT * FROM c WHERE c.name = 'John' AND c.city = 'Seattle'"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?' AND c.city = '?'")

    def test_numeric_literal_sanitized(self):
        """Numeric literals should be replaced with ?."""
        query = "SELECT * FROM c WHERE c.age = 25"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.age = ?")

    def test_float_literal_sanitized(self):
        """Float literals should be sanitized."""
        query = "SELECT * FROM c WHERE c.price = 19.99"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.price = ?")

    def test_boolean_literals_sanitized(self):
        """Boolean literals (true/false) should be sanitized."""
        query = "SELECT * FROM c WHERE c.active = true AND c.deleted = false"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.active = ? AND c.deleted = ?")

    def test_null_literal_sanitized(self):
        """Null literals should be sanitized."""
        query = "SELECT * FROM c WHERE c.value = null"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.value = ?")

    def test_mixed_literals(self):
        """Mix of different literal types should all be sanitized."""
        query = "SELECT * FROM c WHERE c.name = 'Alice' AND c.age = 30 AND c.active = true"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?' AND c.age = ? AND c.active = ?")

    def test_parameterized_with_literals(self):
        """Parameterized queries can have literals that should be sanitized."""
        query = "SELECT * FROM c WHERE c.id = @id AND c.status = 'active'"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.id = @id AND c.status = '?'")

    def test_complex_query_with_functions(self):
        """Complex queries with functions and literals."""
        query = "SELECT * FROM c WHERE CONTAINS(c.name, 'test') AND c.count > 100"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE CONTAINS(c.name, '?') AND c.count > ?")

    def test_in_clause_with_literals(self):
        """IN clause with multiple literals."""
        query = "SELECT * FROM c WHERE c.category IN ('A', 'B', 'C')"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.category IN ('?', '?', '?')")

    def test_empty_string_literal(self):
        """Empty string literals should be sanitized."""
        query = "SELECT * FROM c WHERE c.name = ''"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.name = '?'")

    def test_string_with_escaped_quotes(self):
        """String literals with escaped quotes."""
        query = "SELECT * FROM c WHERE c.message = 'She said \\'hello\\''"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.message = '?'")

    def test_negative_numbers(self):
        """Negative numbers should be sanitized."""
        query = "SELECT * FROM c WHERE c.temperature = -5.5 AND c.balance = -100"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.temperature = ? AND c.balance = ?")

    def test_real_world_auth_query(self):
        """Real-world authentication query with sensitive data."""
        query = "SELECT * FROM c WHERE c.username = 'admin@example.com' AND c.password = 'P@ssw0rd123'"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.username = '?' AND c.password = '?'")

    def test_real_world_financial_query(self):
        """Real-world financial query with sensitive amounts."""
        query = "SELECT * FROM c WHERE c.accountId = 'ACC-12345' AND c.balance > 50000.00"
        result = _sanitize_query(query)
        self.assertEqual(result, "SELECT * FROM c WHERE c.accountId = '?' AND c.balance > ?")


if __name__ == '__main__':
    unittest.main()

