# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import logging

import pytest

import azure.cosmos._routing.routing_range as routing_range
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap, _build_routing_map_from_ranges


@pytest.mark.cosmosEmulator
class TestCollectionRoutingMap(unittest.TestCase):

    def test_advanced(self):
        partition_key_ranges = [{u'id': u'0', u'minInclusive': u'', u'maxExclusive': u'05C1C9CD673398'},
                                {u'id': u'1', u'minInclusive': u'05C1C9CD673398', u'maxExclusive': u'05C1D9CD673398'},
                                {u'id': u'2', u'minInclusive': u'05C1D9CD673398', u'maxExclusive': u'05C1E399CD6732'},
                                {u'id': u'3', u'minInclusive': u'05C1E399CD6732', u'maxExclusive': u'05C1E9CD673398'},
                                {u'id': u'4', u'minInclusive': u'05C1E9CD673398', u'maxExclusive': u'FF'}]
        partitionRangeWithInfo = [(r, True) for r in partition_key_ranges]

        pkRange = routing_range.Range("", "FF", True, False)
        collection_routing_map = CollectionRoutingMap.CompleteRoutingMap(partitionRangeWithInfo, 'sample collection id')
        overlapping_partition_key_ranges = collection_routing_map.get_overlapping_ranges(pkRange)

        self.assertEqual(len(overlapping_partition_key_ranges), len(partition_key_ranges))
        self.assertEqual(overlapping_partition_key_ranges, partition_key_ranges)

    def test_point_range_mapping(self):
        partition_key_ranges = [{u'id': u'0', u'minInclusive': u'', u'maxExclusive': u'1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'},
                                {u'id': u'1', u'minInclusive': u'1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF', u'maxExclusive': u'FF'}]
        partitionRangeWithInfo = [(r, True) for r in partition_key_ranges]
        expected_partition_key_range = routing_range.Range("", "1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", True, False)
        pk_range = routing_range.Range("1EC0C2CBE45DBC919CF2B65D399C2673", "1EC0C2CBE45DBC919CF2B65D399C2673", True, True)
        normalized_pk_range = pk_range.to_normalized_range()

        collection_routing_map = CollectionRoutingMap.CompleteRoutingMap(partitionRangeWithInfo, 'sample collection id')
        overlapping_partition_key_ranges = collection_routing_map.get_overlapping_ranges(normalized_pk_range)

        # a partition key feed range should only map to one physical partition
        self.assertEqual(1, len(overlapping_partition_key_ranges))
        self.assertEqual(expected_partition_key_range, routing_range.Range.PartitionKeyRangeToRange(overlapping_partition_key_ranges[0]))

    def test_collection_routing_map(self):
        Id = 'id'
        MinInclusive = 'minInclusive'
        MaxExclusive = 'maxExclusive'

        partitionKeyRanges = \
            [
                ({Id: "2",
                  MinInclusive: "0000000050",
                  MaxExclusive: "0000000070"},
                 2),
                ({Id: "0",
                  MinInclusive: "",
                  MaxExclusive: "0000000030"},
                 0),
                ({Id: "1",
                  MinInclusive: "0000000030",
                  MaxExclusive: "0000000050"},
                 1),
                ({Id: "3",
                  MinInclusive: "0000000070",
                  MaxExclusive: "FF"},
                 3)
            ]

        crm = CollectionRoutingMap.CompleteRoutingMap(partitionKeyRanges, "")

        self.assertEqual("0", crm._orderedPartitionKeyRanges[0][Id])
        self.assertEqual("1", crm._orderedPartitionKeyRanges[1][Id])
        self.assertEqual("2", crm._orderedPartitionKeyRanges[2][Id])
        self.assertEqual("3", crm._orderedPartitionKeyRanges[3][Id])

        self.assertEqual(0, crm._orderedPartitionInfo[0])
        self.assertEqual(1, crm._orderedPartitionInfo[1])
        self.assertEqual(2, crm._orderedPartitionInfo[2])
        self.assertEqual(3, crm._orderedPartitionInfo[3])

        self.assertEqual("0", crm.get_range_by_effective_partition_key("")[Id])
        self.assertEqual("0", crm.get_range_by_effective_partition_key("0000000000")[Id])
        self.assertEqual("1", crm.get_range_by_effective_partition_key("0000000030")[Id])
        self.assertEqual("1", crm.get_range_by_effective_partition_key("0000000031")[Id])
        self.assertEqual("3", crm.get_range_by_effective_partition_key("0000000071")[Id])

        self.assertEqual("0", crm.get_range_by_partition_key_range_id("0")[Id])
        self.assertEqual("1", crm.get_range_by_partition_key_range_id("1")[Id])

        fullRangeMinToMaxRange = routing_range.Range(CollectionRoutingMap.MinimumInclusiveEffectivePartitionKey,
                                                     CollectionRoutingMap.MaximumExclusiveEffectivePartitionKey, True,
                                                     False)
        overlappingRanges = crm.get_overlapping_ranges([fullRangeMinToMaxRange])
        self.assertEqual(4, len(overlappingRanges))

        onlyPartitionRanges = [item[0] for item in partitionKeyRanges]

        def getKey(r):
            return r['id']

        onlyPartitionRanges.sort(key=getKey)
        self.assertEqual(overlappingRanges, onlyPartitionRanges)

        noPoint = routing_range.Range(CollectionRoutingMap.MinimumInclusiveEffectivePartitionKey,
                                      CollectionRoutingMap.MinimumInclusiveEffectivePartitionKey, False, False)
        self.assertEqual(0, len(crm.get_overlapping_ranges([noPoint])))

        onePoint = routing_range.Range("0000000040", "0000000040", True, True)
        overlappingPartitionKeyRanges = crm.get_overlapping_ranges([onePoint])
        self.assertEqual(1, len(overlappingPartitionKeyRanges))
        self.assertEqual("1", overlappingPartitionKeyRanges[0][Id])

        ranges = [
            routing_range.Range("0000000040", "0000000045", True, True),
            routing_range.Range("0000000045", "0000000046", True, True),
            routing_range.Range("0000000046", "0000000050", True, True)
        ]
        overlappingPartitionKeyRanges = crm.get_overlapping_ranges(ranges)

        self.assertEqual(2, len(overlappingPartitionKeyRanges))
        self.assertEqual("1", overlappingPartitionKeyRanges[0][Id])
        self.assertEqual("2", overlappingPartitionKeyRanges[1][Id])

    def test_invalid_routing_map(self):
        partitionKeyRanges = \
            [
                ({'id': "1", 'minInclusive': "0000000020", 'maxExclusive': "0000000030"}, 2),
                ({'id': "2", 'minInclusive': "0000000025", 'maxExclusive': "0000000035"}, 2),
            ]

        collectionUniqueId = ""

        def createRoutingMap():
            CollectionRoutingMap.CompleteRoutingMap(partitionKeyRanges, collectionUniqueId)

        self.assertRaises(ValueError, createRoutingMap)

    def test_incomplete_routing_map(self):
        crm = CollectionRoutingMap.CompleteRoutingMap(
            [
                ({'id': "2", 'minInclusive': "", 'maxExclusive': "0000000030"}, 2),
                ({'id': "3", 'minInclusive': "0000000031", 'maxExclusive': "FF"}, 2),
            ]
            , "")
        self.assertIsNone(crm)

        crm = CollectionRoutingMap.CompleteRoutingMap(
            [
                ({'id': "2", 'minInclusive': "", 'maxExclusive': "0000000030"}, 2),
                ({'id': "2", 'minInclusive': "0000000030", 'maxExclusive': "FF"}, 2),
            ]
            , "")

        self.assertIsNotNone(crm)

    def test_try_combine_valid_split(self):
        """try_combine correctly merges child ranges from a split into the existing map."""
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '80'}, True),
            ({'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}, True)
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-1"')
        self.assertIsNotNone(crm)

        # Simulate split: range '0' splits into '2' and '3'
        new_ranges = [
            ({'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']}, True),
            ({'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['0']}, True)
        ]
        result = crm.try_combine(new_ranges, '"etag-2"')

        self.assertIsNotNone(result, "try_combine should succeed for a valid split")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 3)
        self.assertEqual(ranges[0]['id'], '2')
        self.assertEqual(ranges[1]['id'], '3')
        self.assertEqual(ranges[2]['id'], '1')
        self.assertEqual(result.change_feed_etag, '"etag-2"')

    def test_try_combine_incomplete_range_returns_none(self):
        """try_combine returns None when merged ranges have a gap."""
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}, True)
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-1"')
        self.assertIsNotNone(crm)

        # Children leave a gap: 40-60 is missing
        gapped_ranges = [
            ({'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']}, True),
            ({'id': '3', 'minInclusive': '60', 'maxExclusive': 'FF', 'parents': ['0']}, True)
        ]
        result = crm.try_combine(gapped_ranges, '"etag-2"')
        self.assertIsNone(result, "try_combine should return None for incomplete range coverage")

    def test_try_combine_preserves_stable_partitions(self):
        """try_combine keeps unaffected partitions when only some split."""
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '40'}, 'info_0'),
            ({'id': '1', 'minInclusive': '40', 'maxExclusive': '80'}, 'info_1'),
            ({'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}, 'info_2')
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-1"')
        self.assertIsNotNone(crm)

        # Only range '1' splits into '3' and '4'; range '0' and '2' unchanged but '0' reappears in delta
        delta = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '40'}, 'info_0'),  # stable, metadata update
            ({'id': '3', 'minInclusive': '40', 'maxExclusive': '60', 'parents': ['1']}, 'info_1'),
            ({'id': '4', 'minInclusive': '60', 'maxExclusive': '80', 'parents': ['1']}, 'info_1')
        ]
        result = crm.try_combine(delta, '"etag-2"')

        self.assertIsNotNone(result, "try_combine should succeed for a partial split")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 4)
        ids = [r['id'] for r in ranges]
        self.assertEqual(ids, ['0', '3', '4', '2'])

        # Verify stable range '2' preserved its original range_info
        self.assertEqual(result._orderedPartitionInfo[3], 'info_2')

    def test_change_feed_etag_stored_and_accessible(self):
        """CompleteRoutingMap stores the change_feed_etag and makes it accessible."""
        ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}, True)
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(ranges, 'coll1', '"my-etag-123"')
        self.assertIsNotNone(crm)
        self.assertEqual(crm.change_feed_etag, '"my-etag-123"')

        # Without etag
        crm_no_etag = CollectionRoutingMap.CompleteRoutingMap(ranges, 'coll1')
        self.assertIsNotNone(crm_no_etag)
        self.assertIsNone(crm_no_etag.change_feed_etag)

    def test_try_combine_valid_merge(self):
        """try_combine correctly handles a merge: two adjacent ranges merge into one.

        Scenario: Range '1' originally split into '1A' and '1B'. The SDK's cache
        has '0', '1A', '1B', '2' (range '1' was evicted when the split was processed).
        Now '1A' and '1B' merge back into range '3'.

        The delta contains: range '3' with parents ['1', '1A', '1B'].
        - '1' is not in the cache (evicted grandparent) -> no-op on removal
        - '1A' and '1B' ARE in the cache -> removed
        - '3' is added
        Result: {0, 3, 2}
        """
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '40'}, 'info_0'),
            ({'id': '1A', 'minInclusive': '40', 'maxExclusive': '60'}, 'info_1A'),
            ({'id': '1B', 'minInclusive': '60', 'maxExclusive': '80'}, 'info_1B'),
            ({'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}, 'info_2')
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-B"')
        self.assertIsNotNone(crm)

        # Merge: '1A' and '1B' merge into '3', parents includes evicted grandparent '1'
        delta = [
            ({'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['1', '1A', '1B']}, 'info_1A')
        ]
        result = crm.try_combine(delta, '"etag-C"')

        self.assertIsNotNone(result, "try_combine should succeed for a valid merge")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 3)
        ids = [r['id'] for r in ranges]
        self.assertEqual(ids, ['0', '3', '2'])
        self.assertEqual(result.change_feed_etag, '"etag-C"')

        # Verify stable ranges preserved their range_info
        self.assertEqual(result._orderedPartitionInfo[0], 'info_0')
        self.assertEqual(result._orderedPartitionInfo[2], 'info_2')

    def test_try_combine_merge_evicted_grandparent_noop(self):
        """try_combine gracefully handles parents that are not in the cache (already evicted).

        When the parents list includes an ancestor that was already removed from the cache
        in a prior split, try_combine should simply skip removing it (no-op) without error.
        """
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '40'}, True),
            ({'id': '1A', 'minInclusive': '40', 'maxExclusive': '60'}, True),
            ({'id': '1B', 'minInclusive': '60', 'maxExclusive': '80'}, True),
            ({'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}, True)
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-1"')
        self.assertIsNotNone(crm)

        # '99' is a grandparent that was never in the cache
        delta = [
            ({'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['99', '1A', '1B']}, True)
        ]
        result = crm.try_combine(delta, '"etag-2"')

        self.assertIsNotNone(result, "try_combine should succeed even with evicted grandparent in parents")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0', '3', '2'])

    def test_try_combine_accumulates_gone_ranges_across_updates(self):
        """Gone range ids should persist across combines, not just within one delta."""
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '80'}, True),
            ({'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}, True),
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-1"')

        first_delta = [
            ({'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']}, True),
            ({'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['0']}, True),
        ]
        after_first = crm.try_combine(first_delta, '"etag-2"')

        self.assertIsNotNone(after_first)
        self.assertIn('0', after_first._goneRangeIds)

        second_delta = [
            ({'id': '4', 'minInclusive': '80', 'maxExclusive': 'C0', 'parents': ['1']}, True),
            ({'id': '5', 'minInclusive': 'C0', 'maxExclusive': 'FF', 'parents': ['1']}, True),
        ]
        after_second = after_first.try_combine(second_delta, '"etag-3"')

        self.assertIsNotNone(after_second)
        self.assertIn('0', after_second._goneRangeIds)
        self.assertIn('1', after_second._goneRangeIds)

    def test_try_combine_ignores_stale_previously_gone_range_in_later_delta(self):
        """A stale previously-gone range in a later delta should be removed by accumulated tombstones."""
        initial_ranges = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '80'}, True),
            ({'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}, True),
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(initial_ranges, 'coll1', '"etag-1"')

        split_left = [
            ({'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']}, True),
            ({'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['0']}, True),
        ]
        after_left_split = crm.try_combine(split_left, '"etag-2"')
        self.assertIsNotNone(after_left_split)

        # Later delta contains a stale copy of previously-gone range '0' plus a valid split of '1'.
        later_delta = [
            ({'id': '0', 'minInclusive': '', 'maxExclusive': '80'}, True),
            ({'id': '4', 'minInclusive': '80', 'maxExclusive': 'C0', 'parents': ['1']}, True),
            ({'id': '5', 'minInclusive': 'C0', 'maxExclusive': 'FF', 'parents': ['1']}, True),
        ]
        result = after_left_split.try_combine(later_delta, '"etag-3"')

        self.assertIsNotNone(result)
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['2', '3', '4', '5'])

    # =========================================================
    # Tests for _build_routing_map_from_ranges parent filtering
    # =========================================================

    def test_build_routing_map_filters_gone_parent_ranges(self):
        """_build_routing_map_from_ranges filters out parent (gone) ranges
        referenced in children's 'parents' lists and builds a complete map
        from only the child ranges."""
        _logger = logging.getLogger("test")
        # Parent '0' split into children '1' and '2'
        ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'},          # gone parent
            {'id': '1', 'minInclusive': '', 'maxExclusive': '80', 'parents': ['0']},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF', 'parents': ['0']},
        ]
        result = _build_routing_map_from_ranges(ranges, 'coll1', '"etag-1"', 'dbs/db/colls/coll1', _logger)

        self.assertIsNotNone(result, "Should build a valid routing map after filtering parent")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['1', '2'])
        self.assertNotIn('0', ids, "Gone parent '0' should be filtered out")
        self.assertEqual(result.change_feed_etag, '"etag-1"')

    def test_build_routing_map_filters_multiple_parent_levels(self):
        """_build_routing_map_from_ranges filters out all ancestors referenced
        as parents, even when multiple levels of splits are present in a single
        change feed response."""
        _logger = logging.getLogger("test")
        # Grandparent '0' split into '1' and '2', then '1' split into '3' and '4'
        # All appear in the same change feed response
        ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'},
            {'id': '1', 'minInclusive': '', 'maxExclusive': '80', 'parents': ['0']},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF', 'parents': ['0']},
            {'id': '3', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['1']},
            {'id': '4', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['1']},
        ]
        result = _build_routing_map_from_ranges(ranges, 'coll1', '"etag-2"', 'dbs/db/colls/coll1', _logger)

        self.assertIsNotNone(result, "Should build a valid routing map after multi-level filtering")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        # '0' is gone (parent of '1' and '2'), '1' is gone (parent of '3' and '4')
        self.assertEqual(ids, ['3', '4', '2'])

    def test_build_routing_map_no_parents_passes_through_all(self):
        """_build_routing_map_from_ranges passes through all ranges when none
        have parents (no splits occurred)."""
        _logger = logging.getLogger("test")
        ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'},
        ]
        result = _build_routing_map_from_ranges(ranges, 'coll1', '"etag-3"', 'dbs/db/colls/coll1', _logger)

        self.assertIsNotNone(result)
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0', '1'])

    def test_build_routing_map_returns_none_for_incomplete_ranges(self):
        """_build_routing_map_from_ranges returns None when the filtered ranges
        don't form a complete partition key space (gap exists)."""
        _logger = logging.getLogger("test")
        ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'},
            # Gap from '80' to 'FF' — incomplete
        ]
        result = _build_routing_map_from_ranges(ranges, 'coll1', '"etag-4"', 'dbs/db/colls/coll1', _logger)
        self.assertIsNone(result, "Should return None for incomplete range coverage")

    def test_build_routing_map_empty_parents_list_not_treated_as_gone(self):
        """_build_routing_map_from_ranges does NOT filter a range whose 'parents'
        key exists but is an empty list — only non-empty parents trigger filtering."""
        _logger = logging.getLogger("test")
        ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80', 'parents': []},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF', 'parents': []},
        ]
        result = _build_routing_map_from_ranges(ranges, 'coll1', '"etag-5"', 'dbs/db/colls/coll1', _logger)

        self.assertIsNotNone(result, "Empty parents list should not cause filtering")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0', '1'])

    def test_build_routing_map_stores_etag(self):
        """_build_routing_map_from_ranges stores the provided ETag on the
        resulting CollectionRoutingMap, and None etag is handled gracefully."""
        _logger = logging.getLogger("test")
        ranges = [{'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}]

        result_with_etag = _build_routing_map_from_ranges(ranges, 'coll1', '"etag-X"', 'link', _logger)
        self.assertEqual(result_with_etag.change_feed_etag, '"etag-X"')

        result_none_etag = _build_routing_map_from_ranges(ranges, 'coll1', None, 'link', _logger)
        self.assertIsNone(result_none_etag.change_feed_etag)


if __name__ == '__main__':
    unittest.main()
