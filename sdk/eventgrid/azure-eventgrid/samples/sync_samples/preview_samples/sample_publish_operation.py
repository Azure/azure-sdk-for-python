import os
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))


# Publish a CloudEvent
try:
    cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event)
except HttpResponseError:
    raise

# Publish a list of CloudEvents
try:
    list_of_cloud_events = [cloud_event, cloud_event]
    client.publish_cloud_events(topic_name=TOPIC_NAME, body=list_of_cloud_events)
except HttpResponseError:
    raise
