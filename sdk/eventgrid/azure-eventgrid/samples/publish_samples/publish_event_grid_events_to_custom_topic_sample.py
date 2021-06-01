# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_event_grid_events_to_custom_topic_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of Eventgrid Events and sending them as a list
    to custom topic.
USAGE:
    python publish_event_grid_events_to_custom_topic_sample.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
from random import randint, sample
import time

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent

key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)
services = ["EventGrid", "ServiceBus", "EventHubs", "Storage"]    # possible values for data field

def publish_event():
    # publish events
    for _ in range(3):

        event_list = []     # list of events to publish
        # create events and append to list
        for j in range(randint(1, 3)):
            sample_members = sample(services, k=randint(1, 4))      # select random subset of team members
            event = EventGridEvent(
                    subject="Door1",
                    data={"team": sample_members},
                    event_type="Azure.Sdk.Demo",
                    data_version="2.0"
                    )
            event_list.append(event)

        # publish list of events
        client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))

if __name__ == '__main__':
    publish_event()
