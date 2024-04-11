# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_release_receive_async.py
DESCRIPTION:
    These samples demonstrate sending, receiving, and releasing CloudEvents.
USAGE:
    python sample_publish_release_receive_async.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_KEY - The access key of your eventgrid account.
    2) EVENTGRID_ENDPOINT - The namespace endpoint. Typically it exists in the format
    "https://<YOUR-NAMESPACE-NAME>.<REGION-NAME>.eventgrid.azure.net".
    3) EVENTGRID_TOPIC_NAME - The namespace topic name.
    4) EVENTGRID_EVENT_SUBSCRIPTION_NAME - The event subscription name.
"""
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


EVENTGRID_KEY: str = os.environ["EVENTGRID_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_EVENT_SUBSCRIPTION_NAME"]


async def run():
    # Create a client
    client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))

    async with client:
        try:
            # Publish a CloudEvent
            cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
            await client.send(topic_name=TOPIC_NAME, events=cloud_event)

            # Receive CloudEvents and parse out lock tokens
            receive_result = await client.receive_cloud_events(topic_name=TOPIC_NAME, subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=1, max_wait_time=15)
            lock_tokens_to_release = []
            for item in receive_result.value:
                lock_tokens_to_release.append(item.broker_properties.lock_token)

            print("Received events:", receive_result.value)

            # Release a LockToken
            release_events = await client.release_cloud_events(
                topic_name=TOPIC_NAME,
                subscription_name=EVENT_SUBSCRIPTION_NAME,
                release_delay=60,
                lock_tokens=lock_tokens_to_release,
            )
            print("Released Event:", release_events)

            # Receive CloudEvents again
            receive_result = await client.receive_cloud_events(topic_name=TOPIC_NAME, subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=1, max_wait_time=15)
            print("Received events after release:", receive_result.value)

            # Acknowledge a LockToken that was released
            acknowledge_events = await client.acknowledge_cloud_events(
                topic_name=TOPIC_NAME,
                subscription_name=EVENT_SUBSCRIPTION_NAME,
                lock_tokens=lock_tokens_to_release,
            )
            print("Acknowledged events after release:", acknowledge_events)
        except HttpResponseError:
            raise

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())