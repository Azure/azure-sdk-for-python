# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_custom_schema_to_a_topic.py
DESCRIPTION:
    These samples demonstrate creating a list of Custom Events and sending them as a list.
USAGE:
    python sample_publish_custom_schema_to_a_topic.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_CUSTOM_EVENT_TOPIC_KEY - The access key of your eventgrid account.
    2) EVENTGRID_CUSTOM_EVENT_TOPIC_ENDPOINT - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
from random import randint
import time
import uuid
from msrest.serialization import UTC
import datetime as dt

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient

key = os.environ["EVENTGRID_CUSTOM_EVENT_TOPIC_KEY"]
endpoint = os.environ["EVENTGRID_CUSTOM_EVENT_TOPIC_ENDPOINT"]

def publish_event():
    # authenticate client
    credential = AzureKeyCredential(key)
    client = EventGridPublisherClient(endpoint, credential)

    # [START publish_custom_schema]
    custom_schema_event = {
        "customSubject": "sample",
        "customEventType": "sample.event",
        "customDataVersion": "2.0",
        "customId": uuid.uuid4(),
        "customEventTime": dt.datetime.now(UTC()).isoformat(),
        "customData": "sample data"
    }

    client.send(custom_schema_event)
    # [END publish_custom_schema]

if __name__ == '__main__':
    publish_event()
