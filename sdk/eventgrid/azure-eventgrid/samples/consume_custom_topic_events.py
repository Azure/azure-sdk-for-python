import sys
import os
import datetime as dt
import json

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from msrestazure.azure_active_directory import ServicePrincipalCredentials
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import EventSubscription
from src.generated_client import GeneratedClient
from src.generated_client.models import EventGridEvent, CloudEvent
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

STORAGE_BLOB_CREATED_EVENT = "Microsoft.Storage.BlobCreated"
SUBSCRIPTION_VALIDATION_EVENT = "Microsoft.EventGrid.SubscriptionValidationEvent"
AZURE_SUBSCRIPTION_ID = "faa080af-c1d8-40ad-9cce-e1a450ca5b57"
RESOURCE_GROUP_NAME = "t-swpill-test"
TOPIC_NAME = "eventgridcloudeventsub"
REQUEST_BIN_URL = 'https://eventgridgrideventsviewer.azurewebsites.net/'

client_id = os.environ.get('AZURE_CLIENT_ID')
tenant_id = os.environ.get('AZURE_TENANT_ID')
secret = os.environ.get('AZURE_CLIENT_SECRET')
credentials = ServicePrincipalCredentials(tenant=tenant_id, client_id=client_id, secret=secret)
sample_mgmt_client = EventGridManagementClient(credentials, AZURE_SUBSCRIPTION_ID)

#scope = '/subscriptions/'+AZURE_SUBSCRIPTION_ID+'/resourceGroups/'+RESOURCE_GROUP_NAME+'/providers/Microsoft.EventGrid/topics/'+TOPIC_NAME
#event_sub_name = 'eventgridegsub'
response = sample_mgmt_client.topics.get('t-swpill-test', TOPIC_NAME)
#response = sample_mgmt_client.event_subscriptions.list_global_by_resource_group("t-swpill-test") #create_or_update(scope, event_sub_name, { 'destination': {'endpoint_url': REQUEST_BIN_URL, 'endpoint_type': 'WebHook'}})
print(response)

def create_event_subscription():
    event_sub = EventSubscription()



#def create_custom_topic():
#    custom_topic_name = 'eventgridviewercustomtopicevents'
#
#def deserialize_events_string():
#    # stub postreqdata
#    req = [
#    {
#    "id": "b85d631a-101e-005a-02f2-cee7aa06f148",
#    "source": "/subscriptions/{subscription_id}/resourceGroup/{resource_group}/Microsoft.Storage/storageAccounts/{storage_account}",
#    "data": {
#        "api": "PutBlockList"
#    },
#    "type": "Microsoft.Storage.BlobCreated",
#    "time": "2020-09-14T10:00:00Z",
#    "specversion": "1.0",
#    "subject": "blobServices/default/containers/{storage-container}/blobs/{new-file}"
#    },
#    {
#    "id": "b85d631a-101e-005a-02f2-cee7aa06f149",
#    "source": "/subscriptions/{subscription_id}/resourceGroup/{resource_group}/Microsoft.Storage/storageAccounts/{storage_account}",
#    "data": { 
#        "api": "PutBlockList"
#    },
#    "type": "Microsoft.Storage.BlobCreated",
#    "time": "2020-09-14T10:00:00Z",
#    "specversion": "1.0",
#    "subject": "blobServices/default/containers/{storage-container}/blobs/{new-file}"
#    }]
#
#    jsonstr = json.dumps(req)
#    postreqdata = json.loads(jsonstr)
#    for event in postreqdata:
#        event_data = event['data']
#        print(event_data['api'])
#        if event['type'] == STORAGE_BLOB_CREATED_EVENT:
#            print("Got BlobCreated event data, blob API: {}".format(event_data['api']))
#        elif event['type'] == SUBSCRIPTION_VALIDATION_EVENT:
#            validation_code = event_data['validation_code']
#            validation_url = event_data['validation_url']
#            print("Got SubscriptionValidation event data, validation code is: {}".format(
#                validation_code,
#                validation_url
#            ))
#            response_payload = {
#                "validationResponse": validation_code
#            }
#            response = json.dumps(response_payload)
#
#deserialize_events_string()