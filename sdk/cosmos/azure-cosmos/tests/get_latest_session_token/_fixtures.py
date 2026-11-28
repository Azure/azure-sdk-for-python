# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retained token observations and write helpers, independent of legacy tests."""

import random
import uuid

from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos.http_constants import HttpHeaders


def create_split_ranges():
    # Source: tests/test_session_token_helpers.py::create_split_ranges
    return [        # split with two children
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "1:1#55#3=52,2:1#54#3=52"),
                    # same range different partition key range ids
                   ([(("AA", "DD"), "1:1#51#3=52"), (("AA", "DD"),"0:1#55#3=52")],
                    ("AA", "DD"), "0:1#55#3=52"),
                    # split with one child
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#51#3=52,1:1#55#3=52"),
                    # Highest GLSN, which is 55 in this         # cspell:disable-line
                    # ex. "1:1#55#3=52", is the one that will be returned because
                    # it is higher than all of the other feed range contained in the same
                    # range
                   ([(("AA", "DD"), "0:1#42#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "1:1#55#3=52"),
                    # Highest GLSN, which is 60 in this            # cspell:disable-line
                    # ex. "1:1#60#3=52", is the one that will be returned because
                    # it is higher than all of the other feed range contained in the same
                    # range with some of them overlapping with each other
                   ([(("AA", "DD"), "0:1#60#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#60#3=52"),
                    # AA-DD can be created from the other ranges
                    # but the GLSN's are not all larger than the one  # cspell:disable-line
                    # in the AA-DD range so we just compound as cannot make
                    # conclusions in this case
                   ([(("AA", "DD"), "0:1#60#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#66#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#60#3=52,1:1#66#3=52"),
                    # merge with one child
                   ([(("AA", "DD"), "3:1#55#3=52"), (("AA", "BB"),"1:1#51#3=52")],
                    ("AA", "DD"), "3:1#55#3=52"),
                    # merge with two children
                   ([(("AA", "DD"), "3:1#55#3=52"), (("AA", "BB"),"1:1#51#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "3:1#55#3=52"),
                    # compound session token
                   ([(("AA", "DD"), "2:1#54#3=52,1:1#55#3=52"), (("AA", "BB"),"0:1#51#3=52")],
                    ("AA", "BB"), "2:1#54#3=52,1:1#55#3=52,0:1#51#3=52"),
                    # several compound session token with one range
                   ([(("AA", "DD"), "2:1#57#3=52,1:1#57#3=52"), (("AA", "DD"),"2:1#56#3=52,1:1#58#3=52")],
                    ("AA", "DD"), "2:1#57#3=52,1:1#58#3=52"),
                    # overlapping ranges
                   ([(("AA", "CC"), "0:1#54#3=52"), (("BB", "FF"),"2:1#51#3=52")],
                    ("AA", "EE"), "0:1#54#3=52,2:1#51#3=52"),
                    # different version numbers
                   ([(("AA", "BB"), "0:1#54#3=52"), (("AA", "BB"),"0:2#57#3=53")],
                    ("AA", "BB"), "0:2#57#3=53"),
                    # mixed scenarios
                   ([(("AA", "DD"), "3:1#60#3=53"), (("AA", "BB"), "1:1#54#3=52"), (("AA", "BB"), "1:1#52#3=53"),
                     (("BB", "CC"),"1:1#53#3=52"), (("BB", "CC"),"6:1#70#3=55,4:1#90#3=52"),
                     (("CC", "DD"),"1:1#55#3=52")], ("AA", "DD"), "3:1#60#3=53,6:1#70#3=55,4:1#90#3=52")
                  ]


def create_item(hpk):
    # Source: tests/_split_test_utils.py::create_item
    if hpk:
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'state': 'CA',
            'city': 'LA' + str(random.randint(1, 10)),
            'zipcode': '90001'
        }
    else:
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
    return item


def create_items_logical_pk(container, target_pk_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
    # Source: tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios.create_items_logical_pk
    target_session_token = ""
    for i in range(100):
        item = create_item(hpk)
        response = container.create_item(item, session_token=previous_session_token)
        session_token = response.get_response_headers()[HttpHeaders.SessionToken]
        pk = item['pk'] if not hpk else [item['state'], item['city'], item['zipcode']]
        pk_range = container.feed_range_from_partition_key(pk)
        pk_feed_range_epk = FeedRangeInternalEpk.from_json(pk_range)
        target_feed_range_epk = FeedRangeInternalEpk.from_json(target_pk_range)
        if (pk_feed_range_epk.get_normalized_range() ==
                target_feed_range_epk.get_normalized_range()):
            target_session_token = session_token
        previous_session_token = session_token
        feed_ranges_and_session_tokens.append((pk_range,
                                           session_token))
    return target_session_token, previous_session_token


def create_items_physical_pk(container, pk_feed_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
    # Source: tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios.create_items_physical_pk
    target_session_token = ""
    container_feed_ranges = list(container.read_feed_ranges())
    target_feed_range = None
    for feed_range in container_feed_ranges:
        if container.is_feed_range_subset(feed_range, pk_feed_range):
            target_feed_range = feed_range
            break

    for i in range(100):
        item = create_item(hpk)
        response = container.create_item(item, session_token=previous_session_token)
        session_token = response.get_response_headers()[HttpHeaders.SessionToken]
        if hpk:
            pk = [item['state'], item['city'], item['zipcode']]
            curr_feed_range = container.feed_range_from_partition_key(pk)
        else:
            curr_feed_range = container.feed_range_from_partition_key(item['pk'])
        if container.is_feed_range_subset(target_feed_range, curr_feed_range):
            target_session_token = session_token
        previous_session_token = session_token
        feed_ranges_and_session_tokens.append((curr_feed_range, session_token))

    return target_session_token, target_feed_range, previous_session_token


async def create_items_logical_pk_async(container, target_pk_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
    # Source: tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.create_items_logical_pk_async
    target_session_token = ""
    for i in range(100):
        item = create_item(hpk)
        response = await container.create_item(item, session_token=previous_session_token)
        session_token = response.get_response_headers()[HttpHeaders.SessionToken]
        pk = item['pk'] if not hpk else [item['state'], item['city'], item['zipcode']]
        pk_feed_range = await container.feed_range_from_partition_key(pk)
        pk_feed_range_epk = FeedRangeInternalEpk.from_json(pk_feed_range)
        target_feed_range_epk = FeedRangeInternalEpk.from_json(target_pk_range)
        if (pk_feed_range_epk.get_normalized_range() ==
                target_feed_range_epk.get_normalized_range()):
            target_session_token = session_token
        previous_session_token = session_token
        feed_ranges_and_session_tokens.append((pk_feed_range,
                                               session_token))
    return target_session_token, previous_session_token


async def create_items_physical_pk_async(container, pk_feed_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
    # Source: tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.create_items_physical_pk_async
    target_session_token = ""
    container_feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
    target_feed_range = None
    for feed_range in container_feed_ranges:
        if await container.is_feed_range_subset(feed_range, pk_feed_range):
            target_feed_range = feed_range
            break

    for i in range(100):
        item = create_item(hpk)
        response = await container.create_item(item, session_token=previous_session_token)
        session_token = response.get_response_headers()[HttpHeaders.SessionToken]
        if hpk:
            pk = [item['state'], item['city'], item['zipcode']]
            curr_feed_range = await container.feed_range_from_partition_key(pk)
        else:
            curr_feed_range = await container.feed_range_from_partition_key(item['pk'])
        if await container.is_feed_range_subset(target_feed_range, curr_feed_range):
            target_session_token = session_token
        previous_session_token = session_token
        feed_ranges_and_session_tokens.append((curr_feed_range, session_token))

    return target_session_token, target_feed_range, previous_session_token
