import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridNamespaceClient
from azure.eventgrid.models import *


# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridNamespaceClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))

async def run():
    # Acknowledge a batch of CloudEvents
    try: 
        lock_tokens = LockTokenInput(lock_tokens=["token"])
        ack = await client.acknowledge_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, lock_tokens=lock_tokens)
        print(ack)
    except Exception as e:
        print(e)


asyncio.run(run())