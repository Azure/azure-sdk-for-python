# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: consume_cloud_events_from_eventhub.py
DESCRIPTION:
    These samples demonstrate receiving events from an Event Hub.
USAGE:
    python consume_cloud_events_from_eventhub.py
    Set the environment variables with your own values before running the sample:
    1) EVENT_HUB_CONN_STR: The connection string to the Event hub account
    3) EVENTHUB_NAME: The name of the eventhub account
"""
import os
import json
from azure.core.messaging import CloudEvent
from azure.eventhub import EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ["EVENTHUB_NAME"]


def on_event(partition_context, event):
 
    dict_event = CloudEvent.from_dict(json.loads(event)[0])
    print("data: {}\n".format(deserialized_event.data))

consumer_client = EventHubConsumerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
)

with consumer_client:
    event_list = consumer_client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
        prefetch=5
    )
