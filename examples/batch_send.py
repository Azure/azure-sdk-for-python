#!/usr/bin/env python

"""
An example to show batch sending events to an Event Hub.
"""

# pylint: disable=C0111

import sys
import logging
import datetime
import time
import os

from azure.eventhub import EventHubClient, Sender, EventData

import examples
logger = examples.get_logger(logging.INFO)

# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')


def data_generator():
    for i in range(1500):
        logger.info("Yielding message {}".format(i))
        yield b"Hello world"


try:
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")

    client = EventHubClient(ADDRESS, debug=False, username=USER, password=KEY)
    sender = client.add_sender(partition="1")
    client.run()
    try:
        start_time = time.time()
        data = EventData(batch=data_generator())
        sender.send(data)
    except:
        raise
    finally:
        end_time = time.time()
        client.stop()
        run_time = end_time - start_time
        logger.info("Runtime: {} seconds".format(run_time))

except KeyboardInterrupt:
    pass
