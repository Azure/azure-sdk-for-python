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

RECEIVE_TIMEOUT = 1  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small


def do_operation(event):
    # do some operations on the event
    print(event)


def on_events(partition_context, events):
    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    for event in events:
        do_operation(event)


consumer_client = EventHubConsumerClient.from_connection_string(
    conn_str=CONNECTION_STR, event_hub_path=EVENT_HUB, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL,
    http_proxy=HTTP_PROXY)
producer_client = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR, event_hub_path=EVENT_HUB, http_proxy=HTTP_PROXY)

with producer_client:
    producer_client.send(EventData("A single event"))
    print('Finish sending.')

with consumer_client:
    receiving_time = 5
    consumer_client.receive(on_events=on_events, consumer_group='$Default')
    time.sleep(receiving_time)
    print('Finish receiving.')

