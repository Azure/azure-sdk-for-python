from azure.eventgrid import AzureMessagingEventGridClient
from azure.eventgrid.models import *
from azure.core.credentials import AzureKeyCredential

ENDPOINT = "https://{my_endpoint_here}.centraluseuap-1.eventgrid.azure.net"
KEY = "key"
credential = AzureKeyCredential(KEY)
topic = "my_topic_here"
es = "my_event_subscription_here"

client = AzureMessagingEventGridClient(endpoint=ENDPOINT, credential=credential)


# PUBLISH

try:
    publish = client.publish_cloud_event(topic_name=topic, event=CloudEvent(id="1", source="test", type="test", data="test", specversion="1.0"))
    print("PUBLISH")
    print(publish)
except Exception as e:
    print("PUBLISH")
    print(e)

# PUBLISH BATCH
try:
    publish_batch = client.publish_batch_of_cloud_events(topic_name=topic, events=[CloudEvent(id="1", source="test", type="test", data="test", specversion="1.0")])
    print("PUBLISH BATCH")
    print(publish_batch)
except Exception as e:
    print("PUBLISH BATCH")
    print(e)


# RECEIVE
try:
    receive = client.receive_batch_of_cloud_events(topic_name=topic, event_subscription_name=es)
    # receive = client.receive_batch_of_cloud_events(topic_name=topic, subscription_name=es, max_events=10, timeout=10)
    print("RECEIVE")
    print(receive)
except Exception as e:
    print("RECEIVE")
    print(e)

# ACKNOWLEDGE
try: 
    lock_tokens = LockTokenInput(lock_tokens=["token"])
    ack = client.acknowledge_batch_of_cloud_events(topic_name=topic, event_subscription_name=es, lock_tokens=lock_tokens)
    print("ACKNOWLEDGE")
    print(ack)
except Exception as e:
    print("ACKNOWLEDGE")
    print(e)


# RELEASE
try: 
    tokens = [LockToken({'lockToken': 'token'})]
    ack = client.release_batch_of_cloud_events(topic_name=topic, event_subscription_name=es, tokens=tokens)
    print("RELEASE")
    print(ack)
except Exception as e:
    print("RELEASE")
    print(e)