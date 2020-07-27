import sys
import os
import datetime as dt
from random import randint
import time
import exrex

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.generated_client import GeneratedClient
from azure.generated_client.models import EventGridEvent, CloudEvent
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

cloud_hostname = "eventgridcloudeventsub.eastus-1.eventgrid.azure.net/"
eg_hostname = "eventgridegeventsub.eastus-1.eventgrid.azure.net/"

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
    if type(events[0]) == EventGridEvent:
        sample_client.publish_events(hostname, events)
    else:
        response = sample_client.publish_cloud_event_events(hostname, events)
        print(response)


dtime = dt.datetime.now().strftime("%m-%d-%YT%I:%M:%S.%f")
# send EG event
#eg_event = EventGridEvent(id='831e1650-001e-001b-66ab-eeb76e06l631', subject="/blobServices/default/containers/oc2d2817345i200097container/blobs/oc2d2817345i20002296blob", data="\{\}", event_type='recordInserted', event_time=dtime, data_version="1.0")
#eg_events = [eg_event]
#key_authentication(eg_events, eg_key, eg_hostname)
akc_credential = AzureKeyCredential(cloud_key)
akc_policy = get_authentication_policy(akc_credential)
sample_client = GeneratedClient(authentication_policy=akc_policy)

# read events from json file pattern
with open(os.path.dirname(__file__) + CLOUD_EVENTS_FILE_PATH) as json_file:
    cloud_events_dict = json.load(json_file)
        events = []
        i = 1
        for event in source:
            events.append(CloudEvent(**event))
#cloud_events = CloudEvent.from_dict(cloud_events_dict)


for i in range(5):

    # generate random # of random events
    event_batch = []
    for j in range(randint(1, 2)):
        unique_id = exrex.getone('[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}')
        event = CloudEvent(
                specversion="1.0", \
                id=unique_id, \
                type="Azure.Sdk.Demo", \
                source="https://egdemo.dev/demoevent", \
                data="{ \"team\": [\"Matt\", \"Josh\", \"Laurent\", \"Lily\", \"Srikanta\", \"Kieran\", \"Kerri\", \"Soren\", \"Swathi\"] }"
                )
        event_batch.append(event)

    # publish and receive response
    response = sample_client.publish_cloud_event_events(cloud_hostname, event_batch)
    print("batch of size {} sent".format(len(event_batch)))
    time.sleep(randint(1, 5))

# send cloud event
#cloud_event = CloudEvent(specversion="1.0", id="b85d631a-101e-005a-02f2-cee7aa06f148", type="zohan.music.request", source="https://swath1.dev/music/", subject="zohan/music/requests/4322", time="2020-09-14T10:00:00Z", data="{ \"artist\": \"Gerardo\", \"song\": \"Rico Suave\" }")
#cloud_event2 = CloudEvent(specversion="1.0", id="b85d631a-101e-005a-02f2-cee7aa06f149", type="zohan.music.request", source="https://swath2.dev/music/", subject="zohan/music/requests/4322", time="2020-09-14T10:00:00Z", data="{ \"artist\": \"Gerardo\", \"song\": \"Rico Suave\" }")
#cloud_events = [cloud_event, cloud_event2]
