#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show streaming sending events with different options to an Event Hub.
"""

# pylint: disable=C0111

import time
import os

from azure.eventhub import EventHubProducerClient, EventData

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


start_time = time.time()

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)
to_send_message_cnt = 500
bytes_per_message = 256

with producer:
    while to_send_message_cnt > 0:
        event_data_batch = producer.create_batch(max_size_in_bytes=2048)
        message_in_batch_cnt = 0
        while message_in_batch_cnt < to_send_message_cnt:
            try:
                event_data_batch.add(EventData('D' * bytes_per_message))
                message_in_batch_cnt += 1
            except ValueError:
                break
        producer.send_batch(event_data_batch)
        to_send_message_cnt -= message_in_batch_cnt

print("Send messages in {} seconds".format(time.time() - start_time))
