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

from azure.eventgrid._consumer import EventGridConsumer
from azure.servicebus import ServiceBusClient, Message

connection_str = 'Endpoint=sb://t-swpill-service-bus-queue.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=EBfVpjF0v8p0G4Ksh35qi1VouzNxo1GQeKvDp2wx1I0='

sb_client = ServiceBusClient.from_connection_string(connection_str)
consumer = EventGridConsumer()

with sb_client:
    receiver = sb_client.get_queue_receiver("cloudeventqueue", prefetch=1)
    with receiver:
        msgs = receiver.receive(max_batch_size=1, max_wait_time=5)
        for msg in msgs:
            print(type(msg))
            msg.complete()
            get_deserialized_events(msg)

def get_deserialized_events(msg):
    events = consumer.deserialize_events(msg)
    for event in events:
        print(event["time"])
        print(type(event.model.time))