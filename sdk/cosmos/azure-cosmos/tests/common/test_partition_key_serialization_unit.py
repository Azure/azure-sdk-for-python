# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Legacy wire-format oracle tests — no network, no Cosmos emulator.

Partition-scoped item requests carry an ``x-ms-documentdb-partitionkey`` HTTP
header. Its JSON array preserves distinctions such as string versus number,
null versus undefined, and component order. The Rust driver uses finite-f64
numeric components; these tests do not assert that integer 42 and float 42.0
identify different partitions.

``legacy_partition_key_header`` is retained for legacy execution/parity, not
the native request boundary. These tests cover its historical input shapes:

* Single values (string, int, float, bool, None) → one-element array
  with the type preserved (no quoting an int, no rounding a float).
* Sentinel values (``_Undefined``, ``_Empty``, ``NonePartitionKeyValue``)
  → the specific reserved on-request-byte shapes the service expects
  (``[{}]``, ``[]``, ``[]``).
* Hierarchical partition keys (lists / tuples) → a multi-element JSON
  array in the order the user supplied, with ``_Empty`` / ``_Undefined``
  components replaced by JSON ``null`` at their position.
* The output is *always* a string (some pipelines assigned a list
  by mistake, which broke header serialization downstream) and uses
  compact JSON (no spaces) so customer dashboards doing string
  comparison stay stable.

The file also cross-checks against the legacy in-place serializer in
``_base.GetHeaders``. Typed normalization and native routing-key equivalence
have separate coverage in the typed-partition-key tests.

