# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for serialize_body_to_bytes, which turns a request body into the bytes
the SDK sends. Each test checks the exact bytes, or the error, for one kind of
input.
"""
import unittest

from azure.cosmos._helpers._wire_encoding import serialize_body_to_bytes


class TestEmptyAndPrimitiveBodies(unittest.TestCase):
    """Bodies that are not turned into JSON: None, bytes, bytearray and str.

    They are returned as bytes without changing their content.
    """

    def test_none_returns_empty_bytes_rust(self):
        """``None`` means "no body" (as for delete) and gives ``b""``."""
        self.assertEqual(serialize_body_to_bytes(None), b"")

    def test_bytes_input_passes_through_unchanged_rust(self):
        """A ``bytes`` body is returned as it is."""
        payload = b'{"id":"x","total":1}'
        result = serialize_body_to_bytes(payload)
        self.assertEqual(result, payload)
        self.assertIsInstance(result, bytes)

    def test_bytearray_input_returns_bytes_rust(self):
        """A ``bytearray`` body is returned as a separate ``bytes`` copy, so later
        changes to the bytearray do not change the request body."""
        buffer = bytearray(b'{"k":1}')
        result = serialize_body_to_bytes(buffer)
        self.assertEqual(result, b'{"k":1}')
        self.assertIsInstance(result, bytes)
        # Changing the bytearray must not change the result.
        buffer[0] = ord("X")
        self.assertEqual(result, b'{"k":1}')

    def test_str_input_is_utf8_encoded_rust(self):
        """A ``str`` body is taken to be JSON text and is UTF-8 encoded. An empty
        string gives ``b""``."""
        self.assertEqual(serialize_body_to_bytes('{"id":"x"}'), b'{"id":"x"}')
        self.assertEqual(serialize_body_to_bytes(""), b"")


class TestDictListSerialization(unittest.TestCase):
    """Bodies that are turned into JSON: dict, list and tuple.

    The JSON is compact (no spaces after "," or ":"), keeps the order of dict
    keys, and by default escapes non-ASCII characters as ``\\uXXXX``.
    """

    def test_simple_dict_compact_no_spaces_rust(self):
        """A dict becomes compact JSON with no spaces."""
        self.assertEqual(
            serialize_body_to_bytes({"id": "order-42", "total": 99.5}),
            b'{"id":"order-42","total":99.5}',
        )

    def test_dict_key_insertion_order_preserved_rust(self):
        """Keys appear in the order they were added to the dict."""
        body = {"z": 1, "a": 2, "m": 3}
        self.assertEqual(
            serialize_body_to_bytes(body),
            b'{"z":1,"a":2,"m":3}',
        )

    def test_integer_stays_integer_not_float_rust(self):
        """An integer stays an integer: ``123``, not ``123.0``."""
        self.assertEqual(
            serialize_body_to_bytes({"n": 123}),
            b'{"n":123}',
        )

    def test_float_with_simple_decimal_keeps_decimal_rust(self):
        """``99.5`` stays ``99.5``, with no rounding and no scientific notation."""
        self.assertEqual(
            serialize_body_to_bytes({"price": 99.5}),
            b'{"price":99.5}',
        )

    def test_booleans_render_lowercase_rust(self):
        """``True`` and ``False`` become ``true`` and ``false``."""
        self.assertEqual(
            serialize_body_to_bytes({"flag": True, "off": False}),
            b'{"flag":true,"off":false}',
        )

    def test_none_value_renders_as_json_null_rust(self):
        """A ``None`` value inside the body becomes ``null``. This is different from
        a body that is ``None``, which means "no body"."""
        self.assertEqual(
            serialize_body_to_bytes({"v": None}),
            b'{"v":null}',
        )

    def test_nested_dict_serializes_recursively_rust(self):
        """Nested dicts follow the same rules."""
        body = {"id": "x", "meta": {"region": "us-east", "count": 3}}
        self.assertEqual(
            serialize_body_to_bytes(body),
            b'{"id":"x","meta":{"region":"us-east","count":3}}',
        )

    def test_list_input_serializes_as_json_array_rust(self):
        """A list becomes a JSON array."""
        self.assertEqual(
            serialize_body_to_bytes([1, 2, 3]),
            b"[1,2,3]",
        )

    def test_tuple_input_serializes_as_json_array_rust(self):
        """A tuple becomes a JSON array, like a list."""
        self.assertEqual(
            serialize_body_to_bytes(("a", "b")),
            b'["a","b"]',
        )

    def test_non_ascii_string_value_uses_unicode_escape_rust(self):
        """By default, non-ASCII characters are escaped: ``"café"`` becomes
        ``"caf\\u00e9"``."""
        self.assertEqual(
            serialize_body_to_bytes({"name": "café"}),
            b'{"name":"caf\\u00e9"}',
        )


class TestUnsupportedTypeRaises(unittest.TestCase):
    """Any other type raises TypeError before a request is sent.

    The message names the type and lists the types that are accepted.
    """

    def test_object_input_raises_type_error_rust(self):
        """An instance of a custom class raises TypeError, and the message names
        the class."""
        class Custom:
            """A class the serializer does not accept."""

            pass

        with self.assertRaises(TypeError) as raised:
            serialize_body_to_bytes(Custom())
        self.assertIn("Custom", str(raised.exception))

    def test_int_input_raises_type_error_rust(self):
        """A plain integer as the whole body raises TypeError."""
        with self.assertRaises(TypeError):
            serialize_body_to_bytes(42)

    def test_set_input_raises_type_error_rust(self):
        """A set raises TypeError, because JSON has no set type."""
        with self.assertRaises(TypeError):
            serialize_body_to_bytes({"a", "b"})


if __name__ == "__main__":
    unittest.main()

