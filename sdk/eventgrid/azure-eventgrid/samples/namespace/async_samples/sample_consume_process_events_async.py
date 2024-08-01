# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_consume_process_events_async.py
DESCRIPTION:
    These samples demonstrate sending, receiving, releasing, and acknowledging CloudEvents.
USAGE:
    python sample_consume_process_events_async.py
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
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError
from azure.eventgrid.aio import EventGridConsumerClient, EventGridPublisherClient

EVENTGRID_KEY: str = os.environ["EVENTGRID_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_EVENT_SUBSCRIPTION_NAME"]


async def run():
    # Create a client
    publisher = EventGridPublisherClient(
        EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY), namespace_topic=TOPIC_NAME
    )
    client = EventGridConsumerClient(
        EVENTGRID_ENDPOINT,
        AzureKeyCredential(EVENTGRID_KEY),
        namespace_topic=TOPIC_NAME,
        subscription=EVENT_SUBSCRIPTION_NAME,
    )

    cloud_event_reject = CloudEvent(data="reject", source="https://example.com", type="example")
    cloud_event_release = CloudEvent(data="release", source="https://example.com", type="example")
    cloud_event_ack = CloudEvent(data="acknowledge", source="https://example.com", type="example")
    cloud_event_renew = CloudEvent(data="renew", source="https://example.com", type="example")

    async with publisher, client:
        # Send Cloud Events
        await publisher.send(
            [
                cloud_event_reject,
                cloud_event_release,
                cloud_event_ack,
                cloud_event_renew,
            ]
        )

        # Receive Published Cloud Events
        try:
            receive_results = await client.receive(
                max_events=10,
                max_wait_time=10,
            )
        except HttpResponseError:
            raise

        # Iterate through the results and collect the lock tokens for events we want to release/acknowledge/reject/renew:

        release_events = []
        acknowledge_events = []
        reject_events = []
        renew_events = []

        for detail in receive_results:
            data = detail.event.data
            broker_properties = detail.broker_properties
            if data == "release":
                release_events.append(broker_properties.lock_token)
            elif data == "acknowledge":
                acknowledge_events.append(broker_properties.lock_token)
            elif data == "renew":
                renew_events.append(broker_properties.lock_token)
            else:
                reject_events.append(broker_properties.lock_token)

        # Release/Acknowledge/Reject/Renew events

        if len(release_events) > 0:
            try:
                release_result = await client.release(
                    lock_tokens=release_events,
                )
            except HttpResponseError:
                raise

            for succeeded_lock_token in release_result.succeeded_lock_tokens:
                print(f"Succeeded Lock Token:{succeeded_lock_token}")

        if len(acknowledge_events) > 0:
            try:
                ack_result = await client.acknowledge(
                    lock_tokens=acknowledge_events,
                )
            except HttpResponseError:
                raise

            for succeeded_lock_token in ack_result.succeeded_lock_tokens:
                print(f"Succeeded Lock Token:{succeeded_lock_token}")

        if len(reject_events) > 0:
            try:
                reject_result = await client.reject(
                    lock_tokens=reject_events,
                )
            except HttpResponseError:
                raise

            for succeeded_lock_token in reject_result.succeeded_lock_tokens:
                print(f"Succeeded Lock Token:{succeeded_lock_token}")

        if len(renew_events) > 0:
            try:
                renew_result = await client.renew_locks(
                    lock_tokens=renew_events,
                )
            except HttpResponseError:
                raise

            for succeeded_lock_token in renew_result.succeeded_lock_tokens:
                print(f"Succeeded Lock Token:{succeeded_lock_token}")


if __name__ == "__main__":
    asyncio.run(run())
