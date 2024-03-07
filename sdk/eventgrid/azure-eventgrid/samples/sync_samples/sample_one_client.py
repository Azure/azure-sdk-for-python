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


EVENTGRID_KEY_GA: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_KEY"]
EVENTGRID_ENDPOINT_GA: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT"]
EVENTGRID_KEY: str = os.environ["EVENTGRID_NAMESPACE_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_NAMESPACES_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_NAMESPACE_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_NAMESPACE_SUBSCRIPTION_NAME"]

# Create a NameSpace client
namespace_client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))

# Create a client using publisherClient naming, will create a PublisherClient and fail on operations
publisher_client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA, AzureKeyCredential(EVENTGRID_KEY_GA))

# Create a standard client using EventGridClient
try:
    client_standard = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))
except ValueError as e:
    print(e)

# Create a Basic Client with the correct endpoint
client_basic = EventGridClient(EVENTGRID_ENDPOINT_GA, AzureKeyCredential(EVENTGRID_KEY_GA))

# Publish an event to a topic using basic client
event = CloudEvent(data={"key": "value"}, type="Contoso.Items.ItemReceived", source="https://contoso.com/items")
client_basic.publish(TOPIC_NAME, event)

# Publish an event to a topic using NameSpace client
client_standard.publish(TOPIC_NAME, event)

# Publish an event to a topic using Publisher client
publisher_client.send(event)


# Receive events from EventGrid with a basic client - raise error
try:
    client_basic.receive_cloud_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME)
except AttributeError as e:
    print(e)

try:
    # Receive events from EventGrid publisher client
    publisher_client.receive_cloud_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME)
except AttributeError as e:
    print(e)

# Receive events from EventGrid with a standard client
try:
    events = client_standard.receive_cloud_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME)
    print(events)
except AttributeError as e:
    print(e)