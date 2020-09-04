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

from azure.eventgrid import EventGridConsumer, CloudEvent, EventGridEvent
from azure.eventhub import EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ["EVENTHUB_NAME"]


def on_event(partition_context, event):

    dict_event = event.body_as_json()[0]
    deserialized_event = eg_consumer.decode_eventgrid_event(dict_event)
    if deserialized_event.model.__class__ == CloudEvent:
        dict_event = deserialized_event.to_json()
        print("event.type: {}\n".format(dict_event["type"]))
        print("event.to_json(): {}\n".format(dict_event))
        print("model: {}\n".format(deserialized_event.model))
        print("model.data: {}\n".format(deserialized_event.model.data))
    else:
        dict_event = deserialized_event.to_json()
        print("event.to_json(): {}\n".format(dict_event))
        print("model: {}\n".format(deserialized_event.model))
        print("model.data: {}\n".format(deserialized_event.model.data))

eg_consumer = EventGridConsumer()
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
