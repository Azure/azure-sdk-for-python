import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridNamespaceClient
from azure.eventgrid.models import *
from azure.core.exceptions import HttpResponseError

# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridNamespaceClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))

async def run():
    # Release a LockToken
    try: 
        tokens = [LockToken({'lockToken': 'token'})]
        release = await client.release_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, tokens=tokens)
        print(release)
    except HttpResponseError:
        raise


asyncio.run(run())