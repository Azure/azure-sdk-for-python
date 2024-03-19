# --------------------------------------------------------------------------
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridPublisherClient, EventGridEvent


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

# Send EventGrid Event to a CloudEvent Topic
def send_eventgrid_event_to_cloud_event_topic():
    try:
        credential = AzureKeyCredential(EVENTGRID_KEY_GA_CLOUDEVENT)
        client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA_CLOUDEVENT, credential)
        client.send(eventgrid_event)
        print("EventGrid Event sent to Cloud Event Topic")
    except Exception as e:
        print(f"Error Occured: {e}")

# Send Cloud Event to a EventGridEvent Topic
def send_cloud_event_to_eventgrid_event_topic():
    try:
        credential = AzureKeyCredential(EVENTGRID_KEY_GA_EVENTGRIDEVENT)
        client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT, credential)
        client.send(cloud_event)
        print("Cloud Event sent to EventGrid Event Topic")
    except Exception as e:
        print(f"Error Occured: {e}")

# Send a broken EventGrid Event to a EventGrid Topic
def send_broken_eventgrid_event_to_eventgrid_event_topic():
    try:
        credential = AzureKeyCredential(EVENTGRID_KEY_GA_EVENTGRIDEVENT)
        client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA_EVENTGRIDEVENT, credential)
        client.send(broken_eventgrid_event)
        print("Broken EventGrid Event sent to EventGrid Topic")
    except Exception as e:
        print(f"Error Occured: {e}")

# Send a broken Cloud Event to a Cloud Event Topic
def send_broken_cloud_event_to_cloud_event_topic():
    try:
        credential = AzureKeyCredential(EVENTGRID_KEY_GA_CLOUDEVENT)
        client = EventGridPublisherClient(EVENTGRID_ENDPOINT_GA_CLOUDEVENT, credential)
        client.send(broken_cloud_event)
        print("Broken Cloud Event sent to Cloud Event Topic")
    except Exception as e:
        print(f"Error Occured: {e}")

send_eventgrid_event_to_cloud_event_topic()
send_cloud_event_to_eventgrid_event_topic()
send_broken_eventgrid_event_to_eventgrid_event_topic()
send_broken_cloud_event_to_cloud_event_topic()