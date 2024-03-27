import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridClient, EventGridEvent, ClientLevel, EventGridPublisherClient


# Cloud Event Topic
EVENTGRID_KEY_GA_CLOUDEVENT: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_KEY"]
EVENTGRID_ENDPOINT_GA_CLOUDEVENT: str = os.environ[
    "EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT"
]

# EventGridEvent Topic
EVENTGRID_KEY_GA_EVENTGRIDEVENT: str = os.environ["EVENTGRID_TOPIC_KEY"]
EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT: str = os.environ["EVENTGRID_TOPIC_ENDPOINT"]

# EventGrid Partner Namespace
EVENTGRID_GA_PARTNER_KEY = os.environ["EVENTGRID_PARTNER_NAMESPACE_TOPIC_KEY"]
EVENTGRID_GA_PARTNER_ENDPOINT = os.environ["EVENTGRID_PARTNER_NAMESPACE_TOPIC_ENDPOINT"]
CHANNEL_NAME = os.environ["EVENTGRID_PARTNER_CHANNEL_NAME"]

# EventGrid Namespace
EVENTGRID_KEY: str = os.environ["EVENTGRID_NAMESPACE_KEY"]
EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_NAMESPACES_ENDPOINT"]
TOPIC_NAME: str = os.environ["EVENTGRID_NAMESPACE_TOPIC_NAME"]
EVENT_SUBSCRIPTION_NAME: str = os.environ["EVENTGRID_NAMESPACE_SUBSCRIPTION_NAME"]


# Make the events
cloud_event = CloudEvent(
    data=json.dumps({"hello": "data"}).encode("utf-8"),
    source="https://example.com",
    type="example",
    datacontenttype="application/json",
)
cloud_event_dict = {
    "type": "Contoso.Items.ItemReceived",
    "source": "/contoso/items",
    "data": {"itemSku": "Contoso Item SKU #1"},
    "subject": "Door1",
    "specversion": "1.0",
    "id": "randomclouduuid11",
}
list_cloud_event = [cloud_event, cloud_event]
list_cloud_event_dict = [cloud_event_dict, cloud_event_dict]
eventgrid_event = EventGridEvent(
    event_type="Contoso.Items.ItemReceived",
    data="hello",
    subject="Door1",
    data_version="2.0",
    id="randomeventgriduuid11",
)
eventgrid_event_dict = {
    "eventType": "Contoso.Items.ItemReceived",
    "data": {"itemSku": "Contoso Item SKU #1"},
    "subject": "Door1",
    "dataVersion": "2.0",
    "id": "randomeventgriduuid11",
    "eventTime": "2021-01-20T00:00:00.000000Z",
}
list_eventgrid_event = [eventgrid_event, eventgrid_event]
list_eventgrid_event_dict = [eventgrid_event_dict, eventgrid_event_dict]

broken_eventgrid_event = {
    "data": {"itemSku": "Contoso Item SKU #1"},
    "subject": "Door1",
    "dataVersion": "2.0",
    "id": "randomeventgriduuid11",
}
broken_cloud_event = {
    "type": "Contoso.Items.ItemReceived",
    "subject": "Door1",
    "specversion": "1.0",
    "id": "randomclouduuid11",
}

try:
    # Get resource not found error because wrong endpoint for basic client
    credential = AzureKeyCredential(EVENTGRID_KEY)
    client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential, level=ClientLevel.BASIC)
    client.send(cloud_event_dict)
except Exception as e:
    print(f"Basic Client Created with wrong endpoint: {e} \n \n")

try:
    # Get resource not found error (with a description) because wrong endpoint for standard client
    credential = AzureKeyCredential(EVENTGRID_KEY_GA_CLOUDEVENT)
    client = EventGridClient(EVENTGRID_ENDPOINT_GA_CLOUDEVENT, credential=credential, level=ClientLevel.STANDARD)
    client.send(cloud_event_dict, topic_name=TOPIC_NAME)
except Exception as e:
    print(f"Standard Client Created with wrong endpoint: {e} \n \n")

try:
    # Create a Standard Client but pass an eventgrid event
    credential = AzureKeyCredential(EVENTGRID_KEY)
    client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential, level=ClientLevel.STANDARD)
    client.send(eventgrid_event, topic_name=TOPIC_NAME)
except Exception as e:
    print(" Get from service: Standard Client Created with EventGridEvent: (BadRequest) Cannot deserialize input event"
        "Code: BadRequest "
        "Message: Cannot deserialize input event \n ")
    print(f"Standard Client Created with EventGridEvent: {e} \n \n")

try:
    # Create a Standard Client but pass an eventgrid event dict
    credential = AzureKeyCredential(EVENTGRID_KEY)
    client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential, level=ClientLevel.STANDARD)
    client.send(eventgrid_event_dict, topic_name=TOPIC_NAME)
except Exception as e:
    print("Get from service: Standard Client Created with EventGrid Event Dict:"
        "(BadRequest) CloudEvents attribute names MUST consist of lower-case letters ('a' to 'z') or digits ('0' to '9') from the ASCII character set."
        "Code: BadRequest "
        "Message: CloudEvents attribute names MUST consist of lower-case letters ('a' to 'z') or digits ('0' to '9') from the ASCII character set. \n ")
    print(f"Standard Client Created with EventGrid Event Dict: {e} \n \n")

try:
    # Send a broken eventgrid event to Basic Client
    credential = AzureKeyCredential(EVENTGRID_KEY_GA_EVENTGRIDEVENT)
    client = EventGridClient(EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT, credential=credential, level=ClientLevel.BASIC)
    client.send(broken_eventgrid_event)
except Exception as e:
    print(f"Basic Client Sent Broken EventGrid Event: {e} \n \n")

try:
    # Send a broken cloud event to Basic Client
    credential = AzureKeyCredential(EVENTGRID_KEY_GA_CLOUDEVENT)
    client = EventGridClient(EVENTGRID_ENDPOINT_GA_CLOUDEVENT, credential=credential, level=ClientLevel.BASIC)
    client.send(broken_cloud_event)
except Exception as e:
    print(f"Basic Client Sent Broken Cloud Event: {e} \n \n")

try:
    # Send a broken cloud event to Standard Client
    credential = AzureKeyCredential(EVENTGRID_KEY)
    client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential, level=ClientLevel.STANDARD)
    client.send(broken_cloud_event, topic_name=TOPIC_NAME)
except Exception as e:
    print(f"Standard Client Sent Broken Cloud Event: {e} \n \n")

try:
    # Send a broken eventgrid event to Standard Client
    credential = AzureKeyCredential(EVENTGRID_KEY)
    client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential, level=ClientLevel.STANDARD)
    client.send(broken_eventgrid_event, topic_name=TOPIC_NAME)
except Exception as e:
    print(f"Standard Client Sent Broken EventGrid Event: {e} \n \n")


try:
    # Send a broken eventgrid event to Basic Client
    credential = AzureKeyCredential(EVENTGRID_KEY_GA_EVENTGRIDEVENT)
    client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT, credential=credential,)
    client.send(broken_eventgrid_event)
except Exception as e:
    print(f"Publisher Client Sent Broken EventGrid Event: {e} \n \n")

try:
    # Send a broken cloud event to Basic Client
    credential = AzureKeyCredential(EVENTGRID_KEY_GA_CLOUDEVENT)
    client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA_CLOUDEVENT, credential=credential)
    client.send(broken_cloud_event)
except Exception as e:
    print(f"Publisher Client Sent Broken Cloud Event: {e} \n \n")
