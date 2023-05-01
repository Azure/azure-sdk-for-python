import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid.aio import EventGridClient
from azure.eventgrid.models import *
from azure.core.exceptions import HttpResponseError

# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))


async def run():
    # Receive CloudEvents
    try:
        async with client:
            receive_response = await client.receive_cloud_events(
                topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, max_events=10, max_wait_time=10
            )
            print(receive_response)
    except HttpResponseError:
        raise

if __name__ == '__main__':
    asyncio.run(run())
