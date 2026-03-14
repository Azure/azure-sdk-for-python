# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import unittest
import json
from json import JSONDecodeError
from azure.appconfiguration.provider._json import (
    remove_json_comments,
    _find_string_end,
)


class TestJsonUtils(unittest.TestCase):
    def test_remove_json_comments_no_comments(self):
        # Test a simple JSON with no comments
        input_json = '{"key": "value", "number": 123}'
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value")
        self.assertEqual(parsed["number"], 123)

    def test_remove_json_comments_single_line(self):
        # Test removing single line comments
        input_json = """{
            "key": "value" // this is a comment
        }"""
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value")

    def test_remove_json_comments_single_line_no_newline(self):
        # Test removing single line comments without a newline at the end
        input_json = '{ "key": "value" } // this is a comment'
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value")

    def test_remove_json_comments_multi_line(self):
        # Test removing multi-line comments
        input_json = """{/* This is a
            multi-line
            comment */
            "key": "value"
        }"""
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value")

    def test_remove_json_comments_mixed(self):
        # Test removing both single-line and multi-line comments
        input_json = """{
            "key1": "value1", // single line comment
            /* multi-line comment
            spanning multiple lines */
            "key2": "value2"
        }"""
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key1"], "value1")
        self.assertEqual(parsed["key2"], "value2")

    def test_remove_json_comments_inside_string(self):
        # Test that comments within string literals are not removed
        input_json = '{"key": "value with // not a comment"}'
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value with // not a comment")

        input_json = '{"key": "value with /* not a comment */"}'
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value with /* not a comment */")

    def test_remove_json_comments_nested_comments(self):
        # Test with nested comments (which aren't really supported in JSON)
        input_json = """{
            /* outer comment /* inner comment */ */
            "key": "value"
        }"""
        result = remove_json_comments(input_json)
        # Verify the json is valid after comment removal, we don't support nested comments
        with self.assertRaises(JSONDecodeError):
            json.loads(result)

    def test_remove_json_comments_escaped_quotes(self):
        # Test with escaped quotes
        input_json = '{"key": "value with \\" escaped quote // not a comment"}'
        result = remove_json_comments(input_json)
        # Verify the result is valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], 'value with " escaped quote // not a comment')

    def test_find_string_end_basic(self):
        # Test basic string end finding
        text = '"string" more'
        index = _find_string_end(text, 1)
        self.assertEqual(index, 8)
        self.assertEqual(text[1:index], 'string"')

    def test_find_string_end_escaped_quote(self):
        # Test with escaped quotes
        text = '"escaped \\" quote" end'
        index = _find_string_end(text, 1)
        self.assertEqual(index, 18)
        self.assertEqual(text[1:index], 'escaped \\" quote"')

    def test_find_string_end_unterminated(self):
        # Test with unterminated string
        text = '"unterminated string'
        with self.assertRaises(ValueError):
            _find_string_end(text, 1)

    def test_find_string_end_multiple_escapes(self):
        # Test with multiple escape characters
        text = '"multiple \\\\" end'
        index = _find_string_end(text, 1)
        self.assertEqual(index, 13)
        self.assertEqual(text[1:index], 'multiple \\\\"')

    def test_remove_json_comments_unterminated_string(self):
        # Test with unterminated string
        input_json = '{ "key": "unterminated string }'
        with self.assertRaises(ValueError):
            remove_json_comments(input_json)

    def test_remove_json_comments_unterminated_multiline(self):
        # Test with unterminated multi-line comment
        # This should raise a ValueError
        input_json = """{
            "key": "value"
            /* unterminated comment
        }"""
        with self.assertRaises(ValueError):
            remove_json_comments(input_json)

        # Another test case for unterminated multi-line comment
        input_json2 = """{
            "key1": "value1",
            "key2": "value2" /* unterminated comment
        }"""
        with self.assertRaises(ValueError):
            remove_json_comments(input_json2)
