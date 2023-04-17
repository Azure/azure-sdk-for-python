import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError


# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))

async def run():
    # Publish a CloudEvent
    try:
        cloud_event = CloudEvent(data="HI", source="https://example.com", type="example")
        await client.publish(topic_name=TOPIC_NAME, body=cloud_event)
    except HttpResponseError:
        raise

    # Publish a list of CloudEvents
    try:
        list_of_cloud_events = [cloud_event, cloud_event]
        await client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
    except HttpResponseError:
        raise

asyncio.run(run())