import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError
from azure.eventgrid import EventGridClient

EVENTGRID_KEY = os.environ.get("EVENTGRID_KEY")
EVENTGRID_ENDPOINT = os.environ.get("EVENTGRID_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
EVENT_SUBSCRIPTION_NAME = os.environ.get("EVENT_SUBSCRIPTION_NAME")


# Create a client
client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))


cloud_event_reject = CloudEvent(data="reject", source="https://example.com", type="example")
cloud_event_release = CloudEvent(data="release", source="https://example.com", type="example")
cloud_event_ack = CloudEvent(data="acknowledge", source="https://example.com", type="example")

# Publish a CloudEvent
try:
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event_reject)
except HttpResponseError:
    raise

# Publish a list of CloudEvents
try:
    list_of_cloud_events = [cloud_event_release, cloud_event_ack]
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=list_of_cloud_events)
except HttpResponseError:
    raise

# Receive Published Cloud Events
try:
    receive_results = client.receive_cloud_events(
        topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=10, max_wait_time=10
    )
except HttpResponseError:
    raise

# Iterate through the results and collect the lock tokens for events we want to release/acknowledge/reject:

release_events = []
acknowledge_events = []
reject_events = []

for detail in receive_results.get("value"):
    cloud_event = detail.get("event")
    broker_properties = detail.get("brokerProperties")
    if cloud_event.data == "release":
        release_events.append(broker_properties.get("lockToken"))
    elif cloud_event.data == "acknowledge":
        acknowledge_events.append(broker_properties.get("lockToken"))
    else:
        reject_events.append(broker_properties.get("lockToken"))

# Release/Acknowledge/Reject events

if len(release_events) > 0:
    try:
        release_result = client.release_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=release_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in release_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")

if len(acknowledge_events) > 0:
    try:
        ack_result = client.acknowledge_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=acknowledge_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in ack_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")

if len(reject_events) > 0:
    try:
        reject_result = client.reject_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=reject_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in reject_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")
