# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_binary_mode.py
DESCRIPTION:
    These samples demonstrate sending CloudEvents in binary mode.
USAGE:
    python sample_binary_mode.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_KEY - The access key of your eventgrid account.
    2) EVENTGRID_ENDPOINT - The namespace endpoint. Typically it exists in the format
    "https://<YOUR-NAMESPACE-NAME>.<REGION-NAME>.eventgrid.azure.net".
    3) EVENTGRID_TOPIC_NAME - The namespace topic name.
    4) EVENTGRID_EVENT_SUBSCRIPTION_NAME - The event subscription name.
"""
import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


EVENTGRID_KEY: str = os.environ["EVENTGRID_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_EVENT_SUBSCRIPTION_NAME"]

# Create a client
client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))


# Publish a CloudEvent
try:
    # Publish CloudEvent in binary mode with str encoded as bytes
    cloud_event_dict = {
        "data": b"HI",
        "source": "https://example.com",
        "type": "example",
        "datacontenttype": "text/plain",
    }
    client.send(topic_name=TOPIC_NAME, events=cloud_event_dict, binary_mode=True)

    # Publish CloudEvent in binary mode with json encoded as bytes
    cloud_event = CloudEvent(
        data=json.dumps({"hello": "data"}).encode("utf-8"),
        source="https://example.com",
        type="example",
        datacontenttype="application/json",
    )
    client.send(topic_name=TOPIC_NAME, events=cloud_event, binary_mode=True)

    # Receive a CloudEvent
    receive_result = client.receive_cloud_events(
        topic_name=TOPIC_NAME, subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=100
    )
    for receive_details in receive_result.value:
        cloud_event_received = receive_details.event
        print("CloudEvent: ", cloud_event_received)
        print("CloudEvent data: ", cloud_event_received.data)
except HttpResponseError:
    raise
