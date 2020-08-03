import sys
import os
import datetime as dt
import json

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from msrestazure.azure_active_directory import ServicePrincipalCredentials
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

from azure.eventgrid import EventGridConsumer, CloudEvent, EventGridEvent
from azure.servicebus import ServiceBusClient, Message

def get_deserialized_events(msg):
    events = consumer.deserialize_events(msg)
    for event in events:
        if type(event.model) == CloudEvent:
            print(type(event["time"]))
            print(type(event["data"]))
            print(event.model)
            print(type(event.model.data))
            print(type(event.model.time))

connection_str = os.environ.get('SB_CONN_STR')

sb_client = ServiceBusClient.from_connection_string(connection_str)
consumer = EventGridConsumer()

#while True:
with sb_client:
    receiver = sb_client.get_queue_receiver("cloudeventqueue", prefetch=1)
    with receiver:
        msgs = receiver.receive(max_batch_size=1, max_wait_time=5)
        for msg in msgs:
            msg.complete()
            get_deserialized_events(msg)
