# Sync EventGrid Client Examples:



```
import os
from azure.core.credentials import AzureKeyCredential
from azure.messaging.eventgridmessaging import EventGridMessagingClient
from azure.messaging.eventgridmessaging.models import *
from azure.core.messaging import CloudEvent


# Create a client
EG_KEY = os.environ.get("EG_KEY")
EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
ES_NAME = os.environ.get("ES_NAME")

client = EventGridMessagingClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))


# Publish a CloudEvent
try:
    cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
    client.publish(topic_name=TOPIC_NAME, body=cloud_event)
except Exception as e:
    print(e)

# Publish a list of CloudEvents
try:
    list_of_cloud_events = [cloud_event, cloud_event]
    client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
except Exception as e:
    print(e)


# Receive CloudEvents
try:
    receive_response = client.receive(topic_name=TOPIC_NAME,event_subscription_name=ES_NAME,max_events=10,timeout=10)
    print(receive_response)
except Exception as e:
    print(e)

# Release a LockToken
try: 
    tokens = [LockToken({'lockToken': 'token'})]
    release = client.release_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, tokens=tokens)
    print(release)
except Exception as e:
    print(e)

# Acknowledge a batch of CloudEvents
try: 
    lock_tokens = LockTokenInput(lock_tokens=["token"])
    ack = client.acknowledge_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, lock_tokens=lock_tokens)
    print(ack)
except Exception as e:
    print(e)
```