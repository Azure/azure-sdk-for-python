# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_event_grid_events_to_custom_topic_async_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of Eventgrid Events and sending them as a list
    to custom topic asynchronously.
USAGE:
    python publish_event_grid_events_to_custom_topic_async_sample.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
import asyncio
from random import randint, sample
import time

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import EventGridEvent

async def publish_event():
    key = os.environ["EG_ACCESS_KEY"]
    topic_hostname = os.environ["EG_TOPIC_HOSTNAME"]

    # authenticate client
    credential = AzureKeyCredential(key)
    client = EventGridPublisherClient(topic_hostname, credential)

    azure_messaging_services = ["Event Grid", "Event Hubs", "Service Bus"]   # possible values for data field

    # publish events
    for _ in range(3):

        event_list = []     # list of events to publish
        # create events and append to list
        for j in range(randint(1, 3)):
            sample_services = sample(azure_messaging_services, k=randint(1, 3)) # select random subset of team members
            event = EventGridEvent(
                    subject="Door1",
                    data={"messaging_services": sample_services},
                    event_type="Azure.Sdk.Demo",
                    data_version="2.0"
                    )
            event_list.append(event)

        # publish list of events
        await client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish_event())
