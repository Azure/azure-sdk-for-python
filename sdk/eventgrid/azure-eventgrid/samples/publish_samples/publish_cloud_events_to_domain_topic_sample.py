import sys
import os
import json
from random import randint, sample
import time

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient
from azure.eventgrid import EventGridEvent, CloudEvent
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

key = os.environ.get("DOMAIN_ACCESS_KEY")
topic_hostname = "t-swpill-domain.eastus-1.eventgrid.azure.net"

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)

# publish events
while True:

    event_list = []     # list of events to publish
    team_members = ["Josh", "Kerri", "Kieran", "Laurent", "Lily", "Matt", "Soren", "Srikanta", "Swathi"]    # possible values for data field

    # create events and append to list
    for j in range(randint(1, 3)):
        sample_members = sample(team_members, k=randint(1, 9))      # select random subset of team members
        event = CloudEvent(
                type="Azure.Sdk.Demo",
                source="t-swpill-domain",
                data={"team": sample_members}
                )
        event_list.append(event)

    # publish list of events
    client.send(event_list)
    print("Batch of size {} published".format(len(event_list)))
    time.sleep(randint(1, 5))
