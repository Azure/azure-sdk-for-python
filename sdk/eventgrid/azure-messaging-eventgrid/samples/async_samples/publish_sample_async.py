import os
import asyncio
from azure.messaging.eventgridmessaging.aio import EventGridMessagingClient
from azure.messaging.eventgridmessaging import EventGridSharedAccessKeyCredential
from azure.messaging.eventgridmessaging.models import *
from azure.core.messaging import CloudEvent



# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")

client = EventGridMessagingClient(EG_ENDPOINT, EventGridSharedAccessKeyCredential(EG_KEY))


async def run():
    # Publish a CloudEvent
    try:
        cloud_event = CloudEvent(data={"hello": "world"}, source="https://example.com", type="example")
        await client.publish(cloud_event)
    except Exception as e:
        print(e)

    # Publish a list of CloudEvents
    try:
        list_of_cloud_events = [cloud_event, cloud_event]
        await client.publish(list_of_cloud_events)
    except Exception as e:
        print(e)


asyncio.run(run())