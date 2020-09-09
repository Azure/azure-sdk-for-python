# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: change_feed_samples.py
DESCRIPTION:
    This sample demonstrates
    1) list events by page
    2) list all events
    3) list events in a time range
    4) list events starting from a continuation token
USAGE:
    python blob_samples_container.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    2) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""

import os
from datetime import datetime
from time import sleep

from azure.storage.blob.changefeed import ChangeFeedClient


class ChangeFeedSamples(object):

    ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCESS_KEY")

    def list_events_by_page(self):

        # Instantiate a ChangeFeedClient
        # [START list_events_by_page]
        # [START create_change_feed_client]
        cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format(self.ACCOUNT_NAME),
                                     credential=self.ACCOUNT_KEY)
        # [END create_change_feed_client]

        change_feed = cf_client.list_changes(results_per_page=10).by_page()

        # print first page of events
        change_feed_page1 = next(change_feed)
        for event in change_feed_page1:
            print(event)

        # print second page of events
        change_feed_page2 = next(change_feed)
        for event in change_feed_page2:
            print(event)
        # [END list_events_by_page]

    def list_all_events(self):
        # [START list_all_events]
        cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format(self.ACCOUNT_NAME),
                                     credential=self.ACCOUNT_KEY)
        change_feed = cf_client.list_changes()

        # print all events
        for event in change_feed:
            print(event)
    # [END list_all_events]

    def list_range_of_events(self):
        cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format(self.ACCOUNT_NAME),
                                     credential=self.ACCOUNT_KEY)
        start_time = datetime(2020, 8, 18, 10)
        end_time = datetime(2020, 3, 4)
        change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time)

        # print first page of events
        for event in change_feed:
            print(event)

    def list_events_using_continuation_token(self):

        # Instantiate a ChangeFeedClient
        cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format(self.ACCOUNT_NAME),
                                     credential=self.ACCOUNT_KEY)
        # to get continuation token
        change_feed = cf_client.list_changes(results_per_page=2).by_page()
        change_feed_page1 = next(change_feed)
        for event in change_feed_page1:
            print(event)
        token = change_feed.continuation_token

        # restart using the continuation token
        change_feed2 = cf_client.list_changes(results_per_page=56).by_page(continuation_token=token)
        change_feed_page2 = next(change_feed2)
        for event in change_feed_page2:
            print(event)

    def list_events_in_live_mode(self):
        # Instantiate a ChangeFeedClient
        cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format(self.ACCOUNT_NAME),
                                     credential=self.ACCOUNT_KEY)
        token = None
        while True:
            change_feed = cf_client.list_changes(results_per_page=500).by_page(continuation_token=token)

            for page in change_feed:
                for event in page:
                    print(event)
            token = change_feed.continuation_token

            sleep(60)
            print("continue printing events")


if __name__ == '__main__':
    sample = ChangeFeedSamples()
    sample.list_events_by_page()
    sample.list_all_events()
    sample.list_range_of_events()
    sample.list_events_using_continuation_token()
    sample.list_events_in_live_mode()

