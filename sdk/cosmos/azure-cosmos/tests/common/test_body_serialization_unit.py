# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline examples for serialize_body_to_bytes.

Assert exact bytes or errors for the listed inputs and compare a finite
input table with an inline reproduction of the legacy serializer.
No network transmission, stored-item representation, or exhaustive
serializer equivalence is established.
"""
import json
import unittest

from azure.cosmos._helpers._wire_encoding import serialize_body_to_bytes


class TestEmptyAndPrimitiveBodies(unittest.TestCase):
    """Inputs that skip ``json.dumps`` entirely — passthrough cases.

    ``None``, ``str``, ``bytes`` and ``bytearray`` are all already
    "already in byte form" (or carry the explicit "no body" signal), so the
    helper just normalises them to ``bytes`` without re-serialising.
    These tests cover that passthrough behaviour.
    """

    def test_none_returns_empty_bytes(self):
        """``body=None`` → ``b""`` (the "no payload" signal for ops like delete)."""
        self.assertEqual(serialize_body_to_bytes(None), b"")

    def test_bytes_input_passes_through_unchanged(self):
        """A ``bytes`` body (e.g. pre-encoded by a future Rust path) is returned as-is."""
        payload = b'{"id":"x","total":1}'
        result = serialize_body_to_bytes(payload)
        self.assertEqual(result, payload)
        self.assertIsInstance(result, bytes)

    def test_bytearray_input_returns_bytes(self):
        """A ``bytearray`` body returns an immutable ``bytes`` copy.

        The helper must hand back ``bytes`` (not ``bytearray``) so that
        downstream code can rely on ``body_bytes`` not changing under
        it if the original buffer is later mutated.
        """
        ba = bytearray(b'{"k":1}')
        result = serialize_body_to_bytes(ba)
        self.assertEqual(result, b'{"k":1}')
        self.assertIsInstance(result, bytes)
        # Mutating the original bytearray must not change the result.
        ba[0] = ord("X")
        self.assertEqual(result, b'{"k":1}')

    def test_str_input_is_utf8_encoded(self):
        """A ``str`` body is assumed to already be valid JSON text and is just UTF-8 encoded."""
        self.assertEqual(serialize_body_to_bytes('{"id":"x"}'), b'{"id":"x"}')


class TestDictListSerialization(unittest.TestCase):
    """The common case: ``dict`` / ``list`` / ``tuple`` is JSON-serialised.

    The output must use compact separators (no space after ``,`` or
    ``:``), preserve dict insertion order, keep ints as ints, render
    booleans lowercase, render ``None`` as ``null``, and escape
    non-ASCII characters as ``\\uXXXX``. All of those are the existing
    core-python pipeline's behaviour and the rest of the SDK (and
    customer fixtures) depend on it byte-for-byte.
    """

    def test_simple_dict_compact_no_spaces(self):
        """Dict → compact JSON with no incidental whitespace anywhere."""
        self.assertEqual(
            serialize_body_to_bytes({"id": "order-42", "total": 99.5}),
            b'{"id":"order-42","total":99.5}',
        )

    def test_dict_key_insertion_order_preserved(self):
        """Keys appear in the exact order the caller inserted them.

        Python dicts preserve insertion order since 3.7. The Cosmos
        service does not care about key order, but customer fixtures
        often do (string compare). This test locks the order in.
        """
        body = {"z": 1, "a": 2, "m": 3}
        self.assertEqual(
            serialize_body_to_bytes(body),
            b'{"z":1,"a":2,"m":3}',
        )

    def test_integer_stays_integer_not_float(self):
        """The sample integer is encoded as 123 rather than 123.0."""
        self.assertEqual(
            serialize_body_to_bytes({"n": 123}),
            b'{"n":123}',
        )

    def test_float_with_simple_decimal_keeps_decimal(self):
        """``99.5`` stays ``99.5`` — no scientific notation, no rounding."""
        self.assertEqual(
            serialize_body_to_bytes({"price": 99.5}),
            b'{"price":99.5}',
        )

    def test_booleans_render_lowercase(self):
        """Python ``True`` / ``False`` → JSON ``true`` / ``false`` (lowercase)."""
        self.assertEqual(
            serialize_body_to_bytes({"flag": True, "off": False}),
            b'{"flag":true,"off":false}',
        )

    def test_none_value_renders_as_json_null(self):
        """A ``None`` *value* inside the body becomes JSON ``null``.

        Distinct from the top-level ``None`` case (which means "no
        body at all" and returns empty bytes).
        """
        self.assertEqual(
            serialize_body_to_bytes({"v": None}),
            b'{"v":null}',
        )

    def test_nested_dict_serializes_recursively(self):
        """Nested dicts are serialised recursively with the same compact rules."""
        body = {"id": "x", "meta": {"region": "us-east", "count": 3}}
        self.assertEqual(
            serialize_body_to_bytes(body),
            b'{"id":"x","meta":{"region":"us-east","count":3}}',
        )

    def test_list_input_serializes_as_json_array(self):
        """A bare ``list`` is a legal JSON document and serialises to a JSON array."""
        self.assertEqual(
            serialize_body_to_bytes([1, 2, 3]),
            b"[1,2,3]",
        )

    def test_tuple_input_serializes_as_json_array(self):
        """A ``tuple`` takes the same path as a list — ``json.dumps`` treats them identically."""
        self.assertEqual(
            serialize_body_to_bytes(("a", "b")),
            b'["a","b"]',
        )

    def test_non_ascii_string_value_uses_unicode_escape(self):
        """Check escaped Unicode bytes for the supplied string with ensure_ascii enabled."""
        self.assertEqual(
            serialize_body_to_bytes({"name": "café"}),
            b'{"name":"caf\\u00e9"}',
        )


class TestUnknownTypeRaisesLoudly(unittest.TestCase):
    """Unsupported input types must raise ``TypeError`` immediately.

    The legacy serializer silently returned ``None`` for unknown
    types, which produced a quiet "request had no body" bug
    downstream. The new helper raises at the boundary so the caller
    learns about the mistake during development instead of debugging
    a confusing 400 from the service.
    """

    def test_object_input_raises_type_error(self):
        """A custom class instance is not a body shape we accept; the error names the type."""
        class Custom:
            """Represent an unsupported request-body type."""

            pass

        with self.assertRaises(TypeError) as ctx:
            serialize_body_to_bytes(Custom())
        self.assertIn("Custom", str(ctx.exception))

    def test_int_input_raises_type_error(self):
        """A bare integer is not a valid Cosmos document — caught here, not by the service."""
        with self.assertRaises(TypeError):
            serialize_body_to_bytes(42)

    def test_set_input_raises_type_error(self):
        """A ``set`` has no JSON representation; we raise with a clearer message than ``json.dumps``."""
        with self.assertRaises(TypeError):
            serialize_body_to_bytes({"a", "b"})


class TestParityWithLegacySerializer(unittest.TestCase):
    """Compare selected inputs with an inline legacy-style serializer.

    This reference is not a call into the legacy transport and does not
    establish byte parity for every possible SDK input.
    """

    @staticmethod
    def _legacy_serialize_to_bytes(data):
        """Inline reproduction of the legacy dict/list branch + transport encode step."""
        if isinstance(data, (dict, list, tuple)):
            return json.dumps(data, separators=(",", ":")).encode("utf-8")
        if isinstance(data, str):
            return data.encode("utf-8")
        if data is None:
            return b""
        raise TypeError("test-only helper does not handle this input")

    def test_parity_for_full_input_table(self):
        """Helper bytes equal the inline reference for each input in this table."""
        for value in [
            None,
            "",
            '{"id":"x"}',
            {"id": "order-42", "total": 99.5},
            {"z": 1, "a": 2, "m": 3},
            {"flag": True, "off": False, "v": None},
            {"meta": {"region": "us-east", "count": 3}},
            [1, 2, 3],
            ("a", "b"),
            {"name": "café"},
        ]:
            with self.subTest(value=value):
                self.assertEqual(
                    serialize_body_to_bytes(value),
                    self._legacy_serialize_to_bytes(value),
                )


if __name__ == "__main__":
    unittest.main()

