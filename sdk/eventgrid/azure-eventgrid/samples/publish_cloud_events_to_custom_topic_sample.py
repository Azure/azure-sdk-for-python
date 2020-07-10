import sys
import os
import datetime as dt
import json
from random import randint, sample
import time
import uuid

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.eventgrid._publisher_client import EventGridPublisherClient
from azure.eventgrid._models import EventGridEvent, CloudEvent
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

key = os.environ.get("DEMO_ACCESS_KEY")
topic_hostname = "eg-azure-sdk-demo.westus2-1.eventgrid.azure.net"

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)

# publish events
while True:

    # generate random # of events
    event_list = []
    team_members = ["Josh", "Kerri", "Kieran", "Laurent", "Lily", "Matt", "Soren", "Srikanta", "Swathi"]
    for j in range(randint(1, 3)):
        event_uuid = uuid.uuid4()
        sample_members = sample(team_members, k=randint(1, 9))
        event = CloudEvent(
                specversion="1.0",
                id=event_uuid,
                type="Azure.Sdk.Demo",
                source="https://egdemo.dev/demoevent",
                data={"team": sample_members}
                )
        event_list.append(event)

    # publish and receive response
    response = client.publish_events(event_list)
    print("Batch of size {} published".format(len(event_list)))
    time.sleep(randint(1, 5))
