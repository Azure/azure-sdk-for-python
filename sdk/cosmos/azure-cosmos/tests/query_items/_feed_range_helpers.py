# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Self-contained feed-range builders copied from tests/test_config.py."""

from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range


def create_range(range_min: str, range_max: str, is_min_inclusive: bool = True, is_max_inclusive: bool = False):
    if range_max == range_min:
        range_max += "FF"
    return Range(
        range_min=range_min,
        range_max=range_max,
        isMinInclusive=is_min_inclusive,
        isMaxInclusive=is_max_inclusive,
    )


def create_feed_range_in_dict(feed_range):
    return FeedRangeInternalEpk(feed_range).to_dict()
