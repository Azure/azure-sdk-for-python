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


try:
    # Publish a CloudEvent
    cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event)

    # Receive CloudEvents and parse out lock tokens
    receive_result = client.receive_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=1, max_wait_time=15)
    lock_tokens_to_release = []
    for item in receive_result.value:
        lock_tokens_to_release.append(item.broker_properties.lock_token)

    print("Received events:", receive_result.value)

    # Release a LockToken
    release_token = ReleaseOptions(lock_tokens=lock_tokens_to_release)
    release_events = client.release_cloud_events(
        topic_name=TOPIC_NAME,
        event_subscription_name=EVENT_SUBSCRIPTION_NAME,
        release_delay_in_seconds=60,
        release_options=release_token,
    )
    print("Released Event:", release_events)

    # Receive CloudEvents again
    receive_result = client.receive_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=1, max_wait_time=15)
    print("Received events after release:", receive_result.value)

    # Acknowledge a LockToken
    acknowledge_token = AcknowledgeOptions(lock_tokens=lock_tokens_to_release)
    acknowledge_events = client.acknowledge_cloud_events(
        topic_name=TOPIC_NAME,
        event_subscription_name=EVENT_SUBSCRIPTION_NAME,
        acknowledge_options=acknowledge_token,
    )
    print("Acknowledged events after release:", acknowledge_events)
except HttpResponseError:
    raise
