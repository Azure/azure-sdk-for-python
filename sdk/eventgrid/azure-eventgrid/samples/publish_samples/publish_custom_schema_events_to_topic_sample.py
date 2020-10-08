# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_custom_schema_events_to_topic_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of Custom Events and sending them as a list.
USAGE:
    python publish_custom_schema_events_to_topic_sample.py
    Set the environment variables with your own values before running the sample:
    1) CUSTOM_SCHEMA_ACCESS_KEY - The access key of your eventgrid account.
    2) CUSTOM_SCHEMA_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
from random import randint, sample
import time
import uuid
from msrest.serialization import UTC
import datetime as dt

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CustomEvent

key = os.environ["CUSTOM_SCHEMA_ACCESS_KEY"]
topic_hostname = os.environ["CUSTOM_SCHEMA_TOPIC_HOSTNAME"]

def publish_event():
    # authenticate client
    credential = AzureKeyCredential(key)
    client = EventGridPublisherClient(topic_hostname, credential)

    custom_schema_event = {
        "customSubject": "sample",
        "customEventType": "sample.event",
        "customDataVersion": "2.0",
        "customId": uuid.uuid4(),
        "customEventTime": dt.datetime.now(UTC()).isoformat(),
        "customData": "sample data"
    }

    # publish events
    for _  in range(10):

        event_list = []     # list of events to publish
        # create events and append to list
        for j in range(randint(1, 3)):
            event = CustomEvent(custom_schema_event)
            event_list.append(event)

        # publish list of events
        client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))


if __name__ == '__main__':
    publish_event()
