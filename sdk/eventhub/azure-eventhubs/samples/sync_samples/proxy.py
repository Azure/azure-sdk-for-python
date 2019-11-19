#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending and receiving events behind a proxy
"""
import os
import time
from azure.eventhub import EventPosition, EventData, EventHubConsumerClient, EventHubProducerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENT_HUB = os.environ['EVENT_HUB_NAME']

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"
HTTP_PROXY = {
    'proxy_hostname': '127.0.0.1',  # proxy hostname
    'proxy_port': 3128,  # proxy port
    'username': 'admin',  # username used for proxy authentication if needed
    'password': '123456'  # password used for proxy authentication if needed
}


def on_event(partition_context, events):
    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    # do some operations on the event
    print(event)


consumer_client = EventHubConsumerClient.from_connection_string(
    conn_str=CONNECTION_STR, event_hub_path=EVENT_HUB, http_proxy=HTTP_PROXY)
producer_client = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR, event_hub_path=EVENT_HUB, http_proxy=HTTP_PROXY)

with producer_client:
    event_data_batch = producer_client.create_batch(max_size=10000)
    while True:
        try:
            event_data_batch.add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break
    producer.send_batch(event_data_batch)
    print('Finish sending.')

with consumer_client:
    receiving_time = 5
    consumer_client.receive(on_event=on_event, consumer_group='$Default')
    print('Finish receiving.')

