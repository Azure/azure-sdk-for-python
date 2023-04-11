import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.messaging.eventgridmessaging.aio import EventGridMessagingClient
from azure.messaging.eventgridmessaging.models import *
from azure.core.messaging import CloudEvent



# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridMessagingClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))

async def run():
    # Publish a CloudEvent
    try:
        cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
        await client.publish(topic_name=TOPIC_NAME, body=cloud_event)
    except Exception as e:
        print(e)

    # Publish a list of CloudEvents
    try:
        list_of_cloud_events = [cloud_event, cloud_event]
        await client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
    except Exception as e:
        print(e)


asyncio.run(run())