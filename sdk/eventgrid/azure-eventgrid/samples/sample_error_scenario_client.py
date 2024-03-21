import os
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridClient, EventGridEvent, ClientLevel


# Cloud Event Topic
EVENTGRID_KEY_GA_CLOUDEVENT: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_KEY"]
EVENTGRID_ENDPOINT_GA_CLOUDEVENT: str = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT"]

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
cloud_event = CloudEvent(type="Contoso.Items.ItemReceived", source="/contoso/items", data={"itemSku": "Contoso Item SKU #1"}, subject="Door1", specversion="1.0", id="randomclouduuid11")
cloud_event_dict = {"type": "Contoso.Items.ItemReceived", "source": "/contoso/items", "data": {"itemSku": "Contoso Item SKU #1"}, "subject": "Door1", "specversion": "1.0", "id": "randomclouduuid11"}
list_cloud_event = [cloud_event, cloud_event]
list_cloud_event_dict = [cloud_event_dict, cloud_event_dict]
eventgrid_event = EventGridEvent(event_type="Contoso.Items.ItemReceived", data={"itemSku": "Contoso Item SKU #1"}, subject="Door1", data_version="2.0", id="randomeventgriduuid11")
eventgrid_event_dict = {"eventType": "Contoso.Items.ItemReceived", "data": {"itemSku": "Contoso Item SKU #1"}, "subject": "Door1", "dataVersion": "2.0", "id": "randomeventgriduuid11", "eventTime": "2021-01-20T00:00:00.000000Z"}
list_eventgrid_event = [eventgrid_event, eventgrid_event]
list_eventgrid_event_dict = [eventgrid_event_dict, eventgrid_event_dict]

broken_eventgrid_event = {"data": {"itemSku": "Contoso Item SKU #1"}, "subject": "Door1", "dataVersion": "2.0", "id": "randomeventgriduuid11",}
broken_cloud_event = {"type": "Contoso.Items.ItemReceived", "subject": "Door1", "specversion": "1.0", "id": "randomclouduuid11"}


def send_eventgrid_to_namespace():

    try:
        credential = AzureKeyCredential(EVENTGRID_KEY)
        client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential)
        client.send(eventgrid_event, topic_name=TOPIC_NAME, binary_mode=True)
    except Exception as e:
        print(f"Error occured: {e} \n")

    try:
        credential = AzureKeyCredential(EVENTGRID_KEY)
        client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential)
        client.send(list_eventgrid_event, topic_name=TOPIC_NAME)
    except Exception as e:
        print(f"Error occured: {e} \n")

    try:
        credential = AzureKeyCredential(EVENTGRID_KEY)
        client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential)
        client.send(eventgrid_event_dict, topic_name=TOPIC_NAME)
    except Exception as e:
        print(f"Error occured: {e} \n")

    try:
        credential = AzureKeyCredential(EVENTGRID_KEY)
        client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential)
        client.send(list_eventgrid_event_dict, topic_name=TOPIC_NAME)
    except Exception as e:
        print(f"Error occured: {e} \n")


def send_partner_to_namespace():

    try:
        credential = AzureKeyCredential(EVENTGRID_KEY)
        client = EventGridClient(EVENTGRID_ENDPOINT, credential=credential)
        client.send(cloud_event, topic_name=TOPIC_NAME, channel_name=CHANNEL_NAME)
    except Exception as e:
        print(f"Error occured: {e} \n")


send_eventgrid_to_namespace()
send_partner_to_namespace()
