import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from azure.eventgrid import EventGridConsumer, CloudEvent, EventGridEvent
from azure.eventhub import EventHubConsumerClient

"""
An example to show receiving events from an Event Hub.
"""

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ["EVENTHUB_NAME"]


def on_event(partition_context, event):

    dict_event = event.body_as_json()[0]
    deserialized_event = eg_consumer.deserialize_event(dict_event)
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
