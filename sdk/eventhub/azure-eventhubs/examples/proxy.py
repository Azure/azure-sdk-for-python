#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending and receiving events behind a proxy
"""
import os
import logging

from azure.eventhub import EventHubClient, EventPosition, EventData, EventHubSharedKeyCredential

import examples
logger = examples.get_logger(logging.INFO)


# Hostname can be <mynamespace>.servicebus.windows.net"
HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"
HTTP_PROXY = {
    'proxy_hostname': '127.0.0.1',  # proxy hostname
    'proxy_port': 3128,  # proxy port
    'username': 'admin',  # username used for proxy authentication if needed
    'password': '123456'  # password used for proxy authentication if needed
}


if not HOSTNAME:
    raise ValueError("No EventHubs URL supplied.")

client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY), network_tracing=False, http_proxy=HTTP_PROXY)
try:
    producer = client.create_producer(partition_id=PARTITION)
    consumer = client.create_consumer(consumer_group="$default", partition_id=PARTITION, event_position=EVENT_POSITION)

    consumer.receive(timeout=1)

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    print('Start sending events behind a proxy.')

    producer.send(event_list)

    print('Start receiving events behind a proxy.')

    received = consumer.receive(max_batch_size=50, timeout=5)
finally:
    producer.close()
    consumer.close()

