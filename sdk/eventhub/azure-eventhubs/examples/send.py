#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending events to an Event Hub partition.
This is just an example of sending EventData, not performance optimal.
To have the best performance, send a batch EventData with one send() call.
"""

# pylint: disable=C0111

import logging
import time
import os

from azure.eventhub import EventHubClient, EventData, EventHubSharedKeyCredential

import examples
logger = examples.get_logger(logging.INFO)


HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

try:
    if not HOSTNAME:
        raise ValueError("No EventHubs URL supplied.")

    client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                            network_tracing=False)
    producer = client.create_producer(partition_id="0")

    try:
        start_time = time.time()
        with producer:
            # not performance optimal, but works. Please do send events in batch to get much better performance.
            for i in range(100):
                ed = EventData("msg")
                logger.info("Sending message: {}".format(i))
                producer.send(ed)
    except:
        raise
    finally:
        end_time = time.time()
        run_time = end_time - start_time
        logger.info("Runtime: {} seconds".format(run_time))

except KeyboardInterrupt:
    pass
