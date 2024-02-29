# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridClient, EventGridPublisherClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


EVENTGRID_KEY_GA: str = os.environ["EVENTGRID_KEY_GA"]
EVENTGRID_ENDPOINT_GA: str = os.environ["EVENTGRID_ENDPOINT_GA"]
EVENTGRID_KEY: str = os.environ["EVENTGRID_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_EVENT_SUBSCRIPTION_NAME"]

# Create a NameSpace client
client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))

# Create a client using publisherClient naming, will create a NamespaceClient
client = EventGridPublisherClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))

# Try to create a basic client with the wrong endpoint
try:
    client_basic = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY), level="Basic")
except ValueError as e:
    print(e)

# Create a Basic Client with the correct endpoint
client_basic = EventGridClient(EVENTGRID_ENDPOINT_GA, AzureKeyCredential(EVENTGRID_KEY_GA), level="Basic")


# Publish an event to a topic using basic client
event = CloudEvent(data={"key": "value"}, type="Contoso.Items.ItemReceived", source="https://contoso.com/items")
client_basic.publish(TOPIC_NAME, event)

# Publish an event to a topic using standard client
client.publish(TOPIC_NAME, event)


# Receive events from EventGrid with a basic client - raise error
try:
    client_basic.receive_cloud_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME)
except ValueError as e:
    print(e)

# Receive events from EventGrid standard client
    client.receive_cloud_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME)