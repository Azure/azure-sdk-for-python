# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from time import sleep

import pytest
from datetime import datetime, timedelta

from math import ceil

from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer
from azure.storage.blob.changefeed import (
    ChangeFeedClient,
)

@pytest.mark.playback_test_only
class StorageChangeFeedTest(StorageTestCase):

    # --Test cases for change feed -----------------------------------------
    @GlobalStorageAccountPreparer()
    def test_get_change_feed_events_by_page(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)
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

    @GlobalStorageAccountPreparer()
    def test_get_all_change_feed_events(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)
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

    @GlobalStorageAccountPreparer()
    def test_get_change_feed_events_with_continuation_token(self, resource_group, location, storage_account,
                                                            storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)
        # To get the total events number
        change_feed = cf_client.list_changes()
        all_events = list(change_feed)
        total_events = len(all_events)

        # To start read events and get continuation token
        change_feed = cf_client.list_changes(results_per_page=180).by_page()
        change_feed_page1 = next(change_feed)
        events_per_page1 = list(change_feed_page1)
        token = change_feed.continuation_token

        # restart to read using the continuation token
        change_feed2 = cf_client.list_changes().by_page(continuation_token=token)
        change_feed_page2 = next(change_feed2)
        events_per_page2 = list(change_feed_page2)

        # Assert the
        self.assertEqual(total_events, len(events_per_page1) + len(events_per_page2))

    @GlobalStorageAccountPreparer()
    def test_get_change_feed_events_in_a_time_range(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)
        start_time = datetime(2020, 8, 12)
        end_time = datetime(2020, 8, 18)
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=2).by_page()

        # print first page of events
        page1 = next(change_feed)
        events = list(page1)

        self.assertIsNot(len(events), 0)

    @GlobalStorageAccountPreparer()
    def test_read_change_feed_without_any_seg(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)
        start_time = datetime(2021, 8, 19)
        change_feed = cf_client.list_changes(start_time=start_time)

        events = list(change_feed)
        self.assertEqual(len(events), 0)

    @GlobalStorageAccountPreparer()
    def test_read_change_feed_tail_where_3_shards_have_data(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)

        # to read until the end
        start_time = datetime(2020, 8, 19, 23)
        change_feed = cf_client.list_changes(start_time=start_time).by_page()

        for page in change_feed:
            for event in page:
                print(event)
        token = change_feed.continuation_token

        dict_token = eval(token)
        self.assertEqual(dict_token['CursorVersion'], 1)
        self.assertIsNotNone(dict_token['UrlHost'])
        self.assertEqual(len(dict_token['CurrentSegmentCursor']['ShardCursors']), 3)
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['SegmentPath'])
        self.assertIsNotNone(dict_token['CurrentSegmentCursor']['CurrentShardPath'])

        if self.is_live:
            sleep(120)
        print("continue printing events")

        # restart using the continuation token after waiting for 2 minutes
        change_feed2 = cf_client.list_changes(results_per_page=5).by_page(continuation_token=token)
        change_feed_page2 = next(change_feed2)
        for event in change_feed_page2:
            print(event)

        if self.is_live:
            sleep(120)
        print("continue printing events")

        # restart using the continuation token which has Non-zero EventIndex for 3 shards
        token2 = change_feed2.continuation_token
        change_feed3 = cf_client.list_changes(results_per_page=57).by_page(continuation_token=token2)
        change_feed_page3 = next(change_feed3)
        for event in change_feed_page3:
            print(event)

    @GlobalStorageAccountPreparer()
    def test_read_change_feed_tail_where_only_1_shard_has_data(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)

        # to read until the end
        start_time = datetime(2020, 8, 20, 1)
        change_feed = cf_client.list_changes(start_time=start_time, results_per_page=3).by_page()

        page = next(change_feed)
        for event in page:
            aaaaaa = event
        token = change_feed.continuation_token

        dict_token = eval(token)
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

    @GlobalStorageAccountPreparer()
    def test_read_change_feed_with_3_shards_in_a_time_range(self, resource_group, location, storage_account, storage_account_key):
        cf_client = ChangeFeedClient(self.account_url(storage_account, "blob"), storage_account_key)

        # to get continuation token
        start_time = datetime(2020, 8, 19, 22)
        end_time = datetime(2020, 8, 19, 23)
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time, results_per_page=16).by_page()

        page = next(change_feed)
        events = list(page)
        self.assertEqual(len(events), 16)

        token = change_feed.continuation_token

        dict_token = eval(token)
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
