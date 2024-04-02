# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_operation_async.py
DESCRIPTION:
    These samples demonstrate sending CloudEvents.
USAGE:
    python sample_publish_operation_async.py
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

# Create a client
client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))


async def run():
    async with client:

        # Publish a CloudEvent as dict
        try:
            cloud_event_dict = {"data": "hello", "source": "https://example.com", "type": "example"}
            await client.send(topic_name=TOPIC_NAME, events=cloud_event_dict)
        except HttpResponseError:
            raise

        # Publish a list of CloudEvents as dict
        try:
            await client.send(topic_name=TOPIC_NAME, events=[cloud_event_dict, cloud_event_dict])
        except HttpResponseError:
            raise

        
        # Publish a CloudEvent
        try:
            cloud_event = CloudEvent(
                data="HI", source="https://example.com", type="example"
            )
            await client.send(topic_name=TOPIC_NAME, events=cloud_event)
        except HttpResponseError:
            raise

        # Publish a list of CloudEvents
        try:
            list_of_cloud_events = [cloud_event, cloud_event]
            await client.send(
                topic_name=TOPIC_NAME, events=list_of_cloud_events
            )
        except HttpResponseError:
            raise


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
