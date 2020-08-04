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

from azure.eventgrid import EventGridConsumer, CloudEvent
from azure.servicebus import ServiceBusClient, Message

connection_str = os.environ['SB_CONN_STR']

sb_client = ServiceBusClient.from_connection_string(connection_str)
consumer = EventGridConsumer()
with sb_client:
    receiver = sb_client.get_queue_receiver("cloudeventqueue", prefetch=10)
    with receiver:
        msgs = receiver.receive(max_batch_size=10, max_wait_time=1)
        print("number of messages: {}".format(len(msgs)))
        for msg in msgs:
            # receive single dict message
            deserialized_event = consumer.deserialize_event(str(msg))
            if deserialized_event.model.__class__ == CloudEvent:
                dict_event = deserialized_event.to_json()
                print("event.type: {}\n".format(dict_event["type"]))
                print("event.to_json(): {}\n".format(dict_event))
                print("model: {}\n".format(deserialized_event.model))
                print("model.data: {}\n".format(deserialized_event.model.data))
            else:
                dict_event = deserialized_event.to_json()
                print("event.eventType: {}\n".format(dict_event["eventType"]))
                print("event.to_json(): {}\n".format(dict_event))
                print("model: {}\n".format(deserialized_event.model))
                print("model.data: {}\n".format(deserialized_event.model.data))
            msg.complete()
