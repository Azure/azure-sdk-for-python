#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using aad credentials
"""

import os
from azure.eventhub import EventData, EventHubProducerClient
from azure.identity import EnvironmentCredential


HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']
EVENT_HUB = os.environ['EVENT_HUB_NAME']


credential = EnvironmentCredential()
producer = EventHubProducerClient(host=HOSTNAME,
                                  event_hub_path=EVENT_HUB,
                                  credential=credential)

with producer:
    event_data_batch = producer.create_batch(max_size=10000)
    while True:
        try:
            event_data_batch.add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break
    producer.send_batch(event_data_batch)
