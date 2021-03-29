# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_eg_events_to_a_domain_async.py
DESCRIPTION:
    These samples demonstrate creating a list of EventGrid Events and sending them as a list to a topic
    in a domain.
USAGE:
    python sample_publish_eg_events_to_a_domain_async.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
import asyncio
from azure.eventgrid import EventGridEvent
from azure.eventgrid.aio import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

domain_key = os.environ["EG_DOMAIN_ACCESS_KEY"]
domain_hostname = os.environ["EG_DOMAIN_TOPIC_HOSTNAME"]

async def publish():
    credential = AzureKeyCredential(domain_key)
    client = EventGridPublisherClient(domain_hostname, credential)

    await client.send([
        EventGridEvent(
            topic="MyCustomDomainTopic1",
            event_type="Contoso.Items.ItemReceived",
            data={
                "itemSku": "Contoso Item SKU #1"
            },
            subject="Door1",
            data_version="2.0"
        ),
        EventGridEvent(
            topic="MyCustomDomainTopic2",
            event_type="Contoso.Items.ItemReceived",
            data={
                "itemSku": "Contoso Item SKU #2"
            },
            subject="Door1",
            data_version="2.0"
        )
    ])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish())
