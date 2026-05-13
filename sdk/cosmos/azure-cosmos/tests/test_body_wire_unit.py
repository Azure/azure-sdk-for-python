# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_body_wire.py`` — no network, no Cosmos emulator.

These tests pin the request-body serializer to byte-exact output for
every input shape the SDK accepts. Any drift here breaks downstream
systems that hash or string-compare Cosmos documents (audit logs,
dedup checks, content-addressed storage). The function under test is
pure, so the tests run in milliseconds.
"""
import json
import unittest

from azure.cosmos._helpers._body_wire import serialize_body_to_bytes


class TestEmptyAndPrimitiveBodies(unittest.TestCase):
    """Inputs that don't go through ``json.dumps`` — passthrough cases."""

    def test_none_returns_empty_bytes(self):
        # No-body operations (e.g. delete) pass None. Empty bytes is
        # the right "no payload" signal for the backend layer.
        self.assertEqual(serialize_body_to_bytes(None), b"")

    def test_bytes_input_passes_through_unchanged(self):
        # A caller that already encoded the body (e.g. a future rust
        # code path) hands us bytes; we must not re-encode it.
        payload = b'{"id":"x","total":1}'
        self.assertEqual(serialize_body_to_bytes(payload), payload)
        # Identity-of-content, not necessarily identity-of-object.
        self.assertIsInstance(serialize_body_to_bytes(payload), bytes)

    def test_bytearray_input_returns_bytes(self):
        # bytearray is mutable; the helper returns an immutable bytes
        # copy so downstream code can rely on body_bytes not changing.
        ba = bytearray(b'{"k":1}')
        result = serialize_body_to_bytes(ba)
        self.assertEqual(result, b'{"k":1}')
        self.assertIsInstance(result, bytes)
        # Mutating the original bytearray must not change the result.
        ba[0] = ord("X")
        self.assertEqual(result, b'{"k":1}')

    def test_str_input_is_utf8_encoded(self):
        # Strings are assumed to already be valid JSON text; the
        # helper just UTF-8 encodes them.
        self.assertEqual(serialize_body_to_bytes('{"id":"x"}'), b'{"id":"x"}')


class TestDictListSerialization(unittest.TestCase):
    """The common case: dict / list / tuple goes through ``json.dumps``."""

    def test_simple_dict_compact_no_spaces(self):
        # The whole reason this helper exists: compact JSON with no
        # incidental whitespace, so the bytes match what the existing
        # pipeline produces.
        self.assertEqual(
            serialize_body_to_bytes({"id": "order-42", "total": 99.5}),
            b'{"id":"order-42","total":99.5}',
        )

    def test_dict_key_insertion_order_preserved(self):
        # Python dicts preserve insertion order since 3.7. The Cosmos
        # service does not care about key order, but customer fixtures
        # often do (string compare). Lock the order.
        body = {"z": 1, "a": 2, "m": 3}
        self.assertEqual(
            serialize_body_to_bytes(body),
            b'{"z":1,"a":2,"m":3}',
        )

    def test_integer_stays_integer_not_float(self):
        # The Cosmos service distinguishes 123 from 123.0 in some
        # query contexts. Make sure json.dumps does not promote.
        self.assertEqual(
            serialize_body_to_bytes({"n": 123}),
            b'{"n":123}',
        )

    def test_float_with_simple_decimal_keeps_decimal(self):
        # 99.5 must stay 99.5; we explicitly do not want scientific
        # notation or rounding for the simple decimal case.
        self.assertEqual(
            serialize_body_to_bytes({"price": 99.5}),
            b'{"price":99.5}',
        )

    def test_booleans_render_lowercase(self):
        self.assertEqual(
            serialize_body_to_bytes({"flag": True, "off": False}),
            b'{"flag":true,"off":false}',
        )

    def test_none_value_renders_as_json_null(self):
        # A literal None value inside the body becomes JSON null. This
        # is distinct from the top-level None case (no body at all).
        self.assertEqual(
            serialize_body_to_bytes({"v": None}),
            b'{"v":null}',
        )

    def test_nested_dict_serializes_recursively(self):
        body = {"id": "x", "meta": {"region": "us-east", "count": 3}}
        self.assertEqual(
            serialize_body_to_bytes(body),
            b'{"id":"x","meta":{"region":"us-east","count":3}}',
        )

    def test_list_input_serializes_as_json_array(self):
        # A bare list is a legal JSON document.
        self.assertEqual(
            serialize_body_to_bytes([1, 2, 3]),
            b"[1,2,3]",
        )

    def test_tuple_input_serializes_as_json_array(self):
        # Tuples take the same path as lists; json.dumps treats them
        # identically.
        self.assertEqual(
            serialize_body_to_bytes(("a", "b")),
            b'["a","b"]',
        )

    def test_non_ascii_string_value_uses_unicode_escape(self):
        # Default ensure_ascii=True matches what every existing Cosmos
        # parity test fixture in the repo expects.
        self.assertEqual(
            serialize_body_to_bytes({"name": "café"}),
            b'{"name":"caf\\u00e9"}',
        )


class TestUnknownTypeRaisesLoudly(unittest.TestCase):
    """The legacy serializer silently dropped unknown types; we don't."""

    def test_object_input_raises_type_error(self):
        # A custom class instance is not a body shape we accept. The
        # legacy path returned None (and the request silently went out
        # with no body); we raise so the caller learns immediately.
        class Custom:
            pass

        with self.assertRaises(TypeError) as ctx:
            serialize_body_to_bytes(Custom())
        self.assertIn("Custom", str(ctx.exception))

    def test_int_input_raises_type_error(self):
        # A bare integer is not a valid Cosmos document. Catching it
        # here prevents a confusing 400 from the service later.
        with self.assertRaises(TypeError):
            serialize_body_to_bytes(42)

    def test_set_input_raises_type_error(self):
        # set() has no JSON representation. json.dumps would raise
        # TypeError further down; we raise earlier with a clearer
        # message that names the helper.
        with self.assertRaises(TypeError):
            serialize_body_to_bytes({"a", "b"})


class TestParityWithLegacySerializer(unittest.TestCase):
    """Cross-check against ``_synchronized_request._data_to_unicode_string``.

    Until the helper-extraction refactor lands, both serializers run side
    by side. The wire bytes the legacy path produces (the str return
    encoded by the transport as UTF-8) must equal the bytes this
    helper returns. If they ever drift, the byte-for-byte parity
    guarantee between the core-python and rust backends breaks. The
    legacy logic is reproduced here locally so the test is self-
    contained even if the legacy code moves.
    """

    @staticmethod
    def _legacy_serialize_to_bytes(data):
        """Reproduces the dict/list branch of ``_data_to_unicode_string``.

        The legacy function returns a str for dict/list/tuple inputs;
        the transport then UTF-8 encodes it. We collapse those two
        steps here so the comparison is byte-vs-byte.
        """
        if isinstance(data, (dict, list, tuple)):
            return json.dumps(data, separators=(",", ":")).encode("utf-8")
        if isinstance(data, str):
            return data.encode("utf-8")
        if data is None:
            return b""
        raise TypeError("test-only helper does not handle this input")

    def test_parity_for_full_input_table(self):
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

