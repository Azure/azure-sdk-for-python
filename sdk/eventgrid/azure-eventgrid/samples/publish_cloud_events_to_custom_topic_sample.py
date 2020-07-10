import sys
import os
import datetime as dt
import json
from random import randint
import time
import exrex

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

CLOUD_EVENTS_FILE_PATH = "\\..\\example_json\\cloud_custom_topic.json"

key = os.environ.get("DEMO_ACCESS_KEY")
topic_hostname = "eg-azure-sdk-demo.westus2-1.eventgrid.azure.net"

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)

# publish events
for i in range(5):

    # generate random # of events
    event_batch = []
    for j in range(randint(1, 3)):
        unique_id = exrex.getone('[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}')
        event = CloudEvent(
                specversion="1.0", \
                id=unique_id, \
                type="Azure.Sdk.Demo", \
                source="https://egdemo.dev/demoevent", \
                data="{ \"team\": [\"Josh\", \"Kerri\", \"Kieran\", \"Laurent\", \"Lily\", \"Matt\", \"Soren\", \"Srikanta\", \"Swathi\"] }"
                )
        event_batch.append(event)

    # publish and receive response
    response = client.publish_event_batch(event_batch)
    time.sleep(randint(1, 5))
