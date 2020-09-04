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
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
from random import randint, sample
import time

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent

key = os.environ["EG_ACCESS_KEY"]
topic_hostname = os.environ["EG_TOPIC_HOSTNAME"]

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)

team_members = ["Josh", "Kerri", "Kieran", "Laurent", "Lily", "Matt", "Soren", "Srikanta", "Swathi"]    # possible values for data field

def publish_event():
    # publish events
    while True:

        event_list = []     # list of events to publish
        # create events and append to list
        for j in range(randint(1, 3)):
            sample_members = sample(team_members, k=randint(1, 9))      # select random subset of team members
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
