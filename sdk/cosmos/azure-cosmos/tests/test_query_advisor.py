# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import json
import unittest
from urllib.parse import quote

from azure.cosmos._query_advisor import (
    QueryAdvice,
    QueryAdviceEntry,
    RuleDirectory,
    get_query_advice_info
)


class TestQueryAdvisor(unittest.TestCase):
    """Unit tests for query advisor functionality."""

    def test_rule_directory_loads_rules(self):
        """Test that RuleDirectory loads all 10 rules."""
        directory = RuleDirectory()
        
        # Check URL prefix
        self.assertTrue(directory.url_prefix.startswith("https://"))
        
        # Check all 10 rules exist
        for rule_id in [f"QA{1000 + i}" for i in range(10)]:
            message = directory.get_rule_message(rule_id)
            if rule_id == "QA1006":
                self.assertIsNotNone(message)
                self.assertIsInstance(message, str)
            else:
                self.assertIsNotNone(message, f"Rule {rule_id} should have a message")
                self.assertIsInstance(message, str)

    def test_rule_directory_invalid_rule(self):
        """Test that invalid rule IDs return None."""
        directory = RuleDirectory()
        self.assertIsNone(directory.get_rule_message("INVALID_RULE"))

    def test_query_advice_entry_from_dict(self):
        """Test creating QueryAdviceEntry from dictionary."""
        data = {"Id": "QA1000", "Params": ["param1", "param2"]}
        entry = QueryAdviceEntry.from_dict(data)
        
        self.assertEqual(entry.id, "QA1000")
        self.assertEqual(entry.parameters, ["param1", "param2"])

    def test_query_advice_entry_to_string(self):
        """Test formatting QueryAdviceEntry as string."""
        directory = RuleDirectory()
        entry = QueryAdviceEntry("QA1000", [])
        
        result = entry.to_string(directory)
        
        self.assertIsNotNone(result)
        self.assertIn("QA1000:", result)
        self.assertIn("ARRAY_CONTAINS", result)
        self.assertIn(directory.url_prefix, result)
        self.assertIn("QA1000", result)

    def test_query_advice_entry_with_parameters(self):
        """Test formatting QueryAdviceEntry with parameters."""
        directory = RuleDirectory()
        # Create a mock entry that would use parameters
        entry = QueryAdviceEntry("QA1000", ["field1", "field2"])
        
        result = entry.to_string(directory)
        
        self.assertIsNotNone(result)
        self.assertIn("QA1000:", result)

    def test_query_advice_entry_unknown_rule_returns_fallback_link(self):
        """Test that an unknown rule ID returns a fallback doc link and logs a warning."""
        directory = RuleDirectory()
        entry = QueryAdviceEntry("QA9999")

        with self.assertLogs("azure.cosmos._query_advisor._query_advice", level="WARNING") as cm:
            result = entry.to_string(directory)

        directory = RuleDirectory()
        self.assertIsNotNone(result)
        self.assertIn("QA9999", result)
        self.assertIn(directory.url_prefix + "QA9999", result)
        self.assertTrue(any("QA9999" in msg for msg in cm.output))

    def test_query_advice_to_string_unknown_rule_included(self):
        """Test that QueryAdvice.to_string includes entries with unknown rule IDs."""
        data = [{"Id": "QA9999", "Params": []}]
        encoded = quote(json.dumps(data))

        advice = QueryAdvice.try_create_from_string(encoded)
        with self.assertLogs("azure.cosmos._query_advisor._query_advice", level="WARNING"):
            result = advice.to_string()

        directory = RuleDirectory()
        self.assertIsInstance(result, str)
        self.assertIn("QA9999", result)
        self.assertIn(directory.url_prefix + "QA9999", result)

    def test_get_query_advice_info_unknown_rule(self):
        """Test end-to-end get_query_advice_info with an unknown rule ID returns fallback link."""
        data = [{"Id": "QA9999", "Params": []}]
        encoded = quote(json.dumps(data))

        with self.assertLogs("azure.cosmos._query_advisor._query_advice", level="WARNING"):
            result = get_query_advice_info(encoded)

        directory = RuleDirectory()
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")
        self.assertIn("QA9999", result)
        self.assertIn(directory.url_prefix + "QA9999", result)

    def test_query_advice_try_create_from_string_single_entry(self):
        """Test parsing query advice with single entry."""
        # Create URL-encoded JSON
        data = [{"Id": "QA1002", "Params": []}]
        json_str = json.dumps(data)
        encoded = quote(json_str)
        
        advice = QueryAdvice.try_create_from_string(encoded)
        
        self.assertIsNotNone(advice)
        self.assertEqual(len(advice.entries), 1)
        self.assertEqual(advice.entries[0].id, "QA1002")

    def test_query_advice_try_create_from_string_multiple_entries(self):
        """Test parsing query advice with multiple entries."""
        # Create URL-encoded JSON
        data = [
            {"Id": "QA1008", "Params": []},
            {"Id": "QA1009", "Params": []}
        ]
        json_str = json.dumps(data)
        encoded = quote(json_str)
        
        advice = QueryAdvice.try_create_from_string(encoded)
        
        self.assertIsNotNone(advice)
        self.assertEqual(len(advice.entries), 2)
        self.assertEqual(advice.entries[0].id, "QA1008")
        self.assertEqual(advice.entries[1].id, "QA1009")

    def test_query_advice_try_create_from_string_null_input(self):
        """Test that None input returns None."""
        advice = QueryAdvice.try_create_from_string(None)
        self.assertIsNone(advice)

    def test_query_advice_try_create_from_string_invalid_json(self):
        """Test that invalid JSON returns None."""
        advice = QueryAdvice.try_create_from_string("not-valid-json")
        self.assertIsNone(advice)

    def test_query_advice_try_create_from_string_empty_input(self):
        """Test that empty string returns None."""
        advice = QueryAdvice.try_create_from_string("")
        self.assertIsNone(advice)

    def test_query_advice_to_string_single_entry(self):
        """Test formatting QueryAdvice with single entry."""
        data = [{"Id": "QA1002", "Params": []}]
        json_str = json.dumps(data)
        encoded = quote(json_str)
        
        advice = QueryAdvice.try_create_from_string(encoded)
        result = advice.to_string()
        
        self.assertIsInstance(result, str)
        self.assertIn("QA1002:", result)
        self.assertIn("STARTSWITH", result)
        self.assertIn("https://", result)

    def test_query_advice_to_string_multiple_entries(self):
        """Test formatting QueryAdvice with multiple entries as multi-line string."""
        data = [
            {"Id": "QA1008", "Params": []},
            {"Id": "QA1009", "Params": []}
        ]
        json_str = json.dumps(data)
        encoded = quote(json_str)
        
        advice = QueryAdvice.try_create_from_string(encoded)
        result = advice.to_string()
        
        self.assertIsInstance(result, str)
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertIn("QA1008:", lines[0])
        self.assertIn("QA1009:", lines[1])
        self.assertIn("GetCurrentTicks", lines[0])
        self.assertIn("GetCurrentTimestamp", lines[1])

    def test_query_advice_to_string_empty(self):
        """Test formatting empty QueryAdvice."""
        advice = QueryAdvice([])
        result = advice.to_string()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "")

    def test_get_query_advice_info_valid_input(self):
        """Test end-to-end get_query_advice_info with valid input."""
        data = [{"Id": "QA1002", "Params": []}]
        json_str = json.dumps(data)
        encoded = quote(json_str)
        
        result = get_query_advice_info(encoded)
        
        self.assertIsInstance(result, str)
        self.assertIn("QA1002:", result)
        self.assertIn("STARTSWITH", result)

    def test_get_query_advice_info_null_input(self):
        """Test get_query_advice_info with None input."""
        result = get_query_advice_info(None)
        self.assertEqual(result, "")

    def test_get_query_advice_info_invalid_input(self):
        """Test get_query_advice_info with invalid input."""
        result = get_query_advice_info("invalid-input")
        self.assertEqual(result, "")

    def test_query_advice_filters_null_entries(self):
        """Test that QueryAdvice filters out None entries."""
        advice = QueryAdvice([QueryAdviceEntry("QA1000"), None, QueryAdviceEntry("QA1002")])
        
        self.assertEqual(len(advice.entries), 2)
        self.assertEqual(advice.entries[0].id, "QA1000")
        self.assertEqual(advice.entries[1].id, "QA1002")


if __name__ == "__main__":
    unittest.main()
