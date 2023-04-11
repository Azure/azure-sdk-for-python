import os
from azure.messaging.eventgridmessaging import EventGridMessagingClient, EventGridSharedAccessKeyCredential
from azure.messaging.eventgridmessaging.models import *


# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridMessagingClient(EG_ENDPOINT, EventGridSharedAccessKeyCredential(EG_KEY))


# Receive CloudEvents
try:
    receive_response = client.receive(topic_name=TOPIC_NAME,event_subscription_name=ES_NAME,max_events=10,timeout=10)
    print(receive_response)
except Exception as e:
    print(e)