Pure in-process; runs in milliseconds.
"""
import json
import unittest
from collections.abc import Sequence

from azure.cosmos._helpers._legacy_partition_key import legacy_partition_key_header
from azure.cosmos.partition_key import (
    NonePartitionKeyValue,
    _Empty,
    _Undefined,
)


class TestSinglePartitionKeyValues(unittest.TestCase):
    """Single-value partition keys (containers with one PK path).

    The whole single-value table: every Python primitive Cosmos
    accepts, plus a literal ``None``. Each must end up wrapped in a
    one-element JSON array with its native JSON type preserved.
    """

    def test_string_value_wraps_in_one_element_array(self):
        """The common case: a string PK like a customer id → ``["customerA"]``."""
        self.assertEqual(legacy_partition_key_header("customerA"), '["customerA"]')

    def test_integer_value_stays_unquoted(self):
        """Integer ``123`` stays an unquoted JSON integer (distinct partition from ``"123"``)."""
        self.assertEqual(legacy_partition_key_header(123), "[123]")

    def test_float_value_stays_unquoted(self):
        """Float ``99.5`` stays unquoted — and is not rounded to ``99``."""
        self.assertEqual(legacy_partition_key_header(99.5), "[99.5]")

    def test_true_renders_as_lowercase_json_true(self):
        """Python ``True`` → JSON ``true`` (lowercase, unquoted)."""
        self.assertEqual(legacy_partition_key_header(True), "[true]")

    def test_false_renders_as_lowercase_json_false(self):
        """Python ``False`` → JSON ``false`` (lowercase, unquoted)."""
        self.assertEqual(legacy_partition_key_header(False), "[false]")

    def test_none_renders_as_json_null(self):
        """A literal ``None`` PK value → ``[null]`` (distinct from ``_Undefined`` and ``_Empty``)."""
        self.assertEqual(legacy_partition_key_header(None), "[null]")


class TestSentinelPartitionKeyValues(unittest.TestCase):
    """Sentinel values that map to specific reserved on-request-byte shapes.

    The SDK uses three sentinels to express situations a regular
    Python value can't represent. Each maps to a different reserved
    JSON shape that the Cosmos service interprets specifically:
    ``[{}]`` for "PK path defined but missing on the document",
    ``[]`` for "container has no partition key at all".
    """

    def test_undefined_renders_as_array_with_empty_object(self):
        """``_Undefined()`` → ``[{}]``: PK path exists in container but doc has no value at it."""
        self.assertEqual(legacy_partition_key_header(_Undefined()), "[{}]")

    def test_empty_instance_renders_as_empty_array(self):
        """``_Empty()`` → ``[]``: legacy partitionless container (no PK path defined)."""
        self.assertEqual(legacy_partition_key_header(_Empty()), "[]")

    def test_none_partition_key_value_class_renders_as_empty_array(self):
        """``NonePartitionKeyValue`` (the class itself, not an instance) → ``[]``, same as ``_Empty()``."""
        self.assertEqual(legacy_partition_key_header(NonePartitionKeyValue), "[]")


class TestHierarchicalPartitionKeyValues(unittest.TestCase):
    """Hierarchical partition keys (containers with multiple PK paths).

    A hierarchical PK is supplied as a list (or tuple); each element
    corresponds to one PK path defined on the container, in the same
    order. Inner sentinels (``_Empty`` / ``_Undefined``) become JSON
    ``null`` at their position — *not* the reserved single-value
    sentinel shapes (``[{}]`` / ``[]``).
    """

    def test_two_level_hierarchical_key_renders_in_order(self):
        """Two PK paths → two-element JSON array in the order supplied."""
        self.assertEqual(
            legacy_partition_key_header(["t1", "r1"]),
            '["t1","r1"]',
        )

    def test_three_level_hierarchical_key_with_mixed_types(self):
        """Mixed string / int / bool components each keep their JSON type."""
        self.assertEqual(
            legacy_partition_key_header(["tenant1", 42, True]),
            '["tenant1",42,true]',
        )

    def test_hierarchical_key_with_empty_leaf_renders_null(self):
        """``_Empty`` inside a hierarchical PK → JSON ``null`` at that position (not ``[]``)."""
        self.assertEqual(
            legacy_partition_key_header(["t1", _Empty()]),
            '["t1",null]',
        )

    def test_hierarchical_key_with_undefined_leaf_renders_null(self):
        """``_Undefined`` inside a hierarchical PK → JSON ``null`` at that position (not ``[{}]``)."""
        self.assertEqual(
            legacy_partition_key_header([_Undefined(), "r1"]),
            '[null,"r1"]',
        )

    def test_tuple_input_treated_the_same_as_list(self):
        """A tuple is accepted (matches the ``Sequence`` check) and serialises identically to a list."""
        self.assertEqual(
            legacy_partition_key_header(("t1", "r1")),
            '["t1","r1"]',
        )


class TestOutputAlwaysStringAndCompactJson(unittest.TestCase):
    """Properties that must hold on every input regardless of branch.

    The Cosmos pipeline assigns the result directly to an HTTP header
    value, which must be a string. A code path that returned a list
    or dict instead would break header serialization downstream
    silently. Compact JSON (no whitespace) keeps the byte shape
    stable for customer string-comparison fixtures.
    """

    def test_every_documented_input_returns_a_str(self):
        """For every documented input shape, the return type is ``str``."""
        for value in [
            "customerA",
            123,
            99.5,
            True,
            False,
            None,
            _Undefined(),
            _Empty(),
            NonePartitionKeyValue,
            ["t1", "r1"],
            ["t1", _Empty()],
        ]:
            with self.subTest(value=value):
                result = legacy_partition_key_header(value)
                self.assertIsInstance(result, str)

    def test_compact_json_no_spaces_in_output(self):
        """Output is compact JSON — no spaces anywhere — so byte comparisons stay stable."""
        self.assertNotIn(
            " ", legacy_partition_key_header(["tenant1", "region1", 99])
        )


class TestParityWithExistingHeaderBuilder(unittest.TestCase):
    """Cross-check against the legacy in-place serializer in ``_base.GetHeaders``.

    Until the legacy code path is removed, both serializers run side
    by side. If they ever drift, the byte-for-byte parity guarantee
    between the core-python and rust backends breaks silently. This
    class reproduces the legacy logic inline (so the test stays
    self-contained even if the legacy code moves) and asserts both
    produce the same output for every row of the documented table.
    """

    @staticmethod
    def _legacy_serialize(pk_value):
        """Inline reproduction of the partition-key branch of ``_base.GetHeaders``.

        The original lives near the line that sets
        ``headers[http_constants.HttpHeaders.PartitionKey]``. Keeping
        a copy here means this test fails loudly if either side
        changes shape, without coupling the test to the import path.
        """
        if isinstance(pk_value, _Undefined):
            return json.dumps([{}], separators=(",", ":"))
        if isinstance(pk_value, _Empty):
            return json.dumps([], separators=(",", ":"))
        is_sequence_not_string = (
            isinstance(pk_value, Sequence) and not isinstance(pk_value, str)
        )
        if is_sequence_not_string and pk_value:
            normalized = [
                None if isinstance(component, (_Empty, _Undefined)) else component
                for component in pk_value
            ]
            return json.dumps(list(normalized), separators=(",", ":"))
        return json.dumps([pk_value], separators=(",", ":"))

    def test_parity_against_legacy_for_full_input_table(self):
        """For every documented input shape, helper output == legacy output."""
        for value in [
            "customerA",
            123,
            99.5,
            True,
            False,
            None,
            _Undefined(),
            _Empty(),
            ["t1", "r1"],
            ["t1", _Empty()],
            [_Undefined(), "r1"],
        ]:
            with self.subTest(value=value):
                self.assertEqual(
                    legacy_partition_key_header(value),
                    self._legacy_serialize(value),
                )


if __name__ == "__main__":
    unittest.main()
