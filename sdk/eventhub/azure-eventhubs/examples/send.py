#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending individual events to an Event Hub partition.
Although this works, sending events in batches will get better performance.
See 'send_list_of_event_data.py' and 'send_event_data_batch.py' for an example of batching.
"""

# pylint: disable=C0111

import time
import os
from azure.eventhub import EventHubProducerClient, EventData, EventHubSharedKeyCredential

EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENT_HUB = os.environ['EVENT_HUB_NAME']

producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, event_hub_path=EVENT_HUB)

start_time = time.time()
with producer:
    ed = EventData("msg sent to partition_id 0")
    producer.send(ed, partition_id='0')

    ed = EventData("msg sent with partition_key")
    producer.send(ed, partition_key="p_key")
print("Send messages in {} seconds".format(time.time() - start_time))
