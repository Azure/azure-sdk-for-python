# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for how "no partition key value" sentinels are hashed.

``{}`` is the legacy spelling of "this item has no value for the partition key path".
It is serialized on the wire as ``[{}]``, exactly like ``NonePartitionKeyValue``, so both
must produce the ``Undefined`` effective partition key.

Regression coverage for https://github.com/Azure/azure-sdk-for-python/issues/48420 where
``query_items(query, partition_key={})`` raised
``TypeError: Unexpected type for PK component: <class 'dict'>`` on Hash V1 containers, and
silently resolved to the ``Null`` effective partition key on Hash V2 containers.

``_Empty`` is the equivalent sentinel for system key (migrated) containers. It is serialized
as ``[]`` rather than ``[{}]`` -- an empty list of partition key components rather than a single
undefined one -- so it resolves to the minimum effective partition key instead.
"""

import unittest

import pytest

from azure.cosmos.partition_key import (
    NonePartitionKeyValue,
    PartitionKey,
    _Empty,
    _Undefined,
)

UNDEFINED_EQUIVALENTS = ({}, NonePartitionKeyValue)


@pytest.mark.cosmosEmulator
@pytest.mark.unittest
class TestUndefinedPartitionKeyHashingUnitTest(unittest.TestCase):

    def test_undefined_equivalents_match_undefined_epk(self):
        for version in (1, 2):
            expected = PartitionKey(
                path="/pk", kind="Hash", version=version
            )._get_epk_range_for_partition_key(_Undefined())
            for pk_value in UNDEFINED_EQUIVALENTS:
                with self.subTest(version=version, pk_value=pk_value):
                    actual = PartitionKey(
                        path="/pk", kind="Hash", version=version
                    )._get_epk_range_for_partition_key(pk_value)
                    self.assertEqual(actual.min, expected.min)
                    self.assertEqual(actual.max, expected.max)

    def test_undefined_equivalents_differ_from_null_epk(self):
        for version in (1, 2):
            null_epk = PartitionKey(
                path="/pk", kind="Hash", version=version
            )._get_epk_range_for_partition_key(None)
            for pk_value in UNDEFINED_EQUIVALENTS:
                with self.subTest(version=version, pk_value=pk_value):
                    actual = PartitionKey(
                        path="/pk", kind="Hash", version=version
                    )._get_epk_range_for_partition_key(pk_value)
                    self.assertNotEqual(
                        actual.min, null_epk.min,
                        "An absent partition key value must not hash to the Null EPK.",
                    )

    def test_undefined_equivalents_match_undefined_epk_for_multi_hash(self):
        pk_definition = PartitionKey(path=["/a", "/b"], kind="MultiHash", version=2)
        expected = pk_definition._get_epk_range_for_partition_key([_Undefined(), "z"])
        for pk_value in UNDEFINED_EQUIVALENTS:
            with self.subTest(pk_value=pk_value):
                actual = pk_definition._get_epk_range_for_partition_key([pk_value, "z"])
                self.assertEqual(actual.min, expected.min)
                self.assertEqual(actual.max, expected.max)

    def test_defined_values_are_unaffected(self):
        """Normalization must not alter any value that does have a partition key value."""
        for version in (1, 2):
            pk_definition = PartitionKey(path="/pk", kind="Hash", version=version)
            for pk_value in (None, True, False, 0, 1, -1, 3.5, "", "a", "x" * 150):
                with self.subTest(version=version, pk_value=pk_value):
                    epk = pk_definition._get_epk_range_for_partition_key(pk_value)
                    self.assertIsNotNone(epk.min)

    def test_empty_resolves_to_minimum_epk(self):
        """``_Empty`` is an empty component list, so it maps to the minimum effective partition key."""
        for pk_definition in (
            PartitionKey(path="/pk", kind="Hash", version=1),
            PartitionKey(path="/pk", kind="Hash", version=2),
            PartitionKey(path=["/a", "/b"], kind="MultiHash", version=2),
        ):
            with self.subTest(kind=pk_definition.kind, version=pk_definition.version):
                epk = pk_definition._get_epk_range_for_partition_key(_Empty())
                self.assertEqual(epk.min, "")
                self.assertEqual(epk.max, "00")
                self.assertTrue(epk.isMinInclusive)
                self.assertFalse(epk.isMaxInclusive)

    def test_empty_range_survives_normalization(self):
        """The range must stay non-empty once normalized, otherwise it matches no feed range.

        An inclusive point range at the minimum effective partition key normalizes to an empty
        range, which would silently resolve to no partitions at all.
        """
        for version in (1, 2):
            with self.subTest(version=version):
                epk = PartitionKey(
                    path="/pk", kind="Hash", version=version
                )._get_epk_range_for_partition_key(_Empty())
                normalized = epk.to_normalized_range()
                self.assertFalse(normalized.isEmpty())
                self.assertEqual(normalized, epk)

    def test_empty_differs_from_undefined(self):
        """``_Empty`` and ``_Undefined`` are distinct sentinels with distinct wire forms."""
        for version in (1, 2):
            with self.subTest(version=version):
                pk_definition = PartitionKey(path="/pk", kind="Hash", version=version)
                self.assertNotEqual(
                    pk_definition._get_epk_range_for_partition_key(_Empty()).min,
                    pk_definition._get_epk_range_for_partition_key(_Undefined()).min,
                )


if __name__ == "__main__":
    unittest.main()
