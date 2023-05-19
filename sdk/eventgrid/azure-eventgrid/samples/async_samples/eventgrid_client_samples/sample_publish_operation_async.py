# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


EVENTGRID_KEY = os.environ.get("EVENTGRID_KEY")
EVENTGRID_ENDPOINT = os.environ.get("EVENTGRID_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
EVENT_SUBSCRIPTION_NAME = os.environ.get("EVENT_SUBSCRIPTION_NAME")

# Create a client
client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))


async def run():
    async with client:
        # Publish a CloudEvent
        try:
            cloud_event = CloudEvent(
                data="HI", source="https://example.com", type="example"
            )
            await client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event)
        except HttpResponseError:
            raise

        # Publish a list of CloudEvents
        try:
            list_of_cloud_events = [cloud_event, cloud_event]
            await client.publish_cloud_events(
                topic_name=TOPIC_NAME, body=list_of_cloud_events
            )
        except HttpResponseError:
            raise


if __name__ == "__main__":
    asyncio.run(run())
