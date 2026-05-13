# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_pk_wire.py`` — no network, no Cosmos emulator.

These tests pin the partition-key wire serializer to the table
documented in ``azure/cosmos/_helpers/_pk_wire.py``. They run in
milliseconds because the function under test is pure: takes a value,
returns a string. Any drift in the on-wire shape — single value,
hierarchical, ``_Undefined``, ``_Empty`` — flips a partition key and
makes a customer's items "disappear" into the wrong physical
partition. We catch that here at PR time.
"""
import json
import unittest

from azure.cosmos._helpers._pk_wire import serialize_partition_key_to_wire
from azure.cosmos.partition_key import (
    NonePartitionKeyValue,
    _Empty,
    _Undefined,
)


class TestSinglePartitionKeyValues(unittest.TestCase):
    """Single-value partition keys (one path defined on the container)."""

    def test_string_value_wraps_in_one_element_array(self):
        # The most common case: a string PK like a customer id.
        self.assertEqual(serialize_partition_key_to_wire("customerA"), '["customerA"]')

    def test_integer_value_stays_unquoted(self):
        # The Cosmos service distinguishes between the integer 123 and
        # the string "123" when hashing to a partition. Keep the integer
        # unquoted on the wire.
        self.assertEqual(serialize_partition_key_to_wire(123), "[123]")

    def test_float_value_stays_unquoted(self):
        # Same separation as integers — and we deliberately do not
        # round 99.5 to an integer.
        self.assertEqual(serialize_partition_key_to_wire(99.5), "[99.5]")

    def test_true_renders_as_lowercase_json_true(self):
        # Python's True is JSON's true (lowercase, unquoted).
        self.assertEqual(serialize_partition_key_to_wire(True), "[true]")

    def test_false_renders_as_lowercase_json_false(self):
        self.assertEqual(serialize_partition_key_to_wire(False), "[false]")

    def test_none_renders_as_json_null(self):
        # A literal None partition-key value is distinct from an
        # _Undefined sentinel and from a partitionless container.
        self.assertEqual(serialize_partition_key_to_wire(None), "[null]")


class TestSentinelPartitionKeyValues(unittest.TestCase):
    """Sentinel values that map to specific reserved on-wire shapes."""

    def test_undefined_renders_as_array_with_empty_object(self):
        # _Undefined is the SDK's marker for "the partition-key path
        # exists in the container definition but the document does not
        # contain a value at that path." The Cosmos service expects
        # [{}] for this case.
        self.assertEqual(serialize_partition_key_to_wire(_Undefined()), "[{}]")

    def test_empty_instance_renders_as_empty_array(self):
        # _Empty is the SDK's marker for a partitionless container
        # (legacy collection with no partition key). The Cosmos service
        # expects an empty array for this case.
        self.assertEqual(serialize_partition_key_to_wire(_Empty()), "[]")

    def test_none_partition_key_value_class_renders_as_empty_array(self):
        # NonePartitionKeyValue is the *class itself* (a sentinel type,
        # not an instance) used in some call sites. It must serialize
        # the same way as an _Empty instance.
        self.assertEqual(serialize_partition_key_to_wire(NonePartitionKeyValue), "[]")


class TestHierarchicalPartitionKeyValues(unittest.TestCase):
    """Hierarchical partition keys (containers with multiple PK paths)."""

    def test_two_level_hierarchical_key_renders_in_order(self):
        # Two paths defined on the container -> a two-element JSON array
        # in the same order the user supplied them.
        self.assertEqual(
            serialize_partition_key_to_wire(["t1", "r1"]),
            '["t1","r1"]',
        )

    def test_three_level_hierarchical_key_with_mixed_types(self):
        # Mixed string/int/bool inside a hierarchical PK is legal and
        # each component keeps its JSON type.
        self.assertEqual(
            serialize_partition_key_to_wire(["tenant1", 42, True]),
            '["tenant1",42,true]',
        )

    def test_hierarchical_key_with_empty_leaf_renders_null(self):
        # An _Empty (or _Undefined) sentinel sitting inside a
        # hierarchical PK list means "the document is missing a value
        # at this path." It serializes as JSON null at that position,
        # not as the [{}] / [] reserved sentinels.
        self.assertEqual(
            serialize_partition_key_to_wire(["t1", _Empty()]),
            '["t1",null]',
        )

    def test_hierarchical_key_with_undefined_leaf_renders_null(self):
        # _Undefined inside a hierarchical PK behaves the same as
        # _Empty inside one — renders as null at the missing position.
        self.assertEqual(
            serialize_partition_key_to_wire([_Undefined(), "r1"]),
            '[null,"r1"]',
        )

    def test_tuple_input_treated_the_same_as_list(self):
        # The hierarchical-PK code path checks for ``Sequence``, so a
        # tuple is also accepted. Output is identical to the list case.
        self.assertEqual(
            serialize_partition_key_to_wire(("t1", "r1")),
            '["t1","r1"]',
        )


class TestOutputAlwaysStringAndCompactJson(unittest.TestCase):
    """Properties the function must hold on every input.

    The Cosmos pipeline assigns the result directly to an HTTP header
    value, which must be a string. Any code path that returned a list
    or dict instead would break header serialization downstream.
    """

    def test_every_documented_input_returns_a_str(self):
        # Walks every row of the mapping table in the module docstring
        # and asserts the return type. Catches a regression where one
        # branch starts returning a Python list (which silently breaks
        # header serialization downstream).
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
                result = serialize_partition_key_to_wire(value)
                self.assertIsInstance(result, str)

    def test_compact_json_no_spaces_in_output(self):
        # Customer dashboards and tests sometimes string-compare the
        # outgoing PK header. Asserting the compact JSON form with no
        # incidental spaces locks the byte shape.
        self.assertNotIn(
            " ", serialize_partition_key_to_wire(["tenant1", "region1", 99])
        )


class TestParityWithExistingHeaderBuilder(unittest.TestCase):
    """Cross-check against the legacy in-place serializer in ``_base.GetHeaders``.

    Until Phase B5/B6 land and the legacy code path is removed, both
    serializers run side by side. If they ever drift, the byte-for-byte
    parity guarantee between the core-python and rust backends breaks
    silently. This test reproduces the legacy logic locally and asserts
    the two produce the same output for every row of the table.
    """

    @staticmethod
    def _legacy_serialize(pk_value):
        """Reproduces the relevant branch of ``_base.GetHeaders``.

        Kept here (rather than imported) so the test fails cleanly if
        either side moves. The legacy code lives in
        ``azure/cosmos/_base.py`` around the line that sets
        ``headers[http_constants.HttpHeaders.PartitionKey]``.
        """
        if isinstance(pk_value, _Undefined):
            # Legacy assigned a Python list literal here; the wire
            # value is the JSON encoding of that literal.
            return json.dumps([{}], separators=(",", ":"))
        if isinstance(pk_value, _Empty):
            return json.dumps([], separators=(",", ":"))
        from collections.abc import Sequence  # local import keeps namespace clean
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
        # Every input the partition-key wire-shape contract requires.
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
                    serialize_partition_key_to_wire(value),
                    self._legacy_serialize(value),
                )


if __name__ == "__main__":
    unittest.main()



