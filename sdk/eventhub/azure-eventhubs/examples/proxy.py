#!/usr/bin/env python

"""
An example to show sending and receiving events behind a proxy
"""
import os
import logging

from azure.eventhub import EventHubClient, EventPosition, EventData

import examples
logger = examples.get_logger(logging.INFO)


# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')
CONSUMER_GROUP = "$default"
EVENT_POSITION = EventPosition.first_available()
PARTITION = "0"
HTTP_PROXY = {
    'proxy_hostname': '127.0.0.1',  # proxy hostname
    'proxy_port': 3128,  # proxy port
    'username': 'admin',  # username used for proxy authentication if needed
    'password': '123456'  # password used for proxy authentication if needed
}


if not ADDRESS:
    raise ValueError("No EventHubs URL supplied.")

client = EventHubClient(ADDRESS, debug=False, username=USER, password=KEY, http_proxy=HTTP_PROXY)
sender = client.create_sender(partition=PARTITION)
receiver = client.create_receiver(consumer_group=CONSUMER_GROUP, partition=PARTITION, event_position=EVENT_POSITION)
try:
    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    print('Start sending events behind a proxy.')

    with sender:
        sender.send(list)

    print('Start receiving events behind a proxy.')

    with receiver:
        received = receiver.receive(max_batch_size=50, timeout=5)

except KeyboardInterrupt:
    pass

