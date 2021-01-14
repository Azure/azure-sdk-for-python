# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_cloud_events_to_domain_topic_async_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and sending them as a list
    to a domain topic asynchronously.
USAGE:
    python publish_cloud_events_to_domain_topic_async_sample.py
    Set the environment variables with your own values before running the sample:
    1) DOMAIN_ACCESS_KEY - The access key of your eventgrid account.
    2) DOMAIN_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
    3) DOMAIN_NAME - the name of the topic
"""
import os
import asyncio
from random import randint, sample
import time

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import CloudEvent

async def publish_event():
    domain_key = os.environ["DOMAIN_ACCESS_KEY"]
    domain_topic_hostname = os.environ["DOMAIN_TOPIC_HOSTNAME"]
    domain_name = os.environ["DOMAIN_NAME"]

    # authenticate client
    credential = AzureKeyCredential(domain_key)
    client = EventGridPublisherClient(domain_topic_hostname, credential)

    # publish events
    for _ in range(3):

        event_list = []     # list of events to publish
        azure_messaging_services = ["Event Grid", "Event Hubs", "Service Bus"]   # possible values for data field

        # create events and append to list
        for j in range(randint(1, 3)):
            sample_services = sample(azure_messaging_services, k=randint(1, 3))      # select random subset of team members
            event = CloudEvent(
                    type="Azure.Sdk.Demo",
                    source=domain_name,
                    data={"messaging_services": sample_services}
                    )
            event_list.append(event)

        # publish list of events
        await client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish_event())
