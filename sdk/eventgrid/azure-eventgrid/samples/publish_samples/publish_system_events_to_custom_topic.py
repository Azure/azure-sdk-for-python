import sys
import os
import json
from random import randint, sample
from typing import Sequence
import time

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from azure.core.credentials import AzureKeyCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.eventgrid._publisher_client import EventGridPublisherClient
from azure.eventgrid._models import EventGridEvent, CloudEvent
from azure.eventgrid._generated.event_grid_publisher_client.models._models import StorageBlobCreatedEventData
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

import logging

#logging.basicConfig(level=logging.DEBUG)

key = os.environ.get("CUSTOM_ACCESS_KEY")
topic_hostname = "eventgridcloudeventsub.eastus-1.eventgrid.azure.net"

# authenticate client
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)#, logging_enable=True)

data_obj = StorageBlobCreatedEventData(
    api="PutBlockList",
    client_request_id="6d79dbfb-0e37-4fc4-981f-442c9ca65760",
    request_id="831e1650-001e-001b-66ab-eeb76e000000",
    e_tag="0x8D4BCC2E4835CD0",
    content_type="application/octet-stream",
    content_length=524288,
    blob_type="BlockBlob",
    url="https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
    sequencer="00000000000004420000000000028963",
    storage_diagnostics={
        "batchId": "b68529f3-68cd-4744-baa4-3c0498ec19f0"
        }
)

data_dict = {
    "api":"PutBlockList",
    "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
    "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
    "e_tag":"0x8D4BCC2E4835CD0",
    "content_type":"application/octet-stream",
    "content_length":524288,
    "blob_type":"BlockBlob",
    "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
    "sequencer":"00000000000004420000000000028963",
    "storage_diagnostics":{
        "batchId": "b68529f3-68cd-4744-baa4-3c0498ec19f0"
        }
}

# publish events
for i in range(3):

    event_list = []     # list of events to publish
    # create events and append to list
    for j in range(randint(10, 10)):
        event = CloudEvent(
                type="Microsoft.Storage.BlobCreated",
                source="https://egdemo.dev/demoevent",
                data=data_dict
                )
        event_list.append(event)

    # publish list of events
    client.send(event_list)
    print("Batch of size {} published".format(len(event_list)))
    time.sleep(randint(1, 5))
