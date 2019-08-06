#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show creating and sending EventBatchData within limited size.
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


def create_batch_data(producer):
    event_data_batch = producer.create_batch(max_size=10000)
    while True:
        try:
            event_data_batch.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break
    return event_data_batch


try:
    if not HOSTNAME:
        raise ValueError("No EventHubs URL supplied.")

    client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                            network_tracing=False)
    producer = client.create_producer()

    try:
        start_time = time.time()
        with producer:
            event_data_batch = create_batch_data(producer)
            producer.send(event_data_batch)
    except:
        raise
    finally:
        end_time = time.time()
        run_time = end_time - start_time
        logger.info("Runtime: {} seconds".format(run_time))

except KeyboardInterrupt:
    pass
