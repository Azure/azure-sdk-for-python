# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import pytest
from datetime import datetime, timedelta
from math import ceil
from time import sleep

try:
    # Hack to run ChangeFeed tests locally due to conflicting namespace and dependency with blob.
    # To run locally, set each library folder in ChangeFeed package as "Sources Root" in PyCharm
    # (i.e. azure, storage, blob, changefeed).
    from changefeed import ChangeFeedClient
except ImportError:
    from azure.storage.blob.changefeed import ChangeFeedClient

from devtools_testutils.storage import StorageTestCase
from settings.testcase import ChangeFeedPreparer
from azure.core.credentials import AzureNamedKeyCredential

@pytest.mark.playback_test_only
class StorageChangeFeedTest(StorageTestCase):

    # --Test cases for change feed -----------------------------------------
    @ChangeFeedPreparer()
    def test_get_change_feed_events_by_page(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        results_per_page = 10
        change_feed = cf_client.list_changes(results_per_page=results_per_page).by_page()

        # get first page of events
        change_feed_page1 = next(change_feed)
        events_per_page1 = list(change_feed_page1)

        # get second page of events
        change_feed_page2 = next(change_feed)
        events_per_page2 = list(change_feed_page2)

        # Assert
        self.assertEqual(len(events_per_page1), results_per_page)
        self.assertEqual(len(events_per_page2), results_per_page)
        self.assertNotEqual(events_per_page1[results_per_page-1]['id'], events_per_page2[0]['id'])

        # Merge the two small pages into one
        events_per_page1.extend(events_per_page2)
        merged_two_pages = events_per_page1

        # get a page with the size of merged pages
        change_feed = cf_client.list_changes(results_per_page=2 * results_per_page).by_page()
        one_page = list(next(change_feed))

        # Assert
        # getting two pages separately gives the same result as getting the big page at once
        for i in range(0, len(one_page)):
            self.assertTrue(merged_two_pages[i].get('id') == one_page[i].get('id'))

    @ChangeFeedPreparer()
    def test_get_all_change_feed_events(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        change_feed = cf_client.list_changes()
        all_events = list(change_feed)
        total_events = len(all_events)

        self.assertTrue(len(all_events) > 0)

        results_per_page = 500
        change_feed_by_page = cf_client.list_changes(results_per_page=results_per_page).by_page()
        pages = list(change_feed_by_page)
        event_number_in_all_pages = 0
        for page in pages:
            page_size = len(list(page))
            event_number_in_all_pages += page_size

        self.assertEqual(ceil(len(all_events)*1.0/results_per_page), len(pages))
        self.assertEqual(total_events, event_number_in_all_pages)

    @ChangeFeedPreparer()
    def test_get_change_feed_events_with_continuation_token(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        # To get the total events number
        start_time = datetime(2020, 8, 18)
        end_time = datetime(2020, 8, 19)
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time)
        all_events = list(change_feed)
        total_events = len(all_events)

        # To start read events and get continuation token
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=180).by_page()
        change_feed_page1 = next(change_feed)
        events_per_page1 = list(change_feed_page1)
        token = change_feed.continuation_token

        # restart to read using the continuation token
        rest_events = list()
        change_feed2 = cf_client.list_changes().by_page(continuation_token=token)
        for page in change_feed2:
            rest_events.extend(list(page))

        # Assert the
        self.assertEqual(total_events, len(events_per_page1) + len(rest_events))

    @ChangeFeedPreparer()
    def test_get_change_feed_events_in_a_time_range(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        start_time = datetime(2020, 8, 12)
        end_time = datetime(2020, 8, 18)
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=2).by_page()

        # print first page of events
        page1 = next(change_feed)
        events = list(page1)

        self.assertIsNot(len(events), 0)

    @ChangeFeedPreparer()
    def test_change_feed_does_not_fail_on_empty_event_stream(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        start_time = datetime(2300, 8, 19)
        change_feed = cf_client.list_changes(start_time=start_time)

        events = list(change_feed)
        self.assertEqual(len(events), 0)

    @ChangeFeedPreparer()
    def test_read_change_feed_tail_where_3_shards_have_data(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)

        # to read until the end
        start_time = datetime(2020, 8, 19, 23)

        # this end_time is to avoid breaking change caused by a new year, it was 2020/08/19 when we recorded the test
        end_time = datetime(2020, 8, 28, 1)

        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time).by_page()

        events = list()
        for page in change_feed:
            for event in page:
                events.append(event)
        token = change_feed.continuation_token

        dict_token = json.loads(token)
        self.assertTrue(len(events) > 0)
        self.assertEqual(dict_token['CursorVersion'], 1)
        self.assertIsNotNone(dict_token['UrlHost'])
        self.assertEqual(len(dict_token['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['SegmentPath'])
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['CurrentShardPath'])

        if self.is_live:
            sleep(120)
        print("continue printing events")

        # restart using the continuation token after waiting for 2 minutes
        change_feed2 = cf_client.list_changes(results_per_page=6).by_page(continuation_token=token)
        change_feed_page2 = next(change_feed2)
        events2 = list()
        for event in change_feed_page2:
            events2.append(event)

        self.assertNotEqual(events2, 0)

        if self.is_live:
            sleep(120)
        print("continue printing events")

        # restart using the continuation token which has Non-zero EventIndex for 3 shards
        token2 = change_feed2.continuation_token
        dict_token2 = json.loads(token2)
        self.assertEqual(len(dict_token2['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertNotEqual(dict_token2['CurrentSegmentCursor']['ShardCursors'][0]['EventIndex'], 0)
        self.assertNotEqual(dict_token2['CurrentSegmentCursor']['ShardCursors'][1]['EventIndex'], 0)
        self.assertNotEqual(dict_token2['CurrentSegmentCursor']['ShardCursors'][2]['EventIndex'], 0)

        change_feed3 = cf_client.list_changes(results_per_page=57).by_page(continuation_token=token2)
        change_feed_page3 = next(change_feed3)
        events3 = list()
        for event in change_feed_page3:
            events3.append(event)
        self.assertNotEqual(events2, 0)

    @ChangeFeedPreparer()
    def test_read_change_feed_tail_where_only_1_shard_has_data(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)

        # to read until the end
        start_time = datetime(2020, 8, 20, 1)

        # this end_time is to avoid breaking change caused by a new year, it was 2020/08/20 when we recorded the test
        end_time = datetime(2020, 8, 28, 8)

        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=3).by_page()

        page = next(change_feed)
        events_on_first_page = list()
        for event in page:
            events_on_first_page.append(event)

        token = change_feed.continuation_token
        dict_token = json.loads(token)

        self.assertEqual(len(events_on_first_page), 3)
        self.assertEqual(dict_token['CursorVersion'], 1)
        self.assertIsNotNone(dict_token['UrlHost'])
        self.assertEqual(len(dict_token['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['SegmentPath'])
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['CurrentShardPath'])

        # if self.is_live:
        #     sleep(120)
        print("continue printing events")

        # restart using the continuation token after waiting for 2 minutes
        change_feed2 = cf_client.list_changes(results_per_page=5).by_page(continuation_token=token)
        events2 = []
        for page in change_feed2:
            for event in page:
                events2.append(event)

        self.assertIsNot(len(events2), 0)

    @ChangeFeedPreparer()
    def test_read_change_feed_with_3_shards_in_a_time_range(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)

        # to get continuation token
        start_time = datetime(2020, 8, 19, 22)
        end_time = datetime(2020, 8, 19, 23)
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=16).by_page()

        page = next(change_feed)
        events = list(page)
        self.assertEqual(len(events), 16)

        token = change_feed.continuation_token

        dict_token = json.loads(token)
        self.assertEqual(dict_token['CursorVersion'], 1)
        self.assertIsNotNone(dict_token['EndTime'])
        self.assertIsNotNone(dict_token['UrlHost'])
        self.assertEqual(len(dict_token['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['SegmentPath'])
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['CurrentShardPath'])

        change_feed2 = cf_client.list_changes().by_page(continuation_token=token)
        events = list(next(change_feed2))

        end_time_str = (end_time + timedelta(hours=1)).isoformat()
        self.assertTrue(events[len(events) - 1]['eventTime'] < end_time_str)

    @ChangeFeedPreparer()
    def test_read_3_shards_change_feed_during_a_time_range_in_multiple_times_gives_same_result_as_reading_all(
            self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)

        # to read until the end
        start_time = datetime(2020, 8, 5, 17)
        end_time = datetime(2020, 8, 5, 17, 15)

        all_events = list(cf_client.list_changes(start_time=start_time, end_time=end_time))
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=50).by_page()

        events = list()
        for _ in (0, 2):
            page = next(change_feed)
            for event in page:
                events.append(event)
        token = change_feed.continuation_token

        dict_token = json.loads(token)
        self.assertTrue(len(events) > 0)
        self.assertEqual(dict_token['CursorVersion'], 1)
        self.assertIsNotNone(dict_token['UrlHost'])
        self.assertEqual(len(dict_token['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['SegmentPath'])
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['CurrentShardPath'])

        # make sure end_time and continuation_token are mutual exclusive
        with self.assertRaises(ValueError):
            cf_client.list_changes(results_per_page=50, end_time=datetime.now()).by_page(continuation_token=token)
        # make sure start_time and continuation_token are mutual exclusive
        with self.assertRaises(ValueError):
            cf_client.list_changes(results_per_page=50, start_time=datetime.now()).by_page(continuation_token=token)

        # restart using the continuation token after waiting for 2 minutes
        change_feed2 = cf_client.list_changes(results_per_page=50).by_page(continuation_token=token)
        events2 = list()
        for _ in (0, 2):
            page = next(change_feed2)
            for event in page:
                events2.append(event)

        self.assertNotEqual(events2, 0)

        # restart using the continuation token which has Non-zero EventIndex for 3 shards
        token2 = change_feed2.continuation_token
        dict_token2 = json.loads(token2)
        self.assertEqual(len(dict_token2['CurrentSegmentCursor']['ShardCursors']), 3)

        change_feed3 = cf_client.list_changes(results_per_page=50).by_page(continuation_token=token2)
        events3 = list()
        for page in change_feed3:
            for event in page:
                events3.append(event)

        token3 = change_feed3.continuation_token
        dict_token3 = json.loads(token3)

        self.assertNotEqual(events3, 0)
        self.assertEqual(len(dict_token3['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertEqual(len(events)+len(events2)+len(events3), len(all_events))

    @ChangeFeedPreparer()
    def test_list_3_shards_events_works_with_1_shard_cursor(self, storage_account_name, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        start_time = datetime(2020, 8, 5, 17)
        end_time = datetime(2020, 8, 5, 17, 15)
        change_feed = cf_client.list_changes(results_per_page=1, start_time=start_time, end_time=end_time).by_page()
        next(change_feed)
        token_with_1_shard = change_feed.continuation_token

        change_feed = cf_client.list_changes(results_per_page=50).by_page(continuation_token=token_with_1_shard)
        events = list()
        for _ in range(0, 2):
            page = next(change_feed)
            for event in page:
                events.append(event)
        dict_token = json.loads(change_feed.continuation_token)
        dict_token_with_1_shard = json.loads(token_with_1_shard)
        self.assertEqual(len(dict_token_with_1_shard['CurrentSegmentCursor']['ShardCursors']), 1)
        self.assertEqual(len(dict_token['CurrentSegmentCursor']['ShardCursors']), 3)
