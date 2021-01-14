# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_with_shared_access_signature_async_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and publish them
    using the shared access signature for authentication asynchronously.
USAGE:
    python publish_with_shared_access_signature_async_sample.py
    Set the environment variables with your own values before running the sample:
    1) CLOUD_ACCESS_KEY - The access key of your eventgrid account.
    2) CLOUD_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
import asyncio
from random import randint, sample
import time

from datetime import datetime, timedelta

from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import CloudEvent, generate_shared_access_signature, EventGridSharedAccessSignatureCredential

async def publish_event():
    key = os.environ["CLOUD_ACCESS_KEY"]
    topic_hostname = os.environ["CLOUD_TOPIC_HOSTNAME"]
    expiration_date_utc = datetime.utcnow() + timedelta(hours=1)

    signature = generate_shared_access_signature(topic_hostname, key, expiration_date_utc)

    # authenticate client
    credential = EventGridSharedAccessSignatureCredential(signature)
    client = EventGridPublisherClient(topic_hostname, credential)

    azure_messaging_services = ["Event Grid", "Event Hubs", "Service Bus"]   # possible values for data field

    # publish events
    for _ in range(3):
        event_list = []     # list of events to publish
        # create events and append to list
        for j in range(randint(1, 3)):
            sample_services = sample(azure_messaging_services, k=randint(1, 3)) # select random subset of team members
            data_dict = {"team": sample_services}
            event = CloudEvent(
                    type="Azure.Sdk.Sample",
                    source="https://egsample.dev/sampleevent",
                    data={"messaging_services": sample_services}
                    )
            event_list.append(event)

        # publish list of events
        await client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish_event())
