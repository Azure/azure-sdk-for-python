# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs5_publish_events_using_cloud_events_1.0_schema_async.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and sending them as a list asynchronously.
USAGE:
    python cs5_publish_events_using_cloud_events_1.0_schema_async.py
    Set the environment variables with your own values before running the sample:
    1) CLOUD_ACCESS_KEY - The access key of your eventgrid account.
    2) CLOUD_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
import asyncio

from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import EventGridEvent, CloudEvent
from azure.core.credentials import AzureKeyCredential

async def publish():
    topic_key = os.environ["CLOUD_ACCESS_KEY"]
    topic_hostname = os.environ["CLOUD_TOPIC_HOSTNAME"]

    credential = AzureKeyCredential(topic_key)
    client = EventGridPublisherClient(topic_hostname, credential)

    await client.send([
        CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="/contoso/items",
            data={
                "itemSku": "Contoso Item SKU #1"
            },
            subject="Door1"
        )
    ])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish())
