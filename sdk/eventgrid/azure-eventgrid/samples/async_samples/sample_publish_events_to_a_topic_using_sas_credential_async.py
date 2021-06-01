# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_events_to_a_topic_using_sas_credential_async.py
DESCRIPTION:
    These samples demonstrate sending an EventGrid Event using a shared access signature for authentication.
USAGE:
    python sample_publish_events_to_a_topic_using_sas_credential_async.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_SAS - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
import asyncio
from azure.eventgrid import EventGridEvent
from azure.eventgrid.aio import EventGridPublisherClient
from azure.core.credentials import AzureSasCredential

sas = os.environ["EVENTGRID_SAS"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

async def publish():
    credential = AzureSasCredential(sas)
    client = EventGridPublisherClient(endpoint, credential)

    async with client:
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

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish())
