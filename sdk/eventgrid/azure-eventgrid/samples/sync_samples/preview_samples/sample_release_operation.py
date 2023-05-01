import os
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import *
from azure.core.exceptions import HttpResponseError

# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))

# Release a LockToken
try:
    lock_tokens = ReleaseOptions(lock_tokens=["token"])
    release = client.release_cloud_events(
        topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, lock_tokens=lock_tokens
    )
    print(release)
except HttpResponseError:
    raise
