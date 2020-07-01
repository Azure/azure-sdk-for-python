import sys
import os
import datetime as dt
import json

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from src.generated_client import GeneratedClient
from src.generated_client.models import EventGridEvent, CloudEvent
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

cloud_hostname = "eventgridcloudeventsub.eastus-1.eventgrid.azure.net/"
eg_hostname = "eventgridegeventsub.eastus-1.eventgrid.azure.net/"
dtime = dt.datetime.now().strftime("%m-%d-%YT%I:%M:%S.%f")

EVENTGRID_KEY_HEADER = 'aeg-sas-key'
cloud_key = '8dQnGCAXpdtLvGAeVzMEcwJEMR1KC60IAA6TqD6Rmbs='
eg_key = ''

def get_authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(credential=credential, name=EVENTGRID_KEY_HEADER)

    return authentication_policy

def key_authentication(events, key, hostname):
    akc_credential = AzureKeyCredential(key)
    akc_policy = get_authentication_policy(akc_credential)
    sample_client = GeneratedClient(authentication_policy=akc_policy)
    if type(events[0]) == EventGridEvent:
        sample_client.publish_events(hostname, events)
    else:
        response = sample_client.publish_cloud_event_events(hostname, events)
        print(response)

def create_event_grid_events():
    eg_event = EventGridEvent(id='831e1650-001e-001b-66ab-eeb76e06l631', subject="/blobServices/default/containers/oc2d2817345i200097container/blobs/oc2d2817345i20002296blob", data="{\"artist\": \"G\"}", event_type='recordInserted', event_time=dtime, data_version="1.0")
    print(type(eg_event.data))
    eg_events = [eg_event]
    return eg_events

def create_cloud_events():
    cloud_event = CloudEvent(specversion="1.0", id="b85d631a-101e-005a-02f2-cee7aa06f148", type="Microsoft.Storage.BlobCreated", source="/subscriptions/{subscription_id}/resourceGroup/{resource_group}/Microsoft.Storage/storageAccounts/{storage_account}", subject="blobServices/default/containers/{storage-container}/blobs/{new-file}", time="2020-09-14T10:00:00Z", data={"api": "PutBlockList"})
    cloud_event2 = CloudEvent(specversion="1.0", id="b85d631a-101e-005a-02f2-cee7aa06f149", type="Microsoft.Storage.BlobCreated", source="/subscriptions/{subscription_id}/resourceGroup/{resource_group}/Microsoft.Storage/storageAccounts/{storage_account}", subject="blobServices/default/containers/{storage-container}/blobs/{new-file}", time="2020-09-14T10:00:00Z", data={"api": "PutBlockList"})
    cloud_events = [cloud_event, cloud_event2]
    return cloud_events

# send cloud event
create_cloud_events()
key_authentication(create_cloud_events(), cloud_key, cloud_hostname)

# send EG event
#create_event_grid_events()


