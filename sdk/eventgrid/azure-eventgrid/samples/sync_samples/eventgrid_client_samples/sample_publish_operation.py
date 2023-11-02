# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
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

# Publish a CloudEvent as dict
try:
    cloud_event_dict = {"data": "hello", "source": "https://example.com", "type": "example"}
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event_dict)
except HttpResponseError:
    raise

# Publish a list of CloudEvents as dict
try:
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=[cloud_event_dict, cloud_event_dict])
except HttpResponseError:
    raise

# Publish a CloudEvent
try:
    cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event)
except HttpResponseError:
    raise

# Publish a list of CloudEvents
try:
    list_of_cloud_events = [cloud_event, cloud_event]
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=list_of_cloud_events)
except HttpResponseError:
    raise
