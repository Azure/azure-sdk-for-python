# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_cncf_cloud_events.py
DESCRIPTION:
    This sample demonstrates creating sending a cloud event from the CNCF library.
USAGE:
    python sample_publish_cncf_cloud_events.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_CLOUD_EVENT_TOPIC_KEY - The access key of your eventgrid account.
    2) EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential
from cloudevents.http import CloudEvent

topic_key = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_KEY"]
endpoint = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

client.send([
    CloudEvent(
        attributes={
            "type": "cloudevent",
            "source": "/cncf/cloud/event/1.0",
            "subject": "testingcncfevent"
        },
        data=b'This is a cncf cloud event.',
    )
])
