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
            await client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event)

            # Receive CloudEvents and parse out lock tokens
            receive_result = await client.receive_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=10, max_wait_time=10)
            lock_tokens_to_release = []
            for item in receive_result.value:
                lock_tokens_to_release.append(item.broker_properties.lock_token)

            # Renew lock tokens
            lock_tokens = RenewLockOptions(lock_tokens=lock_tokens_to_release)
            renew_events = await client.renew_cloud_event_locks(
                topic_name=TOPIC_NAME,
                event_subscription_name=EVENT_SUBSCRIPTION_NAME,
                renew_lock_options=lock_tokens,
            )
            print("Renewed Event:", renew_events)
        except HttpResponseError:
            raise

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())