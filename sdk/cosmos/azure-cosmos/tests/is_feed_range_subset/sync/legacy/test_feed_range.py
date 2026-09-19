# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``is_feed_range_subset`` tests against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in a class fixture and deletes
them afterward. The class name and method names match the source at
``tests/test_feed_range.py`` so test IDs differ only by path.

The parity suite only proves the two backends agree with each other; if both
drifted the same way they would still pass while the answer is wrong. These tests
pin the subset answer for known feed-range pairs to hard-coded expected values, so
an absolute regression is caught even when the backends match.

Run with::

    pytest --noconftest tests/is_feed_range_subset/sync/legacy/test_feed_range.py -v
"""
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Copied verbatim from tests/test_feed_range.py (test_subset_ranges):
# each row is (parent_range, child_range, expected_is_subset).
test_subset_ranges = [(Range("", "FF", True, False),
                       Range("3F", "7F", True, False),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("", "FF", True, False),
                       False),
                      (Range("3F", "7F", True, False),
                       Range("", "5F", True, False),
                       False),
                      (Range("3F", "7F", True, True),
                       Range("3F", "7F", True, True),
                       True),
                      (Range("3F", "7F", False, True),
                       Range("3F", "7F", True, True),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("3F", "7F", True, True),
                       False),
                      (Range("3F", "7F", True, False),
                       Range("", "2F", True, False),
                       False),
                      (Range("3F", "3F", True, True),
                       Range("3F", "3F", True, True),
                       True),
                      (Range("3F", "3F", True, True),
                       Range("4F", "4F", True, True),
                       False)
                      ]


@pytest.fixture(scope="class")
def rust_container():
    # Fresh Rust-backed database + container, deleted afterward. Every method in
    # this file runs against this one container with the client pinned to the
    # Rust backend, which is what makes this the "rust" column of the parity audit.
    client = CosmosClient(HOST, KEY, _backend="rust")
    db_id = "legacy_is_feed_range_subset_sync_" + uuid.uuid4().hex[:8]
    container_id = "c_" + uuid.uuid4().hex[:8]
    database = client.create_database(db_id)
    container = database.create_container(
        id=container_id,
        partition_key=PartitionKey(path="/id"),
    )
    yield container
    try:
        client.delete_database(db_id)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.cosmosEmulator
class TestFeedRange:

    @pytest.mark.parametrize("parent_feed_range, child_feed_range, is_subset", test_subset_ranges)
    def test_feed_range_is_subset(self, rust_container, parent_feed_range, child_feed_range, is_subset):
        """A table of parent and child range pairs with the answer pinned for each.

        The cases cover full containment, the same pair the other way round,
        partial overlap, and two identical ranges with inclusive bounds.

        Both the true and false answers are pinned. Half the value is in the
        false rows: an implementation that leaned towards saying yes would
        still pass every containment case while handing back ranges a caller
        must not treat as covered.

        Inclusive and exclusive bounds are varied deliberately, since that is
        where an off-by-one at the boundary shows up.
        """
        # Source: tests/test_feed_range.py::TestFeedRange.test_feed_range_is_subset
        epk_parent_feed_range = FeedRangeInternalEpk(parent_feed_range).to_dict()
        epk_child_feed_range = FeedRangeInternalEpk(child_feed_range).to_dict()
        assert rust_container.is_feed_range_subset(epk_parent_feed_range, epk_child_feed_range) == is_subset

    def test_feed_range_is_subset_from_pk(self, rust_container):
        """A range built from a partition key sits inside the full range.

        The full range covers everything from empty to ``FF``, so any single
        key must fall within it.

        Kept here for the comparison itself: unlike the table above, the child
        range is produced at runtime rather than written out by hand, so this
        also confirms a freshly built range is in a shape the comparison
        understands.
        """
        # Source: tests/test_feed_range.py::TestFeedRange.test_feed_range_is_subset_from_pk
        epk_parent_feed_range = FeedRangeInternalEpk(Range("", "FF", True, False)).to_dict()
        epk_child_feed_range = rust_container.feed_range_from_partition_key("1")
        assert rust_container.is_feed_range_subset(epk_parent_feed_range, epk_child_feed_range)
