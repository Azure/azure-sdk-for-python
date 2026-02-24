# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
