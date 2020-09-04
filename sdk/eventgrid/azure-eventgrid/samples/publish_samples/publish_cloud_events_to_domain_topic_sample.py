# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: publish_cloud_events_to_domain_topic_sample.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and sending them as a list
    to a domain topic.
USAGE:
    python publish_cloud_events_to_domain_topic_sample.py
    Set the environment variables with your own values before running the sample:
    1) DOMAIN_ACCESS_KEY - The access key of your eventgrid account.
    2) DOMAIN_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
    3) DOMAIN_NAME - the name of the topic
"""
import sys
import os
from random import randint, sample
import time

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent

domain_key = os.environ["DOMAIN_ACCESS_KEY"]
domain_topic_hostname = os.environ["DOMAIN_TOPIC_HOSTNAME"]
domain_name = os.environ["DOMAIN_NAME"]


# authenticate client
credential = AzureKeyCredential(domain_key)
client = EventGridPublisherClient(domain_topic_hostname, credential)

def publish_event():
    # publish events
    for _ in range(10):

        event_list = []     # list of events to publish
        team_members = ["Josh", "Kerri", "Kieran", "Laurent", "Lily", "Matt", "Soren", "Srikanta", "Swathi"]    # possible values for data field

        # create events and append to list
        for j in range(randint(1, 3)):
            sample_members = sample(team_members, k=randint(1, 9))      # select random subset of team members
            event = CloudEvent(
                    type="Azure.Sdk.Demo",
                    source=domain_name,
                    data={"team": sample_members}
                    )
            event_list.append(event)

        # publish list of events
        client.send(event_list)
        print("Batch of size {} published".format(len(event_list)))
        time.sleep(randint(1, 5))

if __name__ == '__main__':
    publish_event()
