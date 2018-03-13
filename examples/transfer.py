#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

# pylint: disable=C0111

import sys
import logging
import datetime
import time
import os

from eventhubs import EventHubClient, Sender, EventData

import examples
logger = examples.get_logger(logging.INFO)


# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

try:
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")

    sender = Sender()
    client = EventHubClient(ADDRESS, debug=False, username=USER, password=KEY).publish(sender).run()
    try:
        start_time = time.time()
        for i in range(1000):
            sender.transfer(EventData(str(i)))
        sender.wait()
    except:
        raise
    finally:
        end_time = time.time()
        client.stop()
        run_time = end_time - start_time
        logger.info("Runtime: {} seconds".format(run_time))

except KeyboardInterrupt:
    pass
