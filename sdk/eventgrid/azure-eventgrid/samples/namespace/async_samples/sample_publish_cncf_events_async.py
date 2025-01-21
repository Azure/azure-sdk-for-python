# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_cncf_events_async.py
DESCRIPTION:
    This sample demonstrates creating sending a cloud event from the CNCF library.
USAGE:
    python sample_publish_cncf_events_async.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_KEY - The access key of your eventgrid account.
    2) EVENTGRID_ENDPOINT - The namespace hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
    3) EVENTGRID_TOPIC_NAME - The namespace topic name.
"""
import os
import asyncio
from azure.eventgrid.aio import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential
from cloudevents.http import CloudEvent

topic_key = os.environ["EVENTGRID_KEY"]
endpoint = os.environ["EVENTGRID_ENDPOINT"]
topic_name = os.environ["EVENTGRID_TOPIC_NAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential, namespace_topic=topic_name)


async def publish():
    async with client:
        await client.send(
            [
                CloudEvent(
                    attributes={
                        "type": "cloudevent",
                        "source": "/cncf/cloud/event/1.0",
                        "subject": "testing-cncf-event",
                    },
                    data=b"This is a cncf cloud event.",
                )
            ]
        )


if __name__ == "__main__":
    asyncio.run(publish())
