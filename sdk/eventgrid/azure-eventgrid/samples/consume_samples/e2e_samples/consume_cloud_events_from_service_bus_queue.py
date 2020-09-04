# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: consume_cloud_events_from_eventhub.py
DESCRIPTION:
    These samples demonstrate receiving events from Service Bus.
USAGE:
    python consume_cloud_events_from_eventhub.py
    Set the environment variables with your own values before running the sample:
    1) SB_CONN_STR: The connection string to the Service Bus account
    3) SERVICE_BUS_QUEUE_NAME: The name of the servicebus account
"""
import os

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential

from azure.eventgrid import EventGridConsumer, CloudEvent
from azure.servicebus import ServiceBusClient

connection_str = os.environ['SB_CONN_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

sb_client = ServiceBusClient.from_connection_string(connection_str)
consumer = EventGridConsumer()
with sb_client:
    receiver = sb_client.get_queue_receiver(queue_name, prefetch=10)
    with receiver:
        msgs = receiver.receive(max_batch_size=10, max_wait_time=1)
        print("number of messages: {}".format(len(msgs)))
        for msg in msgs:
            # receive single dict message
            if 'specversion' in msg:
                deserialized_event = consumer.decode_cloud_event(str(msg))
                dict_event = deserialized_event.to_json()
                print("event.to_json(): {}\n".format(dict_event))
                print("model: {}\n".format(deserialized_event.model))
                print("model.data: {}\n".format(deserialized_event.model.data))
            else:
                deserialized_event = consumer.decode_eventgrid_event(str(msg))
                dict_event = deserialized_event.to_json()
                print("event.to_json(): {}\n".format(dict_event))
                print("model: {}\n".format(deserialized_event.model))
                print("model.data: {}\n".format(deserialized_event.model.data))
            msg.complete()
