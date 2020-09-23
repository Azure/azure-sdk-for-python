# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_cloud_events_to_custom_topic_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and sending them as a list
    to a custom topic.
USAGE:
    python publish_cloud_events_to_custom_topic_sample.py
    Set the environment variables with your own values before running the sample:
    1) CLOUD_ACCESS_KEY - The access key of your eventgrid account.
    2) CLOUD_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
from random import randint, sample
import time

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent

key = os.environ.get("CLOUD_ACCESS_KEY")
topic_hostname = os.environ["CLOUD_TOPIC_HOSTNAME"]

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)

team_members = ["Josh", "Kerri", "Kieran", "Laurent", "Lily", "Matt", "Soren", "Srikanta", "Swathi"]    # possible values for data field

def publish_event():
    # publish events
    for _ in range(10):
        event_list = []     # list of events to publish
        # create events and append to list
        for j in range(randint(1, 1)):
            sample_members = sample(team_members, k=randint(1, 9)) # select random subset of team members
            data_dict = {"team": sample_members}
            event = CloudEvent(
                    type="Azure.Sdk.Sample",
                    source="https://egsample.dev/sampleevent",
                    data={"team": sample_members}
                    )
            event_list.append(event)

        # publish list of events
        client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))

if __name__ == "__main__":
    publish_event()
