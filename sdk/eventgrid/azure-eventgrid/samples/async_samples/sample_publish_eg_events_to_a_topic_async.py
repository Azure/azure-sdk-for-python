# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_eg_events_to_a_topic_async.py
DESCRIPTION:
    These samples demonstrate sending an EventGrid Event directly to a topic.
USAGE:
    python sample_publish_eg_events_to_a_topic_async.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_TOPIC_KEY - The access key of your eventgrid account.
    2) EVENTGRID_TOPIC_ENDPOINT - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
# [START publish_eg_event_to_topic_async]
import os
import asyncio
from azure.eventgrid import EventGridEvent
from azure.eventgrid.aio import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EVENTGRID_TOPIC_KEY"]
endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]

async def publish():
    credential = AzureKeyCredential(topic_key)
    client = EventGridPublisherClient(endpoint, credential)

    await client.send([
        EventGridEvent(
            event_type="Contoso.Items.ItemReceived",
            data={
                "itemSku": "Contoso Item SKU #1"
            },
            subject="Door1",
            data_version="2.0"
        )
    ])
# [END publish_eg_event_to_topic_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish())
