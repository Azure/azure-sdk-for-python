# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridClient, EventGridPublisherClient, EventGridEvent
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


# Cloud Event Topic
EVENTGRID_KEY_GA: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_KEY"]
EVENTGRID_ENDPOINT_GA: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT"]

# EventGridEvent Topic
EVENTGRID_KEY_GA_EVENTGRIDEVENT: str = os.environ["EVENTGRID_TOPIC_KEY"]
EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT: str = os.environ["EVENTGRID_TOPIC_ENDPOINT"]

# EventGrid Namespaces
EVENTGRID_KEY: str = os.environ["EVENTGRID_NAMESPACE_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_NAMESPACES_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_NAMESPACE_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_NAMESPACE_SUBSCRIPTION_NAME"]


# Create a Cloud Event Topic client
client_basic = EventGridClient(EVENTGRID_ENDPOINT_GA, AzureKeyCredential(EVENTGRID_KEY_GA))

# Create a Cloud Event and publish it to the topic
event = CloudEvent(data={"key": "value"}, type="Contoso.Items.ItemReceived", source="https://contoso.com/items")
client_basic.publish(TOPIC_NAME, event)

# Try calling `send` method on the Cloud Event Topic client
try:
    client_basic.send(TOPIC_NAME, event)
except AttributeError as e:
    print(e)

# Try Acknowledge the Cloud Event
try:
    client_basic.acknowledge_cloud_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME, AcknowledgeOptions(lock_tokens=["token"]))
except AttributeError as e:
    print(e)


# Create an EventGridEvent Topic client
client_basic = EventGridClient(EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT, AzureKeyCredential(EVENTGRID_KEY_GA_EVENTGRIDEVENT))

# Create an EventGridEvent and publish it to the topic
eventgrid_event = EventGridEvent(
    id="12345",
    subject="MySubject",
    data={"key": "value"},
    event_type="Contoso.Items.ItemReceived",
    data_version="2.0"
)
client_basic.publish(TOPIC_NAME, [eventgrid_event])

# Try calling `send` method on the EventGridEvent Topic client
try:
    client_basic.send(TOPIC_NAME, event)
except AttributeError as e:
    print(e)

# Try Acknowledge the EventGridEvent
try:
    client_basic.acknowledge_eventgrid_events(TOPIC_NAME, EVENT_SUBSCRIPTION_NAME, AcknowledgeOptions(lock_tokens=["token"]))
except AttributeError as e:
    print(e)



# Create a Namespace client
client_standard = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))

# Create a Cloud Event and publish it to the topic
client_standard.send(TOPIC_NAME, event)

# Create an EventGridEvent and send it to the topic
try:
    client_standard.send(TOPIC_NAME, eventgrid_event)
except Exception as e:
    print(e)

try:
    client_standard.send(TOPIC_NAME, [eventgrid_event])
except AttributeError as e:
    print(e)


# Create an EventGridPublisherClient
publisher_client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA, AzureKeyCredential(EVENTGRID_KEY_GA))

# Create a Cloud Event and publish it to the topic
publisher_client.send(event)
